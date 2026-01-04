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
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}Stopping development services...${NC}"
echo ""

STOPPED=false

# Stop Theia
if [ -f ".theia.pid" ]; then
    PID=$(cat .theia.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
        echo -e "${GREEN}  [OK] Stopped Theia (PID: $PID)${NC}"
        STOPPED=true
    fi
    rm -f .theia.pid
fi

# Stop Backend
if [ -f ".backend.pid" ]; then
    PID=$(cat .backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
        echo -e "${GREEN}  [OK] Stopped Backend (PID: $PID)${NC}"
        STOPPED=true
    fi
    rm -f .backend.pid
fi

# Stop MLFlow
if [ -f ".mlflow.pid" ]; then
    PID=$(cat .mlflow.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
        echo -e "${GREEN}  [OK] Stopped MLFlow (PID: $PID)${NC}"
        STOPPED=true
    fi
    rm -f .mlflow.pid
fi

# Kill any remaining processes on our ports (if Force flag or if PIDs didn't work)
if [ "$FORCE" = true ] || [ "$STOPPED" = false ]; then
    echo ""
    echo -e "${YELLOW}  Checking for processes on development ports...${NC}"
    
    for PORT in 3000 5000 8080; do
        if command -v lsof &> /dev/null; then
            PIDS=$(lsof -ti:$PORT 2>/dev/null)
            if [ -n "$PIDS" ]; then
                for PID in $PIDS; do
                    kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
                    echo -e "${GREEN}  [OK] Stopped process on port $PORT (PID: $PID)${NC}"
                    STOPPED=true
                done
            fi
        elif command -v netstat &> /dev/null; then
            PIDS=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
            if [ -n "$PIDS" ]; then
                for PID in $PIDS; do
                    if [ "$PID" != "-" ] && [ -n "$PID" ]; then
                        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
                        echo -e "${GREEN}  [OK] Stopped process on port $PORT (PID: $PID)${NC}"
                        STOPPED=true
                    fi
                done
            fi
        fi
    done
fi

echo ""
if [ "$STOPPED" = true ]; then
    echo -e "${GREEN}All development services stopped.${NC}"
else
    echo -e "${YELLOW}No running services found.${NC}"
fi
echo ""


