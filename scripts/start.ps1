# =============================================================================
# Agentic Assistants - Startup Script (Windows PowerShell)
# =============================================================================
# This script starts the required services for the Agentic Assistants framework.
#
# Usage:
#   .\scripts\start.ps1              # Start Ollama and MLFlow locally
#   .\scripts\start.ps1 -Full        # Start all services via Docker
#   .\scripts\start.ps1 -Ollama      # Start only Ollama
#   .\scripts\start.ps1 -MLFlow      # Start only MLFlow
# =============================================================================

param(
    [switch]$Full,
    [switch]$Ollama,
    [switch]$MLFlow,
    [switch]$NoOllama,
    [switch]$NoMLFlow,
    [switch]$Help
)

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

function Write-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║           🤖 Agentic Assistants Framework                 ║" -ForegroundColor Blue
    Write-Host "║     Multi-Agent Experimentation & MLOps Platform          ║" -ForegroundColor Blue
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Usage {
    Write-Host "Usage: .\scripts\start.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Full          Start all services via Docker Compose"
    Write-Host "  -Ollama        Start only Ollama"
    Write-Host "  -MLFlow        Start only MLFlow"
    Write-Host "  -NoOllama      Don't start Ollama"
    Write-Host "  -NoMLFlow      Don't start MLFlow"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\start.ps1              # Start Ollama and MLFlow"
    Write-Host "  .\scripts\start.ps1 -Full        # Start via Docker"
    Write-Host "  .\scripts\start.ps1 -Ollama      # Start only Ollama"
}

if ($Help) {
    Write-Usage
    exit 0
}

# Determine what to start
$StartOllama = $true
$StartMLFlow = $true

if ($Ollama) {
    $StartOllama = $true
    $StartMLFlow = $false
}

if ($MLFlow) {
    $StartOllama = $false
    $StartMLFlow = $true
}

if ($NoOllama) { $StartOllama = $false }
if ($NoMLFlow) { $StartMLFlow = $false }

Write-Banner

# Change to project directory
Set-Location $ProjectDir

# Load environment variables if .env exists
if (Test-Path ".env") {
    Write-Host "Loading environment from .env" -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Docker Compose mode
if ($Full) {
    Write-Host "Starting services via Docker Compose..." -ForegroundColor Yellow
    
    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if (-not $dockerCompose) {
        Write-Host "Error: docker-compose not found. Please install Docker." -ForegroundColor Red
        exit 1
    }
    
    docker-compose up -d
    
    Write-Host "✓ Docker services started" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services:"
    Write-Host "  - MLFlow:  http://localhost:5000"
    Write-Host "  - Jaeger:  http://localhost:16686"
    Write-Host ""
    Write-Host "To view logs: docker-compose logs -f"
    Write-Host "To stop:      .\scripts\stop.ps1 -Docker"
    exit 0
}

# Start Ollama
if ($StartOllama) {
    Write-Host "Starting Ollama..." -ForegroundColor Yellow
    
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaCmd) {
        # Check if already running
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
            Write-Host "  ✓ Ollama is already running" -ForegroundColor Green
        }
        catch {
            # Start Ollama
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
            
            Write-Host "  Waiting for Ollama to start" -NoNewline
            for ($i = 0; $i -lt 30; $i++) {
                try {
                    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -ErrorAction SilentlyContinue
                    Write-Host ""
                    Write-Host "  ✓ Ollama started" -ForegroundColor Green
                    break
                }
                catch {
                    Write-Host "." -NoNewline
                    Start-Sleep -Seconds 1
                }
            }
        }
    }
    else {
        Write-Host "  ✗ Ollama not found. Install from https://ollama.ai" -ForegroundColor Red
    }
}

# Start MLFlow
if ($StartMLFlow) {
    Write-Host "Starting MLFlow..." -ForegroundColor Yellow
    
    # Check if MLFlow is installed
    try {
        python -c "import mlflow" 2>$null
        $mlflowInstalled = $true
    }
    catch {
        $mlflowInstalled = $false
    }
    
    if ($mlflowInstalled) {
        # Check if already running
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
            Write-Host "  ✓ MLFlow is already running" -ForegroundColor Green
        }
        catch {
            # Create mlruns directory
            if (-not (Test-Path "mlruns")) {
                New-Item -ItemType Directory -Path "mlruns" | Out-Null
            }
            
            # Start MLFlow
            $mlflowProcess = Start-Process -FilePath "mlflow" -ArgumentList "server", "--host", "127.0.0.1", "--port", "5000", "--backend-store-uri", "./mlruns" -WindowStyle Hidden -PassThru
            
            # Save PID
            $mlflowProcess.Id | Out-File ".mlflow.pid"
            
            Write-Host "  Waiting for MLFlow to start" -NoNewline
            for ($i = 0; $i -lt 15; $i++) {
                try {
                    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
                    Write-Host ""
                    Write-Host "  ✓ MLFlow started" -ForegroundColor Green
                    break
                }
                catch {
                    Write-Host "." -NoNewline
                    Start-Sleep -Seconds 1
                }
            }
        }
    }
    else {
        Write-Host "  ✗ MLFlow not installed. Run: poetry install" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Startup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start:"
Write-Host "  agentic ollama pull llama3.2   # Pull a model"
Write-Host "  agentic run examples/simple_ollama_chat.py"
Write-Host ""
Write-Host "To stop services: .\scripts\stop.ps1"

