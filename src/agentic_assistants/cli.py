"""
Command-line interface for Agentic Assistants.

This module provides a Click-based CLI for managing the framework,
including Ollama, MLFlow, and running experiments.

Usage:
    agentic --help
    agentic ollama start
    agentic ollama pull llama3.2
    agentic mlflow start
    agentic run examples/crewai_research_team.py
    agentic config show
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentic_assistants import __version__
from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager, OllamaError
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.utils.logging import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)


def print_banner():
    """Print the application banner."""
    banner = f"""
[bold blue]╔═══════════════════════════════════════════════════════════╗
║           🤖 Agentic Assistants Framework v{__version__}           ║
║     Multi-Agent Experimentation & MLOps Platform          ║
╚═══════════════════════════════════════════════════════════╝[/bold blue]
"""
    console.print(banner)


@click.group()
@click.version_option(version=__version__, prog_name="agentic")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.pass_context
def cli(ctx, verbose: bool, quiet: bool):
    """
    Agentic Assistants - Multi-Agent Experimentation Framework.
    
    A local platform for experimenting with multi-agent frameworks like
    CrewAI and LangGraph, with integrated MLOps tooling.
    
    \b
    Examples:
        agentic ollama start        Start Ollama server
        agentic ollama pull llama3.2    Pull a model
        agentic mlflow start        Start MLFlow tracking server
        agentic run experiment.py   Run an experiment with tracking
        agentic config show         Show current configuration
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    # Configure logging
    log_level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    setup_logging(level=log_level)


# =============================================================================
# OLLAMA COMMANDS
# =============================================================================


@cli.group()
@click.pass_context
def ollama(ctx):
    """Manage Ollama server and models."""
    ctx.obj["ollama"] = OllamaManager(AgenticConfig())


@ollama.command("start")
@click.option("--wait/--no-wait", default=True, help="Wait for server to be ready")
@click.option("--timeout", default=30, help="Timeout in seconds when waiting")
@click.pass_context
def ollama_start(ctx, wait: bool, timeout: int):
    """Start the Ollama server."""
    manager: OllamaManager = ctx.obj["ollama"]

    try:
        if manager.is_running():
            console.print("[green]✓[/green] Ollama is already running")
            return

        console.print("[yellow]Starting Ollama server...[/yellow]")
        manager.start(wait=wait, timeout=timeout)
        console.print("[green]✓[/green] Ollama server started successfully")

    except OllamaError as e:
        console.print(f"[red]✗[/red] Failed to start Ollama: {e}")
        raise SystemExit(1)


@ollama.command("stop")
@click.pass_context
def ollama_stop(ctx):
    """Stop the Ollama server (if started by this tool)."""
    manager: OllamaManager = ctx.obj["ollama"]

    if manager.stop():
        console.print("[green]✓[/green] Ollama server stopped")
    else:
        console.print("[yellow]![/yellow] No managed Ollama process to stop")
        console.print("  If Ollama is running externally, stop it manually")


@ollama.command("status")
@click.pass_context
def ollama_status(ctx):
    """Show Ollama server status."""
    manager: OllamaManager = ctx.obj["ollama"]
    status = manager.get_status()

    table = Table(title="Ollama Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Running", "✓ Yes" if status["running"] else "✗ No")
    table.add_row("Host", status["host"])
    table.add_row("Managed Process", "Yes" if status["managed_process"] else "No")

    if status["running"]:
        table.add_row("Models", str(status.get("model_count", 0)))
        for model in status.get("models", []):
            table.add_row("  └─", model)

    console.print(table)


@ollama.command("list")
@click.pass_context
def ollama_list(ctx):
    """List available models."""
    manager: OllamaManager = ctx.obj["ollama"]

    if not manager.is_running():
        console.print("[red]✗[/red] Ollama is not running. Start it with: agentic ollama start")
        raise SystemExit(1)

    try:
        models = manager.list_models()

        if not models:
            console.print("[yellow]No models found.[/yellow]")
            console.print("Pull a model with: agentic ollama pull llama3.2")
            return

        table = Table(title="Available Models")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Modified", style="dim")

        for model in models:
            table.add_row(
                model.name,
                f"{model.size_gb:.1f} GB",
                model.modified_at[:19] if model.modified_at else "-",
            )

        console.print(table)

    except OllamaError as e:
        console.print(f"[red]✗[/red] Error listing models: {e}")
        raise SystemExit(1)


@ollama.command("pull")
@click.argument("model")
@click.pass_context
def ollama_pull(ctx, model: str):
    """Pull a model from the Ollama registry."""
    manager: OllamaManager = ctx.obj["ollama"]

    if not manager.is_running():
        console.print("[yellow]Ollama is not running, starting...[/yellow]")
        try:
            manager.start()
        except OllamaError as e:
            console.print(f"[red]✗[/red] Failed to start Ollama: {e}")
            raise SystemExit(1)

    console.print(f"[yellow]Pulling model: {model}[/yellow]")

    def progress_callback(data):
        if "status" in data:
            status = data["status"]
            if "completed" in data and "total" in data:
                pct = (data["completed"] / data["total"]) * 100 if data["total"] > 0 else 0
                console.print(f"  {status}: {pct:.1f}%", end="\r")
            else:
                console.print(f"  {status}")

    try:
        manager.pull_model(model, callback=progress_callback)
        console.print(f"\n[green]✓[/green] Successfully pulled: {model}")
    except OllamaError as e:
        console.print(f"\n[red]✗[/red] Failed to pull model: {e}")
        raise SystemExit(1)


@ollama.command("delete")
@click.argument("model")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def ollama_delete(ctx, model: str, yes: bool):
    """Delete a model from local storage."""
    manager: OllamaManager = ctx.obj["ollama"]

    if not yes:
        if not click.confirm(f"Delete model '{model}'?"):
            console.print("Cancelled")
            return

    if manager.delete_model(model):
        console.print(f"[green]✓[/green] Deleted: {model}")
    else:
        console.print(f"[red]✗[/red] Failed to delete: {model}")
        raise SystemExit(1)


# =============================================================================
# MLFLOW COMMANDS
# =============================================================================


@cli.group()
def mlflow():
    """Manage MLFlow tracking server."""
    pass


@mlflow.command("start")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=5000, help="Port to bind to")
@click.option("--backend-store", default="./mlruns", help="Backend store URI")
def mlflow_start(host: str, port: int, backend_store: str):
    """Start the MLFlow tracking server."""
    console.print(f"[yellow]Starting MLFlow server on {host}:{port}...[/yellow]")

    try:
        from agentic_assistants.core.mlflow_tracker import start_mlflow_server

        process = start_mlflow_server(
            host=host,
            port=port,
            backend_store_uri=backend_store,
        )
        console.print(f"[green]✓[/green] MLFlow server started (PID: {process.pid})")
        console.print(f"  UI available at: http://{host}:{port}")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to start MLFlow: {e}")
        raise SystemExit(1)


@mlflow.command("ui")
@click.option("--port", default=5000, help="Port where MLFlow is running")
def mlflow_ui(port: int):
    """Open MLFlow UI in browser."""
    import webbrowser

    url = f"http://localhost:{port}"
    console.print(f"Opening MLFlow UI: {url}")
    webbrowser.open(url)


@mlflow.command("status")
@click.option("--port", default=5000, help="Port to check")
def mlflow_status(port: int):
    """Check MLFlow server status."""
    import httpx

    try:
        response = httpx.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            console.print(f"[green]✓[/green] MLFlow is running on port {port}")
        else:
            console.print(f"[yellow]![/yellow] MLFlow returned status {response.status_code}")
    except httpx.RequestError:
        console.print(f"[red]✗[/red] MLFlow is not running on port {port}")


# =============================================================================
# RUN COMMANDS
# =============================================================================


@cli.command("run")
@click.argument("script", type=click.Path(exists=True))
@click.option("--experiment-name", "-e", help="MLFlow experiment name")
@click.option("--run-name", "-r", help="Run name")
@click.option("--no-tracking", is_flag=True, help="Disable MLFlow tracking")
@click.option("--model", "-m", help="Override default model")
def run_experiment(
    script: str,
    experiment_name: Optional[str],
    run_name: Optional[str],
    no_tracking: bool,
    model: Optional[str],
):
    """
    Run an experiment script with tracking.
    
    The script should be a Python file that uses the agentic_assistants
    framework. MLFlow tracking is enabled by default.
    
    \b
    Examples:
        agentic run examples/crewai_research_team.py
        agentic run my_script.py --experiment-name "my-exp" --model llama3.2
        agentic run my_script.py --no-tracking
    """
    print_banner()

    # Set environment variables for the script
    env = os.environ.copy()
    if no_tracking:
        env["AGENTIC_MLFLOW_ENABLED"] = "false"
    if experiment_name:
        env["MLFLOW_EXPERIMENT_NAME"] = experiment_name
    if model:
        env["OLLAMA_DEFAULT_MODEL"] = model

    console.print(f"[cyan]Running experiment:[/cyan] {script}")
    if experiment_name:
        console.print(f"  Experiment: {experiment_name}")
    if run_name:
        console.print(f"  Run name: {run_name}")
    console.print()

    try:
        result = subprocess.run(
            [sys.executable, script],
            env=env,
            check=True,
        )
        console.print("\n[green]✓[/green] Experiment completed successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗[/red] Experiment failed with exit code {e.returncode}")
        raise SystemExit(e.returncode)


# =============================================================================
# CONFIG COMMANDS
# =============================================================================


@cli.group()
def config():
    """View and manage configuration."""
    pass


@config.command("show")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def config_show(as_json: bool):
    """Show current configuration."""
    cfg = AgenticConfig()

    if as_json:
        import json

        console.print(json.dumps(cfg.to_dict(), indent=2))
        return

    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("MLFlow Enabled", str(cfg.mlflow_enabled))
    table.add_row("Telemetry Enabled", str(cfg.telemetry_enabled))
    table.add_row("Log Level", cfg.log_level)
    table.add_row("Data Directory", str(cfg.data_dir))
    table.add_row("", "")
    table.add_row("[bold]Ollama[/bold]", "")
    table.add_row("  Host", cfg.ollama.host)
    table.add_row("  Default Model", cfg.ollama.default_model)
    table.add_row("  Timeout", f"{cfg.ollama.timeout}s")
    table.add_row("", "")
    table.add_row("[bold]MLFlow[/bold]", "")
    table.add_row("  Tracking URI", cfg.mlflow.tracking_uri)
    table.add_row("  Experiment", cfg.mlflow.experiment_name)
    table.add_row("", "")
    table.add_row("[bold]Telemetry[/bold]", "")
    table.add_row("  OTLP Endpoint", cfg.telemetry.exporter_otlp_endpoint)
    table.add_row("  Service Name", cfg.telemetry.service_name)

    console.print(table)


@config.command("init")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing .env file")
def config_init(force: bool):
    """Initialize configuration by creating .env file."""
    env_file = Path(".env")
    example_file = Path("env.example")

    if env_file.exists() and not force:
        console.print("[yellow]![/yellow] .env file already exists. Use --force to overwrite.")
        return

    if example_file.exists():
        env_file.write_text(example_file.read_text())
        console.print("[green]✓[/green] Created .env file from env.example")
    else:
        # Create basic .env
        content = """# Agentic Assistants Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
AGENTIC_MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://localhost:5000
AGENTIC_LOG_LEVEL=INFO
"""
        env_file.write_text(content)
        console.print("[green]✓[/green] Created .env file with default settings")

    console.print("  Edit the file to customize your configuration")


# =============================================================================
# SERVICES COMMANDS
# =============================================================================


@cli.group()
def services():
    """Manage all services (Ollama, MLFlow, etc.)."""
    pass


@services.command("start")
@click.option("--ollama/--no-ollama", default=True, help="Start Ollama")
@click.option("--mlflow/--no-mlflow", default=True, help="Start MLFlow")
@click.option("--docker", is_flag=True, help="Use Docker Compose for services")
def services_start(ollama: bool, mlflow: bool, docker: bool):
    """Start all required services."""
    print_banner()

    if docker:
        console.print("[yellow]Starting services via Docker Compose...[/yellow]")
        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                check=True,
            )
            console.print("[green]✓[/green] Docker services started")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Failed to start Docker services: {e}")
            raise SystemExit(1)
        except FileNotFoundError:
            console.print("[red]✗[/red] docker-compose not found. Install Docker first.")
            raise SystemExit(1)
        return

    if ollama:
        console.print("[yellow]Starting Ollama...[/yellow]")
        manager = OllamaManager(AgenticConfig())
        try:
            if manager.is_running():
                console.print("  [green]✓[/green] Already running")
            else:
                manager.start()
                console.print("  [green]✓[/green] Started")
        except OllamaError as e:
            console.print(f"  [red]✗[/red] Failed: {e}")

    if mlflow:
        console.print("[yellow]Starting MLFlow...[/yellow]")
        try:
            from agentic_assistants.core.mlflow_tracker import start_mlflow_server

            process = start_mlflow_server()
            console.print(f"  [green]✓[/green] Started (PID: {process.pid})")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed: {e}")


@services.command("status")
def services_status():
    """Show status of all services."""
    table = Table(title="Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    # Check Ollama
    manager = OllamaManager(AgenticConfig())
    if manager.is_running():
        models = manager.list_models()
        table.add_row("Ollama", "[green]✓ Running[/green]", f"{len(models)} models")
    else:
        table.add_row("Ollama", "[red]✗ Stopped[/red]", "")

    # Check MLFlow
    import httpx

    try:
        response = httpx.get("http://localhost:5000/health", timeout=2)
        table.add_row("MLFlow", "[green]✓ Running[/green]", "http://localhost:5000")
    except httpx.RequestError:
        table.add_row("MLFlow", "[red]✗ Stopped[/red]", "")

    # Check Jaeger (if using Docker)
    try:
        response = httpx.get("http://localhost:16686", timeout=2)
        table.add_row("Jaeger", "[green]✓ Running[/green]", "http://localhost:16686")
    except httpx.RequestError:
        table.add_row("Jaeger", "[dim]Not running[/dim]", "Optional (Docker)")

    console.print(table)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()

