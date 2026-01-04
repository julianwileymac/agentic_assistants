#!/usr/bin/env bash
#
# Start JupyterLab with all supporting services (MLFlow, Backend API, OTEL Collector).
#
# This script starts the complete Agentic Assistants development environment:
# - MLFlow tracking server (port 5000)
# - Backend API server (port 8080)
# - OpenTelemetry collector (optional, port 4317)
# - JupyterLab IDE (port 3000)
#
# Usage:
#   ./start-lab.sh                    # Start all services
#   ./start-lab.sh --skip-mlflow      # Skip MLFlow
#   ./start-lab.sh --skip-backend     # Skip Backend API
#   ./start-lab.sh --skip-otel        # Skip OTEL Collector
#   ./start-lab.sh --port 8888        # Custom JupyterLab port
#

set -euo pipefail

# Configuration
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${LAB_PYTHON:-python}"
VENV="${ROOT_DIR}/.venv-lab"
JUPYTERLAB_PORT=3000
SKIP_MLFLOW=false
SKIP_BACKEND=false
SKIP_OTEL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-mlflow)
            SKIP_MLFLOW=true
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-otel)
            SKIP_OTEL=true
            shift
            ;;
        --port)
            JUPYTERLAB_PORT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_status() { echo -e "${CYAN}[*]${NC} $1"; }
log_success() { echo -e "${GREEN}[+]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[-]${NC} $1"; }

# Track background processes for cleanup
PIDS=()

cleanup() {
    log_status "Stopping background services..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    
    # Kill any remaining processes by name
    pkill -f "mlflow server" 2>/dev/null || true
    pkill -f "uvicorn agentic_assistants" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   Agentic Assistants - JupyterLab Environment  ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Check Python version
log_status "Checking Python version..."
PY_VERSION="$(${PY_BIN} - <<'EOF'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
EOF
)"

major="${PY_VERSION%%.*}"
minor="${PY_VERSION#*.}"
if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 13 ]; }; then
    log_error "Python ${PY_VERSION} detected. Please use Python 3.10–3.12 (set LAB_PYTHON to an appropriate interpreter)."
    exit 1
fi
log_success "Python ${PY_VERSION} detected"

# Create/update virtual environment
log_status "Setting up virtual environment..."
if [ ! -d "${VENV}" ]; then
    "${PY_BIN}" -m venv "${VENV}"
    "${VENV}/bin/pip" install --upgrade pip -q
    log_success "Created virtual environment"
else
    log_success "Virtual environment exists"
fi

# Install requirements
log_status "Installing requirements..."
"${VENV}/bin/pip" install -r "${ROOT_DIR}/lab/requirements.txt" -q
log_success "Requirements installed"

# Helper function to check if a port is in use
port_in_use() {
    lsof -i ":$1" >/dev/null 2>&1 || nc -z localhost "$1" 2>/dev/null
}

# Start MLFlow server
if [ "$SKIP_MLFLOW" = false ]; then
    log_status "Starting MLFlow server on port 5000..."
    
    if port_in_use 5000; then
        log_success "MLFlow already running on port 5000"
    else
        mkdir -p "${ROOT_DIR}/mlruns/artifacts"
        
        "${VENV}/bin/mlflow" server \
            --host 127.0.0.1 \
            --port 5000 \
            --backend-store-uri "sqlite:///${ROOT_DIR}/mlruns/mlflow.db" \
            --default-artifact-root "${ROOT_DIR}/mlruns/artifacts" \
            > "${ROOT_DIR}/mlflow.log" 2>&1 &
        MLFLOW_PID=$!
        PIDS+=("$MLFLOW_PID")
        
        # Wait for MLFlow to start
        for i in {1..10}; do
            if port_in_use 5000; then
                log_success "MLFlow server started (PID: $MLFLOW_PID)"
                break
            fi
            sleep 1
        done
        
        if ! port_in_use 5000; then
            log_warning "MLFlow may not have started. Check ${ROOT_DIR}/mlflow.log for details."
        fi
    fi
fi

# Start Backend API server
if [ "$SKIP_BACKEND" = false ]; then
    log_status "Starting Backend API server on port 8080..."
    
    if port_in_use 8080; then
        log_success "Backend API already running on port 8080"
    else
        PYTHONPATH="${ROOT_DIR}/src" "${VENV}/bin/python" -m uvicorn \
            agentic_assistants.server.app:create_app \
            --factory \
            --host 127.0.0.1 \
            --port 8080 \
            > "${ROOT_DIR}/backend.log" 2>&1 &
        BACKEND_PID=$!
        PIDS+=("$BACKEND_PID")
        
        # Wait for backend to start
        for i in {1..10}; do
            if port_in_use 8080; then
                log_success "Backend API server started (PID: $BACKEND_PID)"
                break
            fi
            sleep 1
        done
        
        if ! port_in_use 8080; then
            log_warning "Backend API may not have started. Check ${ROOT_DIR}/backend.log for details."
        fi
    fi
fi

# Check for OTEL Collector (optional - uses Docker)
if [ "$SKIP_OTEL" = false ]; then
    log_status "Checking OpenTelemetry Collector..."
    
    if port_in_use 4317; then
        log_success "OTEL Collector running on port 4317"
    else
        # Check if Docker is available
        if command -v docker &> /dev/null; then
            log_status "Starting OTEL Collector via Docker..."
            
            docker run -d --name agentic-otel-collector \
                -p 4317:4317 -p 4318:4318 -p 8888:8888 \
                -v "${ROOT_DIR}/docker/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml:ro" \
                otel/opentelemetry-collector-contrib:0.91.0 \
                --config=/etc/otelcol-contrib/config.yaml 2>/dev/null && \
                log_success "OTEL Collector started via Docker" || \
                log_warning "Could not start OTEL Collector. Tracing will be disabled."
        else
            log_warning "Docker not available. OTEL Collector not started. Tracing will be disabled."
            log_warning "To enable tracing, install Docker and run: docker-compose up -d otel-collector jaeger"
        fi
    fi
fi

# Set environment variables
export MLFLOW_TRACKING_URI="http://localhost:5000"
export AGENTIC_BACKEND_URL="http://localhost:8080"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   Services Status                              ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "  MLFlow:      http://localhost:5000"
echo -e "  Backend API: http://localhost:8080"
echo -e "  OTEL:        http://localhost:4317 (gRPC)"
echo -e "  JupyterLab:  ${CYAN}http://localhost:${JUPYTERLAB_PORT}${NC}"
echo ""
echo -e "${GREEN}================================================${NC}"
echo ""

# Start JupyterLab
log_status "Starting JupyterLab on port ${JUPYTERLAB_PORT}..."
exec "${VENV}/bin/jupyter" lab \
    --config="${ROOT_DIR}/lab/jupyter_lab_config.py" \
    --port="${JUPYTERLAB_PORT}"
