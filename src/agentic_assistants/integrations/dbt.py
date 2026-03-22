"""
dbt-core integration for data transformation and model management.

Provides a programmatic interface to dbt operations (run, test, compile)
and metadata extraction from manifest.json / catalog.json.
"""

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DbtClient:
    """
    Wrapper around dbt-core CLI for running models and extracting metadata.

    Operates on a dbt project directory and a profiles directory that
    contains connection credentials.
    """

    def __init__(
        self,
        project_dir: str = "",
        profiles_dir: str = "",
        target: str = "dev",
    ):
        self.project_dir = Path(project_dir) if project_dir else None
        self.profiles_dir = Path(profiles_dir) if profiles_dir else None
        self.target = target
        self._runs: Dict[str, Dict[str, Any]] = {}

    def _base_cmd(self) -> List[str]:
        cmd = ["dbt"]
        if self.project_dir:
            cmd += ["--project-dir", str(self.project_dir)]
        if self.profiles_dir:
            cmd += ["--profiles-dir", str(self.profiles_dir)]
        return cmd

    def _exec(self, args: List[str], timeout: int = 300) -> Dict[str, Any]:
        cmd = self._base_cmd() + args
        logger.info("Running dbt command: %s", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_dir) if self.project_dir else None,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except FileNotFoundError:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "dbt CLI not found. Install with: pip install dbt-core dbt-postgres",
                "success": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -2,
                "stdout": "",
                "stderr": f"dbt command timed out after {timeout}s",
                "success": False,
            }

    # -- Core operations -------------------------------------------------------

    def run(
        self,
        select: Optional[str] = None,
        exclude: Optional[str] = None,
        full_refresh: bool = False,
    ) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())[:8]
        args = ["run", "--target", self.target]
        if select:
            args += ["--select", select]
        if exclude:
            args += ["--exclude", exclude]
        if full_refresh:
            args.append("--full-refresh")

        result = self._exec(args)
        self._runs[run_id] = {
            **result,
            "run_id": run_id,
            "command": "run",
            "select": select,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return self._runs[run_id]

    def test(self, select: Optional[str] = None) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())[:8]
        args = ["test", "--target", self.target]
        if select:
            args += ["--select", select]

        result = self._exec(args)
        self._runs[run_id] = {
            **result,
            "run_id": run_id,
            "command": "test",
            "select": select,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return self._runs[run_id]

    def compile(self) -> Dict[str, Any]:
        return self._exec(["compile", "--target", self.target])

    def generate_docs(self) -> Dict[str, Any]:
        return self._exec(["docs", "generate", "--target", self.target])

    # -- Metadata extraction ---------------------------------------------------

    def _target_dir(self) -> Path:
        if self.project_dir:
            return self.project_dir / "target"
        return Path("target")

    def get_manifest(self) -> Dict[str, Any]:
        manifest_path = self._target_dir() / "manifest.json"
        if not manifest_path.exists():
            return {"error": "manifest.json not found; run 'dbt compile' first"}
        return json.loads(manifest_path.read_text())

    def get_catalog(self) -> Dict[str, Any]:
        catalog_path = self._target_dir() / "catalog.json"
        if not catalog_path.exists():
            return {"error": "catalog.json not found; run 'dbt docs generate' first"}
        return json.loads(catalog_path.read_text())

    def get_run_results(self) -> Dict[str, Any]:
        rr_path = self._target_dir() / "run_results.json"
        if not rr_path.exists():
            return {"error": "run_results.json not found; run 'dbt run' first"}
        return json.loads(rr_path.read_text())

    # -- Model introspection ---------------------------------------------------

    def list_models(self) -> List[Dict[str, Any]]:
        manifest = self.get_manifest()
        if "error" in manifest:
            return []

        models = []
        for key, node in manifest.get("nodes", {}).items():
            if node.get("resource_type") != "model":
                continue
            models.append({
                "unique_id": node["unique_id"],
                "name": node["name"],
                "schema": node.get("schema", ""),
                "database": node.get("database", ""),
                "materialized": node.get("config", {}).get("materialized", "view"),
                "description": node.get("description", ""),
                "depends_on": node.get("depends_on", {}).get("nodes", []),
                "tags": node.get("tags", []),
                "path": node.get("path", ""),
            })
        return models

    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        manifest = self.get_manifest()
        if "error" in manifest:
            return None

        for node in manifest.get("nodes", {}).values():
            if node.get("resource_type") == "model" and node.get("name") == name:
                return {
                    "unique_id": node["unique_id"],
                    "name": node["name"],
                    "schema": node.get("schema", ""),
                    "database": node.get("database", ""),
                    "materialized": node.get("config", {}).get("materialized", "view"),
                    "description": node.get("description", ""),
                    "depends_on": node.get("depends_on", {}).get("nodes", []),
                    "tags": node.get("tags", []),
                    "path": node.get("path", ""),
                    "raw_sql": node.get("raw_sql", node.get("raw_code", "")),
                    "compiled_sql": node.get("compiled_sql", node.get("compiled_code", "")),
                    "columns": node.get("columns", {}),
                }
        return None

    def get_lineage(self) -> Dict[str, Any]:
        """Return the full model dependency graph for DAG visualization."""
        manifest = self.get_manifest()
        if "error" in manifest:
            return {"nodes": [], "edges": []}

        nodes = []
        edges = []
        for node in manifest.get("nodes", {}).values():
            if node.get("resource_type") not in ("model", "source", "seed"):
                continue
            nodes.append({
                "id": node["unique_id"],
                "name": node["name"],
                "type": node["resource_type"],
                "materialized": node.get("config", {}).get("materialized", ""),
            })
            for dep in node.get("depends_on", {}).get("nodes", []):
                edges.append({"source": dep, "target": node["unique_id"]})

        return {"nodes": nodes, "edges": edges}

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get(run_id)


def get_dbt_client(config=None) -> DbtClient:
    """Factory that builds a DbtClient from AgenticConfig."""
    if config is None:
        from agentic_assistants.config import AgenticConfig
        config = AgenticConfig()

    dbt_cfg = getattr(config, "dbt", None)
    if dbt_cfg is not None:
        return DbtClient(
            project_dir=dbt_cfg.project_dir,
            profiles_dir=dbt_cfg.profiles_dir,
            target=dbt_cfg.target,
        )
    return DbtClient()
