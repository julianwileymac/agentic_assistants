# Development Guide

This guide will help you set up and run the Agentic Assistants development environment.

## Prerequisites

- **Python 3.10 or 3.11** (not 3.12+)
- **Node.js 18+** (for Theia IDE)
- **Poetry** (for Python dependency management)
- **Git**

### Installing Prerequisites

#### Windows

```powershell
# Install Python 3.11
# Download from https://www.python.org/downloads/

# Install Node.js 18+
# Download from https://nodejs.org/

# Install Poetry
pip install poetry
```

#### Linux/Mac

```bash
# Install Python 3.11 (if not already installed)
# Use your package manager (apt, brew, etc.)

# Install Node.js 18+ using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agentic_assistants.git
cd agentic_assistants
```

### 2. Install Python Dependencies

```bash
# Create and activate virtual environment (optional)
python -m venv py11_venv
source py11_venv/bin/activate  # Linux/Mac
# OR
.\py11_venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
poetry install

# OR if not using Poetry
pip install -e .
```

### 3. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your settings (optional)
```

### 4. Start Development Environment

#### Full Stack (Backend + Frontend)

**Windows:**
```powershell
.\scripts\start-dev.ps1
```

**Linux/Mac:**
```bash
./scripts/start-dev.sh
```

This will start:
- Python Backend on http://localhost:8080
- Theia IDE on http://localhost:3000
- MLFlow on http://localhost:5000

**Note:** The first time you run this, it will take 15-20 minutes to install Node.js dependencies and build Theia. Subsequent starts will be much faster.

#### Backend Only

If you don't need the Theia IDE:

**Windows:**
```powershell
.\scripts\start-dev.ps1 -BackendOnly
```

**Linux/Mac:**
```bash
./scripts/start-dev.sh --backend
```

### 5. Stop Services

**Windows:**
```powershell
.\scripts\stop-dev.ps1
```

**Linux/Mac:**
```bash
./scripts/stop-dev.sh
```

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| **Theia IDE** | 3000 | Web-based IDE with custom extensions for experiment tracking, artifact management, and data viewing |
| **Python Backend** | 8080 | FastAPI server with REST API and WebSocket support |
| **MLFlow** | 5000 | Experiment tracking server |
| **WebSocket** | 8080/ws | Real-time event streaming |

## API Documentation

Once the backend is running, visit:

- **Interactive API Docs**: http://localhost:8080/docs
- **Alternative Docs**: http://localhost:8080/redoc

## Theia IDE Features

The Theia IDE includes custom extensions for:

### 1. Experiments (MLFlow Integration)
- View and create experiments
- Start/stop runs
- Log metrics and parameters
- Browse run artifacts

### 2. Artifacts
- Upload and manage artifacts
- Tag and group artifacts
- Share artifacts across sessions
- Download artifacts

### 3. Data Viewer
- Browse data files
- Preview tables (Parquet, CSV)
- View schemas
- Convert file formats

### 4. Sessions
- Create and manage sessions
- View session history
- Track interactions

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_assistants

# Run specific test file
pytest tests/test_config.py
```

### Linting and Formatting

```bash
# Run Ruff linter
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Type checking
mypy src/
```

### CLI Usage

The CLI is available when the package is installed:

```bash
# Show help
agentic --help

# List available models
agentic ollama list

# Pull a model
agentic ollama pull llama3.2

# Show configuration
agentic config show

# Create an experiment
agentic mlflow create my-experiment
```

## Docker Development

If you prefer Docker:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Troubleshooting

### Backend won't start

1. **Check Python version**: `python --version` (must be 3.10 or 3.11)
2. **Check dependencies**: `poetry install` or `pip install -e .`
3. **Check logs**: `cat backend.log` or `type backend.log` (Windows)
4. **Check port availability**: Make sure port 8080 isn't in use

### Frontend won't start

1. **Check Node version**: `node --version` (must be 18+)
2. **Install dependencies**: `cd frontend && yarn install`
3. **Build Theia**: `cd frontend && yarn build`
4. **Check logs**: `cat theia.log` or `type theia.log` (Windows)
5. **Check port availability**: Make sure port 3000 isn't in use

### Dependency conflicts

If you encounter Python dependency conflicts:

```bash
# Clear lock file and reinstall
rm poetry.lock
poetry lock
poetry install
```

### Services won't stop

Force kill all services:

**Windows:**
```powershell
.\scripts\stop-dev.ps1 -Force
```

**Linux/Mac:**
```bash
./scripts/stop-dev.sh --force
```

## Project Structure

```
agentic_assistants/
├── src/agentic_assistants/     # Python source code
│   ├── server/                 # FastAPI backend
│   │   ├── api/                # REST API routers
│   │   ├── rest.py             # Main REST server
│   │   └── websocket.py        # WebSocket handler
│   ├── core/                   # Core functionality
│   ├── adapters/               # Agent framework adapters
│   ├── data/                   # Data layer
│   │   ├── layer.py            # Data I/O layer
│   │   └── shared_storage.py  # Shared storage manager
│   ├── config.py               # Configuration system
│   └── cli.py                  # CLI commands
├── frontend/                   # Theia IDE frontend
│   ├── packages/               # Theia extensions
│   │   ├── agentic-core/       # Core extension
│   │   ├── agentic-mlflow/     # MLFlow integration
│   │   ├── agentic-artifacts/  # Artifact manager
│   │   └── agentic-data-viewer/# Data viewer
│   └── browser-app/            # Theia application
├── scripts/                    # Development scripts
├── tests/                      # Test files
├── examples/                   # Example scripts
├── notebooks/                  # Jupyter notebooks
├── docker/                     # Docker files
├── pyproject.toml              # Python dependencies
└── docker-compose.yml          # Docker services
```

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for sample code
2. **Read the Docs**: Visit the `docs/` directory for detailed documentation
3. **Try the CLI**: Run `agentic --help` to see available commands
4. **Open Theia**: Visit http://localhost:3000 to use the IDE
5. **View MLFlow**: Visit http://localhost:5000 to track experiments

## Getting Help

- Check the logs in the project root directory
- Review the `scripts/README.md` for script usage
- Read the API docs at http://localhost:8080/docs
- See the plan document at `.cursor/plans/theia_ide_integration_*.plan.md`

## Contributing

See `CONTRIBUTING.md` for guidelines on contributing to the project.


