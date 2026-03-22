#!/bin/bash
# =============================================================================
# Agentic Assistants - Development Startup Script (Bash)
# =============================================================================
# This script starts all services for development:
#   1. Python backend (FastAPI + WebSocket on port 8080)
#   2. IDE frontend (Theia or JupyterLab)
#   3. MLFlow server (port 5000)
#   4. Opens browser to IDE UI
#
# Usage:
#   ./scripts/start-dev.sh              # Start all services (backend + Web UI)
#   ./scripts/start-dev.sh --backend    # Start only Python backend
#   ./scripts/start-dev.sh --frontend   # Start only UI (Web UI / JupyterLab / Theia)
#   ./scripts/start-dev.sh --ide|--ui webui|jupyterlab|theia|none   # Choose UI (default: webui)
#   ./scripts/start-dev.sh --no-browser # Don't open browser
# =============================================================================

set -e

BACKEND_ONLY=false
FRONTEND_ONLY=false
NO_BROWSER=false
IDE_CHOICE="webui"  # default to Web UI (Theia flaky)
JUPYTER_PORT=${JUPYTER_PORT:-8888}
WEBUI_PORT=${WEBUI_PORT:-3000}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend)
            FRONTEND_ONLY=true
            shift
            ;;
        --ide|--ui)
            IDE_CHOICE="$2"
            shift 2
            ;;
        --no-browser)
            NO_BROWSER=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/start-dev.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend                Start only the Python backend"
            echo "  --frontend               Start only the IDE frontend"
            echo "  --ide jupyterlab|theia   Choose IDE backend (default: jupyterlab)"
            echo "  --no-browser             Don't open browser after startup"
            echo "  --help                   Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
SKIP_THEIA=false

function write_banner() {
    echo ""
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}       AGENTIC ASSISTANTS - DEVELOPMENT ENVIRONMENT           ${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo ""
}

function write_section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

function write_step() {
    echo -e "${GRAY}  -> $1${NC}"
}

function write_success() {
    echo -e "${GREEN}  [OK] $1${NC}"
}

function write_error() {
    echo -e "${RED}  [ERROR] $1${NC}"
}

function write_warning() {
    echo -e "${YELLOW}  [WARNING] $1${NC}"
}

function start_python_backend() {
    write_section "Starting Python Backend"
    
    cd "$PROJECT_DIR"
    
    # Detect OS for virtual environment activation
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Git Bash on Windows
        VENV_ACTIVATE_PATH="Scripts/activate"
    else
        # Linux/Mac
        VENV_ACTIVATE_PATH="bin/activate"
    fi
    
    # Check for virtual environment (prefer Poetry's managed venv where
    # packages are actually installed, fall back to manual venvs)
    if command -v poetry &> /dev/null; then
        POETRY_VENV=$(poetry env info --path 2>/dev/null || echo "")
        if [ -n "$POETRY_VENV" ] && [ -d "$POETRY_VENV" ]; then
            write_step "Using Poetry virtual environment"
            if [ -f "$POETRY_VENV/$VENV_ACTIVATE_PATH" ]; then
                source "$POETRY_VENV/$VENV_ACTIVATE_PATH"
            fi
        elif [ -d "py11_venv" ] && [ -f "py11_venv/$VENV_ACTIVATE_PATH" ]; then
            write_step "Using manual virtual environment (py11_venv)"
            source "py11_venv/$VENV_ACTIVATE_PATH"
        fi
    elif [ -d "py11_venv" ] && [ -f "py11_venv/$VENV_ACTIVATE_PATH" ]; then
        write_step "Using manual virtual environment (py11_venv)"
        source "py11_venv/$VENV_ACTIVATE_PATH"
    else
        write_step "No virtual environment found, using system Python"
    fi
    
    # Check if agentic_assistants package is installed
    if ! python -c "import agentic_assistants" 2>/dev/null; then
        write_error "agentic_assistants package not installed"
        write_step "Installing package..."
        if command -v poetry &> /dev/null && [ -f "pyproject.toml" ]; then
            poetry install --no-root 2>&1 | tail -5
            poetry install 2>&1 | tail -5
        else
            pip install -e . 2>&1 | tail -5
        fi
        
        # Check again
        if ! python -c "import agentic_assistants" 2>/dev/null; then
            write_error "Failed to install package. Try manually: poetry install or pip install -e ."
            return 1
        fi
        write_success "Package installed"
    fi
    
    # Create mlruns directory
    mkdir -p mlruns
    
    # Start MLFlow
    write_step "Starting MLFlow server..."
    mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri ./mlruns > mlflow.log 2>&1 &
    MLFLOW_PID=$!
    echo $MLFLOW_PID > .mlflow.pid
    write_success "MLFlow started on port 5000 (PID: $MLFLOW_PID)"
    
    # Start FastAPI backend
    write_step "Starting FastAPI backend..."
    python -m uvicorn agentic_assistants.server.rest:create_rest_app --factory --host 127.0.0.1 --port 8080 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
    write_success "Backend started on port 8080 (PID: $BACKEND_PID)"
    
    # Wait for backend to be ready
    echo -n "  Waiting for backend"
    for i in {1..60}; do
        sleep 1
        
        # Check if process is still running
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo ""
            write_error "Backend process died. Check backend.log for errors."
            if [ -f backend.log ]; then
                echo -e "${YELLOW}Last 10 lines of backend.log:${NC}"
                tail -10 backend.log | sed 's/^/  /'
            fi
            return 1
        fi
        
        # Check if backend is ready using lightweight /ready endpoint
        # Method 1: curl
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 http://localhost:8080/ready > /dev/null 2>&1; then
                echo ""
                write_success "Backend is ready"
                return 0
            fi
        # Method 2: wget
        elif command -v wget &> /dev/null; then
            if wget -q --timeout=2 --spider http://localhost:8080/ready 2>/dev/null; then
                echo ""
                write_success "Backend is ready"
                return 0
            fi
        # Method 3: Python (works on all platforms)
        else
            if python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/ready', timeout=2)" 2>/dev/null; then
                echo ""
                write_success "Backend is ready"
                return 0
            fi
        fi
        
        echo -n "."
    done
    
    echo ""
    write_warning "Backend health check timed out, but process is running. Continuing..."
    echo -e "${YELLOW}  Check backend.log if you encounter issues${NC}"
    return 0
}

function start_jupyterlab() {
    write_section "Starting JupyterLab"

    cd "$PROJECT_DIR"

    # Ensure data dirs exist for notebooks and artifacts
    mkdir -p notebooks data mlruns

    # Start JupyterLab
    write_step "Launching JupyterLab on port ${JUPYTER_PORT} (root: $PROJECT_DIR)"
    nohup jupyter lab \
        --ip 127.0.0.1 \
        --port ${JUPYTER_PORT} \
        --no-browser \
        --NotebookApp.token='' \
        --NotebookApp.password='' \
        --NotebookApp.notebook_dir="$PROJECT_DIR" \
        > jupyterlab.log 2>&1 &

    JUPYTER_PID=$!
    echo $JUPYTER_PID > .jupyter.pid
    write_success "JupyterLab started on http://localhost:${JUPYTER_PORT}/lab (PID: $JUPYTER_PID)"
}

function start_theia_frontend() {
    write_section "Starting Theia Frontend"
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        write_warning "Frontend directory not found. Theia IDE is not set up yet."
        echo "  To set up Theia, run: cd frontend && yarn install && yarn build"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        write_error "Node.js is not installed. Please install Node.js 18 or 20 LTS to use Theia IDE."
        return 1
    fi
    
    NODE_VERSION=$(node --version)
    write_step "Node.js version: $NODE_VERSION"
    
    # Check Node.js version - must be 18.x or 20.x (not 22+ due to native module issues)
    NODE_MAJOR=$(echo "$NODE_VERSION" | sed 's/v\([0-9]*\).*/\1/')
    if [ "$NODE_MAJOR" -gt 20 ]; then
        write_error "Node.js $NODE_VERSION is too new. Theia requires Node.js 18 or 20 LTS."
        write_warning "Please install Node.js 20 LTS:"
        echo "  - Windows: Download from https://nodejs.org/en/download/"
        echo "  - Or use nvm: nvm install 20 && nvm use 20"
        echo ""
        write_step "Skipping Theia frontend due to incompatible Node.js version."
        return 1
    elif [ "$NODE_MAJOR" -lt 18 ]; then
        write_error "Node.js $NODE_VERSION is too old. Theia requires Node.js 18 or 20 LTS."
        write_step "Skipping Theia frontend due to incompatible Node.js version."
        return 1
    fi
    
    # Enable Corepack for Yarn
    if command -v corepack &> /dev/null; then
        corepack enable 2>/dev/null || true
    fi
    
    # Fix: Check for interfering yarn.lock in parent directories
    if [ ! -f "yarn.lock" ]; then
        write_step "Creating yarn.lock to prevent workspace conflicts..."
        touch yarn.lock
    fi
    
    # Check for .yarnrc.yml
    if [ ! -f ".yarnrc.yml" ]; then
        write_step "Creating .yarnrc.yml configuration..."
        cat > .yarnrc.yml << 'EOF'
nodeLinker: node-modules
enableGlobalCache: true
EOF
    fi
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        write_step "Installing dependencies (this may take 10-15 minutes)..."
        echo -e "${YELLOW}  This is a one-time setup. Please be patient...${NC}"
        
        # Set Corepack to non-interactive mode
        export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
        
        # For Windows, warn about native modules
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            write_warning "On Windows, some native modules may fail to build."
            write_step "If installation fails, you may need Visual Studio Build Tools."
            write_step "Download from: https://visualstudio.microsoft.com/downloads/"
            echo ""
        fi
        
        yarn install 2>&1 | tee "$PROJECT_DIR/yarn-install.log"
        INSTALL_EXIT_CODE=${PIPESTATUS[0]}
        
        if [ $INSTALL_EXIT_CODE -ne 0 ]; then
            write_warning "Installation failed (native modules need compilation)."
            echo ""
            write_error "Theia requires Visual Studio Build Tools on Windows."
            echo ""
            echo -e "${YELLOW}  To install Visual Studio Build Tools:${NC}"
            echo "  1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
            echo "  2. Run the installer"
            echo "  3. Select 'Desktop development with C++'"
            echo "  4. Complete installation and restart your terminal"
            echo "  5. Run this script again"
            echo ""
            echo -e "${YELLOW}  Alternative: Use Docker for the full IDE experience:${NC}"
            echo "  docker-compose up -d agentic-ide"
            echo ""
            write_warning "Continuing without Theia IDE..."
            write_step "You can still use the Python backend and MLFlow"
            SKIP_THEIA=true
            return 0
        else
            write_success "Dependencies installed"
            SKIP_THEIA=false
        fi
    else
        write_step "Dependencies already installed"
    fi
    
    # Skip if native modules failed
    if [ "$SKIP_THEIA" = true ]; then
        return 0
    fi
    
    # Build if lib doesn't exist
    BUILD_APP="browser-app"
    if [ ! -d "$BUILD_APP/lib" ]; then
        write_step "Building Theia - this may take 5-10 minutes..."
        echo -e "${YELLOW}  This is a one-time build. Please be patient...${NC}"
        
        yarn workspace $BUILD_APP build 2>&1 | tail -10
        if [ $? -ne 0 ]; then
            write_error "Failed to build Theia. Try manually: cd frontend && yarn workspace $BUILD_APP build"
            return 1
        fi
        write_success "Theia built successfully"
    else
        write_step "Theia already built"
    fi
    
    # Start Theia
    write_step "Starting Theia IDE..."
    cd "$FRONTEND_DIR/browser-app"
    yarn start > "$PROJECT_DIR/theia.log" 2>&1 &
    THEIA_PID=$!
    echo $THEIA_PID > "$PROJECT_DIR/.theia.pid"
    write_success "Theia started on port 3000 (PID: $THEIA_PID)"
    
    # Wait for Theia to be ready
    echo -n "  Waiting for Theia to start"
    for i in {1..120}; do
        sleep 1
        
        # Check if process is still running
        if ! kill -0 $THEIA_PID 2>/dev/null; then
            echo ""
            write_error "Theia process died. Check theia.log for errors."
            return 1
        fi
        
        # Check if port is listening
        if command -v nc &> /dev/null; then
            if nc -z 127.0.0.1 3000 2>/dev/null; then
                echo ""
                write_success "Theia is ready"
                return 0
            fi
        elif command -v wget &> /dev/null; then
            if wget -q --spider http://localhost:3000 2>/dev/null; then
                echo ""
                write_success "Theia is ready"
                return 0
            fi
        fi
        
        echo -n "."
    done
    
    echo ""
    write_warning "Theia may still be starting. Check http://localhost:3000 in a moment."
    return 0
}

function start_webui() {
    write_section "Starting Web UI (Next.js)"

    WEBUI_DIR="$PROJECT_DIR/webui"

    if [ ! -d "$WEBUI_DIR" ]; then
        write_error "Web UI directory not found at $WEBUI_DIR"
        write_step "Run: npx create-next-app webui  (already scaffolded in repo)"
        return 1
    fi

    cd "$WEBUI_DIR"

    # Ensure dependencies
    if [ ! -d "node_modules" ]; then
        write_step "Installing Web UI dependencies..."
        npm install >/dev/null 2>&1 || npm install
    else
        write_step "Dependencies already installed"
    fi

    # Start Next.js (dev server for fast reload)
    write_step "Starting Next.js dev server on port ${WEBUI_PORT}..."
    PORT=${WEBUI_PORT} npm run dev -- --hostname 127.0.0.1 > "$PROJECT_DIR/webui.log" 2>&1 &
    WEBUI_PID=$!
    echo $WEBUI_PID > "$PROJECT_DIR/.webui.pid"
    write_success "Web UI started on http://localhost:${WEBUI_PORT} (PID: $WEBUI_PID)"

    echo -n "  Waiting for Web UI"
    for i in {1..60}; do
        sleep 1

        if ! kill -0 $WEBUI_PID 2>/dev/null; then
            echo ""
            write_error "Web UI process died. Check webui.log for errors."
            return 1
        fi

        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 http://localhost:${WEBUI_PORT} > /dev/null 2>&1; then
                echo ""
                write_success "Web UI is ready"
                return 0
            fi
        fi

        echo -n "."
    done

    echo ""
    write_warning "Web UI health check timed out, but process is running. Continuing..."
    return 0
}

function open_browser() {
    write_section "Opening Browser"
    write_step "Opening $1"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$1" &
    elif command -v open &> /dev/null; then
        open "$1" &
    elif command -v start &> /dev/null; then
        start "$1" &
    else
        write_warning "Could not detect browser command. Please open $1 manually."
    fi
}

function show_summary() {
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}       DEVELOPMENT ENVIRONMENT READY                          ${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo -e "${CYAN}Services Running:${NC}"
    case "$IDE_CHOICE" in
        webui)
            echo "  - Web UI:          http://localhost:${WEBUI_PORT}"
            ;;
        jupyterlab)
            echo "  - JupyterLab:      http://localhost:${JUPYTER_PORT}/lab"
            ;;
        theia)
            if [ "$SKIP_THEIA" = true ]; then
                echo "  - Theia IDE:       ${YELLOW}Not started (native modules need compilation)${NC}"
            else
                echo "  - Theia IDE:       http://localhost:3000"
            fi
            ;;
        *)
            echo "  - UI:              (disabled)"
            ;;
    esac
    echo "  - Python Backend:  http://localhost:8080"
    echo "  - MLFlow:          http://localhost:5000"
    echo "  - WebSocket:       ws://localhost:8080/ws"
    echo ""
    echo -e "${CYAN}API Endpoints:${NC}"
    echo "  - Experiments:     http://localhost:8080/api/v1/experiments"
    echo "  - Artifacts:       http://localhost:8080/api/v1/artifacts"
    echo "  - Sessions:        http://localhost:8080/api/v1/sessions"
    echo "  - Data:            http://localhost:8080/api/v1/data"
    echo "  - Config:          http://localhost:8080/api/v1/config"
    echo ""
    if [ "$SKIP_THEIA" = true ]; then
        echo -e "${YELLOW}NOTE: Theia IDE requires Visual Studio Build Tools on Windows.${NC}"
        echo -e "${YELLOW}      Install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/${NC}"
        echo ""
    fi
    echo -e "${YELLOW}To stop all services: ./scripts/stop-dev.sh${NC}"
    echo ""
}

# Main execution
write_banner
cd "$PROJECT_DIR"

BACKEND_OK=true
FRONTEND_OK=true

if [ "$FRONTEND_ONLY" = false ]; then
    start_python_backend || BACKEND_OK=false
fi

if [ "$BACKEND_ONLY" = false ]; then
    case "$IDE_CHOICE" in
        theia)
            start_theia_frontend || FRONTEND_OK=false
            ;;
        jupyterlab)
            start_jupyterlab || FRONTEND_OK=false
            ;;
        webui)
            start_webui || FRONTEND_OK=false
            ;;
        none)
            write_warning "UI disabled (--ide none). Skipping frontend."
            ;;
        *)
            write_warning "Unknown UI choice '$IDE_CHOICE'. Skipping frontend."
            ;;
    esac
fi

show_summary

if [ "$NO_BROWSER" = false ] && [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_OK" = true ]; then
    case "$IDE_CHOICE" in
        theia)
            open_browser "http://localhost:3000"
            ;;
        jupyterlab)
            open_browser "http://localhost:${JUPYTER_PORT}/lab"
            ;;
        webui)
            open_browser "http://localhost:${WEBUI_PORT}"
            ;;
    esac
fi

