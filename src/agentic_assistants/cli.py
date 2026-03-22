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
# SESSION COMMANDS
# =============================================================================


@cli.group()
def session():
    """Manage sessions for data persistence."""
    pass


@session.command("list")
def session_list():
    """List all sessions."""
    from agentic_assistants.core.session import SessionManager
    
    manager = SessionManager(AgenticConfig())
    sessions = manager.list_sessions()
    
    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        console.print("Create one with: agentic session create <name>")
        return
    
    table = Table(title="Sessions")
    table.add_column("Name", style="cyan")
    table.add_column("Created", style="dim")
    table.add_column("Updated", style="dim")
    
    for s in sessions:
        table.add_row(s["name"], s["created_at"][:19], s["updated_at"][:19])
    
    console.print(table)


@session.command("create")
@click.argument("name")
def session_create(name: str):
    """Create a new session."""
    from agentic_assistants.core.session import SessionManager
    
    manager = SessionManager(AgenticConfig())
    try:
        session = manager.create_session(name)
        console.print(f"[green]✓[/green] Created session: {name}")
        console.print(f"  ID: {session.id}")
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1)


@session.command("delete")
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def session_delete(name: str, yes: bool):
    """Delete a session and all its data."""
    from agentic_assistants.core.session import SessionManager
    
    if not yes:
        if not click.confirm(f"Delete session '{name}' and all its data?"):
            console.print("Cancelled")
            return
    
    manager = SessionManager(AgenticConfig())
    if manager.delete_session(name):
        console.print(f"[green]✓[/green] Deleted session: {name}")
    else:
        console.print(f"[red]✗[/red] Session not found: {name}")
        raise SystemExit(1)


@session.command("info")
@click.argument("name")
def session_info(name: str):
    """Show session details."""
    from agentic_assistants.core.session import SessionManager
    
    manager = SessionManager(AgenticConfig())
    s = manager.get_session(name)
    
    if not s:
        console.print(f"[red]✗[/red] Session not found: {name}")
        raise SystemExit(1)
    
    table = Table(title=f"Session: {name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    
    table.add_row("ID", s.id)
    table.add_row("Name", s.name)
    table.add_row("Created", s.created_at.isoformat())
    
    contexts = s.list_contexts()
    table.add_row("Contexts", str(len(contexts)))
    
    history = s.get_chat_history(limit=5)
    table.add_row("Chat History", f"{len(history)} recent")
    
    console.print(table)


# =============================================================================
# INDEX COMMANDS
# =============================================================================


@cli.command("index")
@click.argument("path", type=click.Path(exists=True))
@click.option("--collection", "-c", default="default", help="Collection name")
@click.option("--patterns", "-p", multiple=True, help="File patterns (e.g., *.py)")
@click.option("--force", "-f", is_flag=True, help="Force re-indexing")
@click.option("--no-recursive", is_flag=True, help="Don't recurse into subdirectories")
def index_path(
    path: str,
    collection: str,
    patterns: tuple,
    force: bool,
    no_recursive: bool,
):
    """
    Index a file or directory into the vector database.
    
    \b
    Examples:
        agentic index ./src --collection my-project
        agentic index ./docs -p "*.md" -p "*.rst"
        agentic index ./src --force
    """
    from agentic_assistants.indexing.codebase import CodebaseIndexer
    from agentic_assistants.vectordb.base import VectorStore
    
    config = AgenticConfig()
    
    console.print(f"[cyan]Indexing:[/cyan] {path}")
    console.print(f"  Collection: {collection}")
    if patterns:
        console.print(f"  Patterns: {', '.join(patterns)}")
    
    try:
        store = VectorStore.create(config=config)
        indexer = CodebaseIndexer(vector_store=store, config=config)
        
        path_obj = Path(path)
        pattern_list = list(patterns) if patterns else None
        
        def progress_callback(current, total, file_path):
            pct = int((current / total) * 100)
            console.print(f"  [{pct:3d}%] {str(file_path)[-50:]}", end="\r")
        
        if path_obj.is_file():
            stats = indexer.index_file(
                path=path_obj,
                collection=collection,
                force=force,
            )
        else:
            stats = indexer.index_directory(
                directory=path_obj,
                collection=collection,
                patterns=pattern_list,
                recursive=not no_recursive,
                force=force,
                progress_callback=progress_callback,
            )
        
        console.print()  # Clear progress line
        console.print(f"[green]✓[/green] Indexing complete")
        console.print(f"  Files processed: {stats.files_processed}")
        console.print(f"  Files skipped: {stats.files_skipped}")
        console.print(f"  Chunks indexed: {stats.chunks_indexed}")
        console.print(f"  Duration: {stats.duration_seconds:.2f}s")
        
        if stats.errors:
            console.print(f"[yellow]  Errors: {len(stats.errors)}[/yellow]")
            for err in stats.errors[:5]:
                console.print(f"    - {err}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Indexing failed: {e}")
        raise SystemExit(1)


# =============================================================================
# SEARCH COMMANDS
# =============================================================================


@cli.command("search")
@click.argument("query")
@click.option("--collection", "-c", default="default", help="Collection to search")
@click.option("--top-k", "-k", default=5, help="Number of results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def search_query(query: str, collection: str, top_k: int, as_json: bool):
    """
    Search the vector database.
    
    \b
    Examples:
        agentic search "authentication flow"
        agentic search "error handling" --collection my-project -k 10
        agentic search "API endpoints" --json
    """
    from agentic_assistants.vectordb.base import VectorStore
    
    config = AgenticConfig()
    
    try:
        store = VectorStore.create(config=config)
        results = store.search(query=query, collection=collection, top_k=top_k)
        
        if as_json:
            import json
            output = {
                "query": query,
                "collection": collection,
                "results": [r.to_dict() for r in results],
            }
            console.print(json.dumps(output, indent=2))
            return
        
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return
        
        console.print(f"[cyan]Search:[/cyan] {query}")
        console.print(f"[dim]Collection: {collection} | Results: {len(results)}[/dim]\n")
        
        for i, r in enumerate(results, 1):
            file_path = r.document.metadata.get("file_path", "unknown")
            content = r.document.content[:200] + "..." if len(r.document.content) > 200 else r.document.content
            
            console.print(f"[bold]{i}.[/bold] [cyan]{file_path}[/cyan] [dim](score: {r.score:.3f})[/dim]")
            console.print(Panel(content, border_style="dim"))
        
    except Exception as e:
        console.print(f"[red]✗[/red] Search failed: {e}")
        raise SystemExit(1)


# =============================================================================
# SERVER COMMANDS
# =============================================================================


@cli.group()
def server():
    """Manage MCP and REST servers."""
    pass


@server.command("start")
@click.option("--host", default=None, help="Host to bind to")
@click.option("--port", "-p", default=None, type=int, help="Port to bind to")
@click.option("--no-mcp", is_flag=True, help="Disable MCP endpoint")
@click.option("--no-rest", is_flag=True, help="Disable REST endpoints")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def server_start(host: Optional[str], port: Optional[int], no_mcp: bool, no_rest: bool, reload: bool):
    """Start the MCP/REST server."""
    from agentic_assistants.server.app import start_server
    
    config = AgenticConfig()
    host = host or config.server.host
    port = port or config.server.port
    
    console.print(f"[yellow]Starting server on {host}:{port}...[/yellow]")
    console.print(f"  MCP: {'disabled' if no_mcp else 'enabled'}")
    console.print(f"  REST: {'disabled' if no_rest else 'enabled'}")
    console.print()
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    
    # Override config
    if no_mcp:
        config._server = config.server
        config._server.enable_mcp = False
    if no_rest:
        config._server = config.server
        config._server.enable_rest = False
    
    try:
        start_server(host=host, port=port, config=config, reload=reload)
    except KeyboardInterrupt:
        console.print("\n[green]✓[/green] Server stopped")


@server.command("status")
@click.option("--port", "-p", default=None, type=int, help="Port to check")
def server_status(port: Optional[int]):
    """Check server status."""
    import httpx
    
    config = AgenticConfig()
    port = port or config.server.port
    
    try:
        response = httpx.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓[/green] Server is running on port {port}")
            console.print(f"  Version: {data.get('version', 'unknown')}")
            console.print(f"  Vector Store: {data.get('vector_store', 'unknown')}")
        else:
            console.print(f"[yellow]![/yellow] Server returned status {response.status_code}")
    except httpx.RequestError:
        console.print(f"[red]✗[/red] Server is not running on port {port}")


# =============================================================================
# COLLECTIONS COMMANDS
# =============================================================================


@cli.group()
def collections():
    """Manage vector database collections."""
    pass


@collections.command("list")
def collections_list():
    """List all collections."""
    from agentic_assistants.vectordb.base import VectorStore
    
    config = AgenticConfig()
    store = VectorStore.create(config=config)
    
    collection_names = store.list_collections()
    
    if not collection_names:
        console.print("[yellow]No collections found.[/yellow]")
        console.print("Create one by indexing: agentic index ./path")
        return
    
    table = Table(title="Collections")
    table.add_column("Name", style="cyan")
    table.add_column("Documents", justify="right")
    
    for name in collection_names:
        count = store.count(name)
        table.add_row(name, str(count))
    
    console.print(table)


@collections.command("delete")
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def collections_delete(name: str, yes: bool):
    """Delete a collection."""
    from agentic_assistants.vectordb.base import VectorStore
    
    if not yes:
        if not click.confirm(f"Delete collection '{name}' and all its documents?"):
            console.print("Cancelled")
            return
    
    config = AgenticConfig()
    store = VectorStore.create(config=config)
    
    if store.delete_collection(name):
        console.print(f"[green]✓[/green] Deleted collection: {name}")
    else:
        console.print(f"[red]✗[/red] Collection not found: {name}")
        raise SystemExit(1)


@collections.command("info")
@click.argument("name")
def collections_info(name: str):
    """Show collection details."""
    from agentic_assistants.indexing.codebase import CodebaseIndexer
    from agentic_assistants.vectordb.base import VectorStore
    
    config = AgenticConfig()
    store = VectorStore.create(config=config)
    indexer = CodebaseIndexer(vector_store=store, config=config)
    
    if name not in store.list_collections():
        console.print(f"[red]✗[/red] Collection not found: {name}")
        raise SystemExit(1)
    
    stats = indexer.get_stats(name)
    
    table = Table(title=f"Collection: {name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    
    table.add_row("Total Files", str(stats["total_files"]))
    table.add_row("Total Chunks", str(stats["total_chunks"]))
    table.add_row("Total Size", f"{stats['total_size_bytes'] / 1024:.1f} KB")
    table.add_row("Vector Count", str(stats["vector_count"]))
    
    if stats["by_language"]:
        table.add_row("", "")
        table.add_row("[bold]By Language[/bold]", "")
        for lang, info in stats["by_language"].items():
            table.add_row(f"  {lang}", f"{info['files']} files, {info['chunks']} chunks")
    
    console.print(table)


# =============================================================================
# CONTEXT COMMANDS
# =============================================================================


@cli.group()
def context():
    """Manage AI assistant context for this codebase."""
    pass


@context.command("show")
@click.option(
    "--task",
    "-t",
    type=click.Choice(["understand", "add_adapter", "add_cli_command", "add_config", "debug"]),
    default="understand",
    help="Load context optimized for a specific task",
)
@click.option("--full", is_flag=True, help="Load full context (for large context windows)")
@click.option("--copy", "copy_to_clipboard", is_flag=True, help="Copy to clipboard")
def context_show(task: str, full: bool, copy_to_clipboard: bool):
    """Show context for AI coding assistants."""
    from agentic_assistants.utils.context_loader import ContextLoader

    loader = ContextLoader()

    if full:
        content = loader.load_full_context()
    else:
        content = loader.load_for_task(task)

    tokens = loader.estimate_tokens(content)
    console.print(f"[dim]Estimated tokens: ~{tokens}[/dim]\n")

    if copy_to_clipboard:
        try:
            import pyperclip

            pyperclip.copy(content)
            console.print("[green]✓[/green] Copied to clipboard!")
        except ImportError:
            console.print("[yellow]![/yellow] Install pyperclip for clipboard support: pip install pyperclip")
            console.print(content)
    else:
        console.print(content)


@context.command("summary")
def context_summary():
    """Show available context options and sizes."""
    from agentic_assistants.utils.context_loader import ContextLoader

    loader = ContextLoader()
    summary = loader.get_context_summary()

    table = Table(title="Available Context Options")
    table.add_column("Type", style="cyan")
    table.add_column("Files")
    table.add_column("Tokens", justify="right", style="green")

    table.add_row(
        "Core",
        ", ".join(summary["core_context"]["files"]),
        f"~{summary['core_context']['estimated_tokens']}",
    )
    table.add_row(
        "Full",
        ", ".join(summary["full_context"]["files"]),
        f"~{summary['full_context']['estimated_tokens']}",
    )

    for task, info in summary["tasks"].items():
        table.add_row(
            f"Task: {task}",
            ", ".join([f.split("/")[-1] for f in info["files"]]),
            f"~{info['estimated_tokens']}",
        )

    console.print(table)
    console.print("\n[dim]Use 'agentic context show --task <task>' to load specific context[/dim]")


# =============================================================================
# TEMPLATE COMMANDS
# =============================================================================


@cli.group("templates")
def templates():
    """Browse available project templates."""
    pass


@templates.command("list")
@click.option("--category", "-c", default=None, help="Filter by template category")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def templates_list(category: Optional[str], as_json: bool):
    """List available templates."""
    from agentic_assistants.templates import list_templates

    items = list_templates(category=category)
    if not items:
        console.print("[yellow]No templates found.[/yellow]")
        return

    if as_json:
        import json

        payload = [
            {
                "id": t.template_id,
                "name": t.name,
                "category": t.category,
                "level": t.level,
                "description": t.description,
                "tags": t.tags,
                "run_hint": t.run_hint,
            }
            for t in items
        ]
        click.echo(json.dumps(payload, indent=2))
        return

    table = Table(title="Template Catalog")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Level", style="yellow")
    table.add_column("Tags", style="dim")
    for t in items:
        table.add_row(
            t.template_id,
            t.name,
            t.category,
            t.level,
            ", ".join(t.tags),
        )
    console.print(table)


@templates.command("show")
@click.argument("template_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def templates_show(template_id: str, as_json: bool):
    """Show template details."""
    from agentic_assistants.templates import get_template

    template = get_template(template_id)
    if template is None:
        console.print(f"[red]✗[/red] Unknown template: {template_id}")
        raise SystemExit(1)

    if as_json:
        import json

        click.echo(
            json.dumps(
                {
                    "id": template.template_id,
                    "name": template.name,
                    "category": template.category,
                    "level": template.level,
                    "description": template.description,
                    "tags": template.tags,
                    "run_hint": template.run_hint,
                    "asset_dir": template.asset_dir,
                },
                indent=2,
            )
        )
        return

    details = (
        f"[bold]{template.name}[/bold]\n"
        f"\nID: {template.template_id}"
        f"\nCategory: {template.category}"
        f"\nLevel: {template.level}"
        f"\nTags: {', '.join(template.tags) if template.tags else '-'}"
        f"\n\n{template.description}"
    )
    if template.run_hint:
        details += f"\n\nRun hint: [cyan]{template.run_hint}[/cyan]"
    console.print(Panel(details, title="Template"))


@cli.command("init")
@click.argument("template_id")
@click.option("--output", "-o", default=".", type=click.Path(), help="Output directory")
@click.option("--name", "-n", default=None, help="Project folder name")
@click.option("--force", is_flag=True, help="Allow writing to non-empty output")
def init_template(template_id: str, output: str, name: Optional[str], force: bool):
    """Instantiate a template into your workspace."""
    from pathlib import Path

    from agentic_assistants.templates import get_template, scaffold_template

    try:
        output_dir = Path(output).expanduser().resolve()
        created_path = scaffold_template(
            template_id=template_id,
            output_dir=output_dir,
            project_name=name,
            force=force,
        )
    except FileExistsError as exc:
        console.print(f"[red]✗[/red] {exc}")
        raise SystemExit(1)
    except FileNotFoundError as exc:
        console.print(f"[red]✗[/red] {exc}")
        raise SystemExit(1)
    except ValueError as exc:
        console.print(f"[red]✗[/red] {exc}")
        raise SystemExit(1)

    template = get_template(template_id)
    console.print(f"[green]✓[/green] Template created at: {created_path}")
    if template and template.run_hint:
        console.print(f"[dim]Next:[/dim] cd {created_path} && {template.run_hint}")


# =============================================================================
# TRACES COMMANDS
# =============================================================================


@cli.group("traces")
def traces():
    """Manage OpenTelemetry trace files (export, import, sync)."""
    pass


@traces.command("status")
def traces_status():
    """Show pending trace files and store location."""
    from agentic_assistants.observability.trace_store import TraceStore

    config = AgenticConfig()
    store = TraceStore(config.telemetry.file_export_path)
    files = store.pending_files()

    table = Table(title="Trace Store Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Store directory", str(store.store_dir.resolve()))
    table.add_row("Pending files", str(len(files)))
    if files:
        table.add_row("Oldest file", files[0].name)
        table.add_row("Newest file", files[-1].name)

    console.print(table)


@traces.command("export")
@click.option("--output", "-o", required=True, type=click.Path(), help="Destination directory")
def traces_export(output: str):
    """Copy pending trace files to a backup directory."""
    from agentic_assistants.observability.trace_store import TraceStore

    config = AgenticConfig()
    store = TraceStore(config.telemetry.file_export_path)
    count = store.export_to_file(output)
    console.print(f"[green]Exported {count} trace file(s) to {output}[/green]")


@traces.command("import")
@click.option("--input", "-i", "input_dir", required=True, type=click.Path(exists=True), help="Source directory")
@click.option("--endpoint", "-e", required=True, help="OTLP HTTP endpoint (e.g. http://localhost:4318)")
@click.option("--delete", is_flag=True, help="Delete files after successful import")
def traces_import(input_dir: str, endpoint: str, delete: bool):
    """Import trace files into an OTLP collector."""
    from agentic_assistants.observability.trace_store import TraceStore

    store = TraceStore()
    count = store.import_from_file(input_dir, endpoint, delete_on_success=delete)
    console.print(f"[green]Imported {count} trace file(s) to {endpoint}[/green]")


@traces.command("sync")
@click.option("--endpoint", "-e", default=None, help="OTLP HTTP endpoint (auto-detects if omitted)")
def traces_sync(endpoint: Optional[str]):
    """Sync pending file traces to a live OTLP collector."""
    from agentic_assistants.observability.trace_store import TraceStore

    config = AgenticConfig()
    store = TraceStore(config.telemetry.file_export_path)

    if not endpoint:
        endpoint = config.telemetry.exporter_otlp_endpoint.replace(":4317", ":4318")
        console.print(f"[dim]Auto-detected endpoint: {endpoint}[/dim]")

    pending = store.pending_count()
    if pending == 0:
        console.print("[yellow]No pending trace files to sync.[/yellow]")
        return

    console.print(f"Syncing {pending} trace file(s) to {endpoint} ...")
    count = store.sync_to_collector(endpoint)
    console.print(f"[green]Successfully synced {count} / {pending} trace file(s).[/green]")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()

