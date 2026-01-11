# Chunk: d4af9ba97ac0_0

- source: `scripts/start-dev.ps1`
- lines: 1-85
- chunk: 1/8

```
# =============================================================================
# Agentic Assistants - Development Startup Script (Windows PowerShell)
# =============================================================================
# This script starts all services for development:
#   1. Python backend (FastAPI + WebSocket on port 8080)
#   2. UI frontend (Web UI default, port 3000) or JupyterLab / Theia
#   3. MLFlow server (port 5000)
#   4. Opens browser to chosen UI
#
# Usage:
#   .\scripts\start-dev.ps1              # Start all services
#   .\scripts\start-dev.ps1 -BackendOnly   # Start only Python backend
#   .\scripts\start-dev.ps1 -FrontendOnly  # Start only UI
#   .\scripts\start-dev.ps1 -UIChoice webui|jupyterlab|theia|none # Choose UI
#   .\scripts\start-dev.ps1 -NoBrowser     # Don't open browser
# =============================================================================

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$Help,
    [string]$UIChoice = "webui",
    [int]$WebUIPort = 3000,
    [int]$JupyterPort = 8888
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectDir "frontend"
$script:SkipTheia = $false

function Write-Banner {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "       AGENTIC ASSISTANTS - DEVELOPMENT ENVIRONMENT           " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Yellow
}

function Write-Step {
    param([string]$Message)
    Write-Host "  -> $Message" -ForegroundColor Gray
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host "Usage: .\scripts\start-dev.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -BackendOnly   Start only the Python backend"
    Write-Host "  -FrontendOnly  Start only the UI frontend"
    Write-Host "  -UIChoice      webui (default) | jupyterlab | theia | none"
    Write-Host "  -NoBrowser     Don't open browser after startup"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Services:"
    Write-Host "  Python Backend:  http://localhost:8080"
    Write-Host "  Web UI:          http://localhost:3000 (default UI)"
    Write-Host "  MLFlow:          http://localhost:5000"
    Write-Host ""
}

function Start-PythonBackend {
    Write-Section "Starting Python Backend"
    
    Set-Location $ProjectDir
    
    # Check for virtual environment
```
