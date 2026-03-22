"""
Managed Jupyter notebook server with full lifecycle management.

Starts a ``jupyter notebook`` subprocess under the FastAPI backend process,
registers an IPython kernel that shares the framework's virtualenv, and
emits OpenTelemetry traces / metrics plus structured logs for every
lifecycle event.

When ``JupyterSettings.external_url`` is set the local process is skipped
and all URL helpers point to the remote JupyterHub deployment instead.
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

_manager: Optional["JupyterManager"] = None


def get_jupyter_manager(config: Optional[AgenticConfig] = None) -> "JupyterManager":
    """Return (and optionally create) the global JupyterManager singleton."""
    global _manager
    if _manager is None:
        _manager = JupyterManager(config or AgenticConfig())
    return _manager


class JupyterManager:
    """Manages the lifecycle of a Jupyter notebook server subprocess.

    Responsibilities:
    - Register an IPython kernel that uses the current virtualenv
    - Start / stop / restart the ``jupyter notebook`` process
    - Poll the notebook REST API until the server is healthy
    - Pipe subprocess stdout/stderr through the structured logger
    - Emit OpenTelemetry spans and metrics for every lifecycle event
    """

    def __init__(self, config: AgenticConfig) -> None:
        self._config = config
        self._process: Optional[subprocess.Popen] = None
        self._started_at: Optional[float] = None
        self._log_task: Optional[asyncio.Task] = None
        self._pid_file = Path(".jupyter.pid")

        self._telemetry = self._init_telemetry()
        self._starts_counter = None
        self._health_histogram = None
        self._setup_metrics()

    # ------------------------------------------------------------------
    # Telemetry helpers
    # ------------------------------------------------------------------

    def _init_telemetry(self):
        try:
            from agentic_assistants.core.telemetry import TelemetryManager
            tm = TelemetryManager(self._config)
            if self._config.telemetry_enabled:
                tm.initialize()
            return tm
        except Exception:
            return None

    def _setup_metrics(self) -> None:
        if self._telemetry is None:
            return
        try:
            meter = self._telemetry.get_meter("jupyter")
            self._starts_counter = meter.create_counter(
                "jupyter.starts_total",
                description="Total number of managed Jupyter server starts",
            )
            self._health_histogram = meter.create_histogram(
                "jupyter.health_check_duration_ms",
                description="Latency of Jupyter health-check polls in ms",
                unit="ms",
            )
        except Exception:
            pass

    def _span(self, name: str, attributes: Optional[dict] = None):
        if self._telemetry:
            return self._telemetry.span(name, attributes)
        from contextlib import nullcontext
        return nullcontext()

    def _record_start(self) -> None:
        if self._starts_counter:
            try:
                self._starts_counter.add(1)
            except Exception:
                pass

    def _record_health_ms(self, ms: float) -> None:
        if self._health_histogram:
            try:
                self._health_histogram.record(ms)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    @property
    def mode(self) -> str:
        return "external" if self._config.jupyter.external_url else "managed"

    def get_url(self) -> str:
        cfg = self._config.jupyter
        if cfg.external_url:
            return cfg.external_url
        scheme = "http"
        host = "localhost" if cfg.host in ("0.0.0.0", "127.0.0.1") else cfg.host
        base = cfg.base_url.rstrip("/")
        return f"{scheme}://{host}:{cfg.port}{base}"

    async def start(self) -> bool:
        """Start the managed notebook server.

        Returns ``True`` if the server is healthy after startup.
        """
        cfg = self._config.jupyter

        if cfg.external_url:
            logger.info("Jupyter configured for external JupyterHub at %s", cfg.external_url)
            return True

        if self.is_running:
            logger.info("Jupyter notebook server already running (PID %s)", self._process.pid)
            return True

        with self._span("jupyter.start", {"jupyter.port": cfg.port}):
            t0 = time.time()

            nb_dir = Path(cfg.notebook_dir)
            nb_dir.mkdir(parents=True, exist_ok=True)

            self._install_kernel()

            cmd = [
                sys.executable, "-m", "notebook",
                "--ip", cfg.host,
                "--port", str(cfg.port),
                "--no-browser",
                f"--NotebookApp.token={cfg.token}",
                f"--NotebookApp.notebook_dir={nb_dir.resolve()}",
            ]
            if cfg.base_url and cfg.base_url != "/":
                cmd.append(f"--NotebookApp.base_url={cfg.base_url}")

            logger.info("Starting Jupyter notebook: %s", " ".join(cmd))

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            self._started_at = time.time()

            if self._pid_file:
                self._pid_file.write_text(str(self._process.pid))

            if cfg.log_to_stdout:
                self._log_task = asyncio.create_task(self._pipe_logs())

            healthy = await self._wait_healthy(cfg.startup_timeout)
            elapsed_ms = (time.time() - t0) * 1000

            self._record_start()

            if healthy:
                logger.info(
                    "Jupyter notebook server ready on %s (PID %s, %.0fms)",
                    self.get_url(), self._process.pid, elapsed_ms,
                )
            else:
                logger.warning(
                    "Jupyter notebook server started but health-check timed out after %ds",
                    cfg.startup_timeout,
                )

            return healthy

    async def stop(self) -> None:
        """Gracefully stop the managed notebook server."""
        if not self.is_running:
            return

        pid = self._process.pid
        with self._span("jupyter.stop", {"jupyter.pid": pid}):
            logger.info("Stopping Jupyter notebook server (PID %s)", pid)

            if sys.platform == "win32":
                self._process.terminate()
            else:
                os.kill(pid, signal.SIGTERM)

            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Jupyter did not exit in 5s, sending SIGKILL")
                self._process.kill()
                self._process.wait(timeout=3)

            if self._log_task and not self._log_task.done():
                self._log_task.cancel()

            if self._pid_file.exists():
                self._pid_file.unlink(missing_ok=True)

            self._process = None
            self._started_at = None
            logger.info("Jupyter notebook server stopped")

    async def restart(self) -> bool:
        """Restart the managed server."""
        with self._span("jupyter.restart"):
            await self.stop()
            return await self.start()

    async def health_check(self) -> dict:
        """Probe the notebook server health endpoint."""
        cfg = self._config.jupyter
        if cfg.external_url:
            return {"running": True, "mode": "external", "url": cfg.external_url}

        if not self.is_running:
            return {"running": False, "mode": "managed", "url": self.get_url()}

        url = f"http://{cfg.host}:{cfg.port}/api/status"
        t0 = time.time()
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
                ok = resp.status_code == 200
        except Exception:
            ok = False

        elapsed_ms = (time.time() - t0) * 1000
        self._record_health_ms(elapsed_ms)

        uptime = time.time() - self._started_at if self._started_at else 0

        return {
            "running": ok,
            "mode": "managed",
            "pid": self._process.pid if self._process else None,
            "port": cfg.port,
            "url": self.get_url(),
            "uptime_seconds": round(uptime, 1),
            "health_check_ms": round(elapsed_ms, 1),
        }

    def status(self) -> dict:
        """Return synchronous status snapshot (no health probe)."""
        cfg = self._config.jupyter
        if cfg.external_url:
            return {"running": True, "mode": "external", "url": cfg.external_url}

        uptime = time.time() - self._started_at if self._started_at else 0
        return {
            "running": self.is_running,
            "mode": "managed",
            "pid": self._process.pid if self._process else None,
            "port": cfg.port,
            "url": self.get_url(),
            "uptime_seconds": round(uptime, 1),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _install_kernel(self) -> None:
        """Register an IPython kernel that uses the current virtualenv."""
        cfg = self._config.jupyter
        try:
            subprocess.run(
                [
                    sys.executable, "-m", "ipykernel", "install",
                    "--user",
                    "--name", cfg.kernel_name,
                    "--display-name", "Agentic Assistants",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("Registered IPython kernel '%s'", cfg.kernel_name)
        except subprocess.CalledProcessError as exc:
            logger.warning("Kernel registration failed: %s", exc.stderr or exc)
        except FileNotFoundError:
            logger.warning("ipykernel not found; kernel registration skipped")

    async def _wait_healthy(self, timeout: int) -> bool:
        """Poll the notebook API until it responds or the timeout expires."""
        cfg = self._config.jupyter
        url = f"http://{cfg.host}:{cfg.port}/api/status"
        deadline = time.time() + timeout

        while time.time() < deadline:
            if not self.is_running:
                return False
            try:
                import httpx
                async with httpx.AsyncClient(timeout=2) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        return True
            except Exception:
                pass
            await asyncio.sleep(0.5)

        return False

    async def _pipe_logs(self) -> None:
        """Read subprocess stdout line-by-line and emit structured logs."""
        if self._process is None or self._process.stdout is None:
            return

        loop = asyncio.get_event_loop()
        try:
            while self.is_running:
                line = await loop.run_in_executor(None, self._process.stdout.readline)
                if not line:
                    break
                line = line.rstrip("\n\r")
                if line:
                    logger.info("[jupyter] %s", line)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
