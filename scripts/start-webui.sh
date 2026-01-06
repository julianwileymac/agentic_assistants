#!/bin/bash
# =============================================================================
# Agentic Assistants - Web UI Startup Script (Unix/Linux/macOS)
# =============================================================================
# This script starts the Next.js web control panel.
#
# Usage:
#   ./scripts/start-webui.sh              # Start web UI on port 3000
#   ./scripts/start-webui.sh --port 3001  # Start on custom port
#   ./scripts/start-webui.sh --dev        # Start in development mode
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
WEBUI_DIR="$PROJECT_DIR/webui"

# Default options
PORT=3000
DEV_MODE=false

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           🎛️  Agentic Control Panel                       ║"
    echo "║              Web UI Startup Script                        ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print usage
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --port PORT     Port to run the web UI on (default: 3000)"
    echo "  --dev           Run in development mode with hot reload"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start on port 3000"
    echo "  $0 --port 3001  # Start on port 3001"
    echo "  $0 --dev        # Start in dev mode"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --dev)
            DEV_MODE=true
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

# Check if webui directory exists
if [ ! -d "$WEBUI_DIR" ]; then
    echo -e "${RED}Error: Web UI directory not found at $WEBUI_DIR${NC}"
    echo "Please ensure the webui has been set up."
    exit 1
fi

cd "$WEBUI_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Start the web UI
if [ "$DEV_MODE" = true ]; then
    echo -e "${GREEN}Starting Web UI in development mode on port $PORT...${NC}"
    PORT=$PORT npm run dev &
else
    echo -e "${YELLOW}Building Web UI for production...${NC}"
    npm run build
    echo -e "${GREEN}Starting Web UI on port $PORT...${NC}"
    PORT=$PORT npm run start &
fi

WEBUI_PID=$!
echo $WEBUI_PID > "$PROJECT_DIR/.webui.pid"

# Wait for the server to start
echo -n "  Waiting for Web UI to start"
for i in {1..30}; do
    if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Web UI started successfully${NC}"
        echo ""
        echo "Access the control panel at: http://localhost:$PORT"
        echo ""
        echo "To stop: kill $WEBUI_PID or ./scripts/stop-webui.sh"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${YELLOW}Web UI is starting... Check http://localhost:$PORT${NC}"

