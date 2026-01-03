#!/bin/bash
# =============================================================================
# Agentic Assistants - Startup Script (Unix/Linux/macOS)
# =============================================================================
# This script starts the required services for the Agentic Assistants framework.
#
# Usage:
#   ./scripts/start.sh              # Start Ollama and MLFlow locally
#   ./scripts/start.sh --full       # Start all services via Docker
#   ./scripts/start.sh --ollama     # Start only Ollama
#   ./scripts/start.sh --mlflow     # Start only MLFlow
#   ./scripts/start.sh --help       # Show help
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
START_OLLAMA=true
START_MLFLOW=true
USE_DOCKER=false

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           🤖 Agentic Assistants Framework                 ║"
    echo "║     Multi-Agent Experimentation & MLOps Platform          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print usage
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --full          Start all services via Docker Compose"
    echo "  --ollama        Start only Ollama"
    echo "  --mlflow        Start only MLFlow"
    echo "  --no-ollama     Don't start Ollama"
    echo "  --no-mlflow     Don't start MLFlow"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start Ollama and MLFlow locally"
    echo "  $0 --full       # Start all services via Docker"
    echo "  $0 --ollama     # Start only Ollama"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            USE_DOCKER=true
            shift
            ;;
        --ollama)
            START_OLLAMA=true
            START_MLFLOW=false
            shift
            ;;
        --mlflow)
            START_OLLAMA=false
            START_MLFLOW=true
            shift
            ;;
        --no-ollama)
            START_OLLAMA=false
            shift
            ;;
        --no-mlflow)
            START_MLFLOW=false
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

print_banner

# Change to project directory
cd "$PROJECT_DIR"

# Load environment variables if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment from .env${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Docker Compose mode
if [ "$USE_DOCKER" = true ]; then
    echo -e "${YELLOW}Starting services via Docker Compose...${NC}"
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: docker-compose not found. Please install Docker.${NC}"
        exit 1
    fi
    
    docker-compose up -d
    
    echo -e "${GREEN}✓ Docker services started${NC}"
    echo ""
    echo "Services:"
    echo "  - MLFlow:  http://localhost:5000"
    echo "  - Jaeger:  http://localhost:16686"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop:      ./scripts/stop.sh --docker"
    exit 0
fi

# Start Ollama
if [ "$START_OLLAMA" = true ]; then
    echo -e "${YELLOW}Starting Ollama...${NC}"
    
    if command -v ollama &> /dev/null; then
        # Check if already running
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Ollama is already running${NC}"
        else
            # Start Ollama serve in background
            nohup ollama serve > /dev/null 2>&1 &
            
            # Wait for Ollama to be ready
            echo -n "  Waiting for Ollama to start"
            for i in {1..30}; do
                if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                    echo ""
                    echo -e "  ${GREEN}✓ Ollama started${NC}"
                    break
                fi
                echo -n "."
                sleep 1
            done
            
            if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo ""
                echo -e "  ${RED}✗ Failed to start Ollama${NC}"
            fi
        fi
    else
        echo -e "  ${RED}✗ Ollama not found. Install from https://ollama.ai${NC}"
    fi
fi

# Start MLFlow
if [ "$START_MLFLOW" = true ]; then
    echo -e "${YELLOW}Starting MLFlow...${NC}"
    
    # Check if MLFlow is installed
    if python -c "import mlflow" 2>/dev/null; then
        # Check if already running
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓ MLFlow is already running${NC}"
        else
            # Create mlruns directory if it doesn't exist
            mkdir -p mlruns
            
            # Start MLFlow in background
            nohup mlflow server \
                --host 127.0.0.1 \
                --port 5000 \
                --backend-store-uri ./mlruns \
                > mlflow.log 2>&1 &
            
            echo $! > .mlflow.pid
            
            # Wait for MLFlow to be ready
            echo -n "  Waiting for MLFlow to start"
            for i in {1..15}; do
                if curl -s http://localhost:5000/health > /dev/null 2>&1; then
                    echo ""
                    echo -e "  ${GREEN}✓ MLFlow started${NC}"
                    break
                fi
                echo -n "."
                sleep 1
            done
            
            if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
                echo ""
                echo -e "  ${YELLOW}! MLFlow may still be starting. Check mlflow.log${NC}"
            fi
        fi
    else
        echo -e "  ${RED}✗ MLFlow not installed. Run: poetry install${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Startup complete!${NC}"
echo ""
echo "Quick Start:"
echo "  agentic ollama pull llama3.2   # Pull a model"
echo "  agentic run examples/simple_ollama_chat.py"
echo ""
echo "To stop services: ./scripts/stop.sh"

