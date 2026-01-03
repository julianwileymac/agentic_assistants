#!/bin/bash
# =============================================================================
# Agentic Assistants - Shutdown Script (Unix/Linux/macOS)
# =============================================================================
# This script stops services started by the Agentic Assistants framework.
#
# Usage:
#   ./scripts/stop.sh              # Stop MLFlow (preserves Ollama)
#   ./scripts/stop.sh --all        # Stop all services including Ollama
#   ./scripts/stop.sh --docker     # Stop Docker Compose services
#   ./scripts/stop.sh --help       # Show help
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default options
STOP_OLLAMA=false
STOP_MLFLOW=true
USE_DOCKER=false

# Print usage
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all           Stop all services including Ollama"
    echo "  --docker        Stop Docker Compose services"
    echo "  --ollama        Stop only Ollama"
    echo "  --mlflow        Stop only MLFlow"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Stop MLFlow (preserves Ollama)"
    echo "  $0 --all        # Stop all services"
    echo "  $0 --docker     # Stop Docker services"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            STOP_OLLAMA=true
            STOP_MLFLOW=true
            shift
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --ollama)
            STOP_OLLAMA=true
            STOP_MLFLOW=false
            shift
            ;;
        --mlflow)
            STOP_OLLAMA=false
            STOP_MLFLOW=true
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Stopping Agentic Assistants services...${NC}"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Docker Compose mode
if [ "$USE_DOCKER" = true ]; then
    echo -e "${YELLOW}Stopping Docker Compose services...${NC}"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
        echo -e "${GREEN}✓ Docker services stopped${NC}"
    else
        echo -e "${RED}Error: docker-compose not found${NC}"
    fi
    exit 0
fi

# Stop MLFlow
if [ "$STOP_MLFLOW" = true ]; then
    echo -e "${YELLOW}Stopping MLFlow...${NC}"
    
    if [ -f .mlflow.pid ]; then
        PID=$(cat .mlflow.pid)
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm .mlflow.pid
            echo -e "  ${GREEN}✓ MLFlow stopped (PID: $PID)${NC}"
        else
            rm .mlflow.pid
            echo -e "  ${YELLOW}! MLFlow was not running${NC}"
        fi
    else
        # Try to find and kill MLFlow process
        MLFLOW_PID=$(pgrep -f "mlflow server" || true)
        if [ -n "$MLFLOW_PID" ]; then
            kill "$MLFLOW_PID" 2>/dev/null || true
            echo -e "  ${GREEN}✓ MLFlow stopped (PID: $MLFLOW_PID)${NC}"
        else
            echo -e "  ${YELLOW}! No MLFlow process found${NC}"
        fi
    fi
fi

# Stop Ollama
if [ "$STOP_OLLAMA" = true ]; then
    echo -e "${YELLOW}Stopping Ollama...${NC}"
    
    # Find Ollama serve process
    OLLAMA_PID=$(pgrep -f "ollama serve" || true)
    if [ -n "$OLLAMA_PID" ]; then
        kill "$OLLAMA_PID" 2>/dev/null || true
        echo -e "  ${GREEN}✓ Ollama stopped (PID: $OLLAMA_PID)${NC}"
    else
        echo -e "  ${YELLOW}! No Ollama process found${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Shutdown complete!${NC}"

