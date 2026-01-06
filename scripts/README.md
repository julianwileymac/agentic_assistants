# Agentic Assistants - Development Scripts

This directory contains scripts to help you start and stop the development environment.

## Quick Start

### Windows (PowerShell)

```powershell
# Start all services
.\scripts\start-dev.ps1

# Start with Web UI Control Panel
.\scripts\start-webui.ps1

# Start JupyterLab only
.\scripts\start-lab.ps1

# Stop all services
.\scripts\stop-dev.ps1

# Start only backend
.\scripts\start-dev.ps1 -BackendOnly

# Don't open browser
.\scripts\start-dev.ps1 -NoBrowser
```

### Linux/Mac/Git Bash

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Start all services
./scripts/start-dev.sh

# Start with Web UI Control Panel
./scripts/start-webui.sh

# Start JupyterLab only
./scripts/start-lab.sh

# Stop all services
./scripts/stop-dev.sh

# Start only backend
./scripts/start-dev.sh --backend

# Choose IDE (jupyterlab, theia, or none)
./scripts/start-dev.sh --ide jupyterlab

# Don't open browser
./scripts/start-dev.sh --no-browser
```

## Services

When you run the development startup script, the following services will be started:

| Service | Port | URL |
|---------|------|-----|
| Web UI Control Panel | 3000 | http://localhost:3000 |
| Python Backend | 8080 | http://localhost:8080 |
| MLFlow | 5000 | http://localhost:5000 |
| JupyterLab | 8888 | http://localhost:8888 |
| WebSocket | 8080 | ws://localhost:8080/ws |

## Web UI Control Panel

The new **Agentic Control Panel** provides a modern web interface for managing your agentic development environment:

- **Dashboard**: System health overview and quick actions
- **Projects**: Manage top-level project containers
- **Agents**: Create and monitor AI agents
- **Flows**: Design multi-agent workflows with YAML
- **Components**: Library of reusable code snippets
- **Experiments**: MLFlow experiment tracking wrapper
- **Monitoring**: System telemetry and metrics
- **Knowledge Bases**: Vector store collection management

### Starting the Web UI

```bash
# Start Web UI in development mode (with hot reload)
./scripts/start-webui.sh --dev

# Start Web UI in production mode
./scripts/start-webui.sh

# Custom port
./scripts/start-webui.sh --port 3001
```

```powershell
# PowerShell
.\scripts\start-webui.ps1 -Dev
.\scripts\start-webui.ps1 -Port 3001
```

### Backend API Endpoints

The Web UI connects to these backend API endpoints:

**Control Panel APIs:**
- `GET/POST /api/v1/projects` - Project management
- `GET/POST /api/v1/agents` - Agent management
- `GET/POST /api/v1/flows` - Flow management
- `GET/POST /api/v1/components` - Component library
- `GET/POST /api/v1/notes` - Free-form notes
- `GET/POST /api/v1/tags` - Resource tagging
- `GET /api/v1/stats` - System statistics

**Original APIs:**
- `GET/POST /api/v1/experiments` - MLFlow experiments
- `GET/POST /api/v1/artifacts` - Artifact storage
- `GET/POST /api/v1/sessions` - Session management
- `GET/POST /api/v1/data` - Data layer operations
- `GET /api/v1/config` - Runtime configuration
- `GET /health` - Health check

## JupyterLab

JupyterLab provides interactive notebooks for experimentation:

```bash
# Start JupyterLab
./scripts/start-lab.sh

# Custom port
JUPYTER_PORT=9999 ./scripts/start-lab.sh
```

```powershell
# PowerShell
.\scripts\start-lab.ps1
.\scripts\start-lab.ps1 -Port 9999
```

JupyterLab has access to:
- All project notebooks (`notebooks/`)
- Source code (`src/`)
- Data directory (`data/`)
- MLFlow runs (`mlruns/`)

## Logs

Service logs are written to the project root:

- `backend.log` - FastAPI backend logs
- `mlflow.log` - MLFlow server logs
- `jupyterlab.log` - JupyterLab logs
- `webui.log` - Web UI logs (if running in background)

If a service fails to start, check these log files for errors.

## Process IDs

The scripts create PID files in the project root to track running processes:

- `.backend.pid`
- `.mlflow.pid`
- `.jupyter.pid`
- `.webui.pid`

These are used by the stop script to cleanly shut down services.

## Troubleshooting

For detailed troubleshooting information, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) in the project root.

### Quick Fixes

**Backend won't start**: Check `backend.log`, ensure `poetry install` has run, check port 8080

**Web UI won't start**: Check if `npm install` has run in `webui/`, ensure Node.js 18+ is installed

**JupyterLab won't start**: Ensure `jupyter` is installed (`pip install jupyterlab`), check port 8888

**Services won't stop**: Delete PID files manually: `rm .backend.pid .mlflow.pid .jupyter.pid .webui.pid`

## First Time Setup

The first time you run the scripts, they will:

1. Check and install Python packages (`poetry install`)
2. Install Web UI dependencies (`npm install` in `webui/`)
3. Build the Web UI (`npm run build`)

This is a one-time setup. Subsequent starts will be much faster.

## Docker Alternative

If you prefer to use Docker instead of running services locally:

```bash
# Start all services with Docker
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Start specific service
docker-compose up -d agentic-api
```

## IDE Options

The development environment supports multiple IDE options:

| IDE | Command | Description |
|-----|---------|-------------|
| Web UI | `start-webui.sh` | Modern React control panel |
| JupyterLab | `start-lab.sh` | Interactive notebooks |
| Theia | `--ide theia` | VS Code-like IDE (experimental) |
| None | `--ide none` | Backend only, no IDE |

## Legacy Scripts

The older startup scripts are still available:

- `start.ps1` / `start.sh` - Simple startup without IDE
- `start-enhanced.ps1` - Enhanced startup with dependency checks
- `stop.ps1` / `stop.sh` - Simple stop scripts

These are kept for backward compatibility but we recommend using the new scripts.
