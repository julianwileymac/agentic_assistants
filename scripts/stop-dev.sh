#!/bin/bash
# =============================================================================
# Agentic Assistants - Stop Development Services (Bash)
# =============================================================================
# Stops all running development services
#
# Usage:
#   ./scripts/stop-dev.sh        # Stop all services
#   ./scripts/stop-dev.sh --force # Force kill all processes on ports
# =============================================================================

# Parse arguments
FORCE=false

for arg in "$@"; do
    case $arg in
        --force|-f)
            FORCE=true
            shift
            ;;
    esac
done

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}Stopping development services...${NC}"
echo ""

STOPPED=false

# Function to kill a process and all its children
kill_process_tree() {
    local PID=$1
    local SERVICE_NAME=$2
    
    if [ -z "$PID" ]; then
        return 1
    fi
    
    # Check if process exists
    if ! kill -0 $PID 2>/dev/null; then
        return 1
    fi
    
    # Get all child processes first
    local CHILDREN=""
    if command -v pgrep &> /dev/null; then
        CHILDREN=$(pgrep -P $PID 2>/dev/null)
    elif command -v ps &> /dev/null; then
        CHILDREN=$(ps --ppid $PID -o pid= 2>/dev/null | tr -d ' ')
    fi
    
    # Kill children recursively
    for CHILD_PID in $CHILDREN; do
        if [ -n "$CHILD_PID" ]; then
            kill_process_tree "$CHILD_PID" "$SERVICE_NAME child"
        fi
    done
    
    # Now kill the parent
    if kill -0 $PID 2>/dev/null; then
        # Try graceful termination first
        kill -TERM $PID 2>/dev/null
        
        # Wait a moment for graceful shutdown
        sleep 0.5
        
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null
        fi
        
        echo -e "${GREEN}  [OK] Stopped $SERVICE_NAME (PID: $PID)${NC}"
        return 0
    fi
    
    return 1
}

# Function to kill processes on a specific port
kill_processes_on_port() {
    local PORT=$1
    local KILLED=false
    
    if command -v lsof &> /dev/null; then
        local PIDS=$(lsof -ti:$PORT 2>/dev/null)
        if [ -n "$PIDS" ]; then
            for PID in $PIDS; do
                if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                    local PROC_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "process")
                    kill_process_tree "$PID" "$PROC_NAME on port $PORT"
                    KILLED=true
                fi
            done
        fi
    elif command -v ss &> /dev/null; then
        local PIDS=$(ss -tlnp 2>/dev/null | grep ":$PORT " | sed -n 's/.*pid=\([0-9]*\).*/\1/p')
        if [ -n "$PIDS" ]; then
            for PID in $PIDS; do
                if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                    local PROC_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "process")
                    kill_process_tree "$PID" "$PROC_NAME on port $PORT"
                    KILLED=true
                fi
            done
        fi
    elif command -v netstat &> /dev/null; then
        local PIDS=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
        if [ -n "$PIDS" ]; then
            for PID in $PIDS; do
                if [ "$PID" != "-" ] && [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                    local PROC_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "process")
                    kill_process_tree "$PID" "$PROC_NAME on port $PORT"
                    KILLED=true
                fi
            done
        fi
    fi
    
    if [ "$KILLED" = true ]; then
        return 0
    fi
    return 1
}

# Stop Theia
if [ -f ".theia.pid" ]; then
    PID=$(cat .theia.pid 2>/dev/null)
    if [ -n "$PID" ] && kill_process_tree "$PID" "Theia"; then
        STOPPED=true
    fi
    rm -f .theia.pid
fi

# Stop Backend (uvicorn spawns multiple workers)
if [ -f ".backend.pid" ]; then
    PID=$(cat .backend.pid 2>/dev/null)
    if [ -n "$PID" ] && kill_process_tree "$PID" "Backend"; then
        STOPPED=true
    fi
    rm -f .backend.pid
fi

# Stop MLFlow
if [ -f ".mlflow.pid" ]; then
    PID=$(cat .mlflow.pid 2>/dev/null)
    if [ -n "$PID" ] && kill_process_tree "$PID" "MLFlow"; then
        STOPPED=true
    fi
    rm -f .mlflow.pid
fi

# Stop Web UI (npm spawns node child processes)
if [ -f ".webui.pid" ]; then
    PID=$(cat .webui.pid 2>/dev/null)
    if [ -n "$PID" ] && kill_process_tree "$PID" "Web UI"; then
        STOPPED=true
    fi
    rm -f .webui.pid
fi

# Stop JupyterLab
if [ -f ".jupyter.pid" ]; then
    PID=$(cat .jupyter.pid 2>/dev/null)
    if [ -n "$PID" ] && kill_process_tree "$PID" "JupyterLab"; then
        STOPPED=true
    fi
    rm -f .jupyter.pid
fi

# Always check ports to catch orphaned processes
echo ""
echo -e "${YELLOW}  Checking for processes on development ports...${NC}"

for PORT in 3000 5000 8080 8888; do
    if kill_processes_on_port $PORT; then
        STOPPED=true
    fi
done

# Additional cleanup in force mode
if [ "$FORCE" = true ]; then
    echo ""
    echo -e "${YELLOW}  Force mode: Looking for related processes...${NC}"
    
    # Kill any uvicorn processes related to our project
    if command -v pgrep &> /dev/null; then
        for PID in $(pgrep -f "uvicorn.*agentic_assistants" 2>/dev/null); do
            if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                kill_process_tree "$PID" "uvicorn (agentic_assistants)"
                STOPPED=true
            fi
        done
        
        # Kill any node processes related to webui
        for PID in $(pgrep -f "node.*webui" 2>/dev/null); do
            if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                kill_process_tree "$PID" "node (webui)"
                STOPPED=true
            fi
        done
        
        for PID in $(pgrep -f "next-server" 2>/dev/null); do
            if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                kill_process_tree "$PID" "next-server"
                STOPPED=true
            fi
        done
        
        # Kill any mlflow server processes
        for PID in $(pgrep -f "mlflow.*server" 2>/dev/null); do
            if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                kill_process_tree "$PID" "mlflow server"
                STOPPED=true
            fi
        done
        
        # Kill any jupyter processes
        for PID in $(pgrep -f "jupyter-lab" 2>/dev/null); do
            if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
                kill_process_tree "$PID" "jupyter-lab"
                STOPPED=true
            fi
        done
    fi
fi

echo ""
if [ "$STOPPED" = true ]; then
    echo -e "${GREEN}All development services stopped.${NC}"
else
    echo -e "${YELLOW}No running services found.${NC}"
fi
echo ""
echo -e "${GRAY}Tip: Use --force flag to also kill orphaned node/python processes.${NC}"
echo ""
