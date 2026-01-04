# Agentic Assistants - Development Scripts

This directory contains scripts to help you start and stop the development environment.

## Quick Start

### Windows (PowerShell)

```powershell
# Start all services
.\scripts\start-dev.ps1

# Stop all services
.\scripts\stop-dev.ps1

# Start only backend
.\scripts\start-dev.ps1 -BackendOnly

# Start only frontend
.\scripts\start-dev.ps1 -FrontendOnly

# Don't open browser
.\scripts\start-dev.ps1 -NoBrowser
```

### Linux/Mac/Git Bash

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Start all services
./scripts/start-dev.sh

# Stop all services
./scripts/stop-dev.sh

# Start only backend
./scripts/start-dev.sh --backend

# Start only frontend
./scripts/start-dev.sh --frontend

# Don't open browser
./scripts/start-dev.sh --no-browser
```

## Services

When you run the development startup script, the following services will be started:

| Service | Port | URL |
|---------|------|-----|
| Theia IDE | 3000 | http://localhost:3000 |
| Python Backend | 8080 | http://localhost:8080 |
| MLFlow | 5000 | http://localhost:5000 |
| WebSocket | 8080 | ws://localhost:8080/ws |

## Logs

Service logs are written to the project root:

- `backend.log` - FastAPI backend logs
- `mlflow.log` - MLFlow server logs
- `theia.log` - Theia IDE logs

If a service fails to start, check these log files for errors.

## Process IDs

The scripts create PID files in the project root to track running processes:

- `.backend.pid`
- `.mlflow.pid`
- `.theia.pid`

These are used by the stop script to cleanly shut down services.

## Troubleshooting

For detailed troubleshooting information, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) in the project root.

### Quick Fixes

**Backend won't start**: Check `backend.log`, ensure `poetry install` has run, check port 8080

**Frontend won't start**: Check `frontend.log`, ensure Node.js 18+ is installed, try `yarn install --ignore-optional` on Windows

**Yarn workspace error**: The scripts now automatically fix this by creating `yarn.lock` in the frontend directory

**Native module build failures**: The scripts automatically retry with `--ignore-optional` flag

**Services won't stop**: Delete PID files manually: `rm .backend.pid .frontend.pid .mlflow.pid`

## First Time Setup

The first time you run `start-dev.ps1` or `start-dev.sh`, it will:

1. Check and install Python package if needed (`poetry install`)
2. Install Node.js dependencies (10-15 minutes)
3. Build Theia IDE (5-10 minutes)

This is a one-time setup. Subsequent starts will be much faster.

### Automatic Fixes

The scripts now automatically handle common issues:

- **Virtual environment detection**: Works on both Windows and Unix-like systems
- **Yarn workspace conflicts**: Creates necessary `.yarnrc.yml` and `yarn.lock` files
- **Native module build failures**: Attempts fallback with `--ignore-optional` on Windows
- **Missing package installation**: Runs `poetry install` if `agentic_assistants` is not found
- **Non-interactive mode**: Sets environment variables to prevent prompts

For more details on troubleshooting, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) in the project root.

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
docker-compose up -d agentic-ide
```

## API Endpoints

Once the backend is running, you can access these API endpoints:

- **Experiments**: http://localhost:8080/api/v1/experiments
- **Artifacts**: http://localhost:8080/api/v1/artifacts
- **Sessions**: http://localhost:8080/api/v1/sessions
- **Data**: http://localhost:8080/api/v1/data
- **Config**: http://localhost:8080/api/v1/config
- **Health**: http://localhost:8080/health

## Legacy Scripts

The older startup scripts are still available:

- `start.ps1` / `start.sh` - Simple startup without Theia
- `start-enhanced.ps1` - Enhanced startup with dependency checks
- `stop.ps1` / `stop.sh` - Simple stop scripts

These are kept for backward compatibility but we recommend using the new `start-dev.ps1` / `start-dev.sh` scripts.

