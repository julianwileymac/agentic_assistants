# =============================================================================
# Agentic Assistants - Enhanced Startup Script (Windows PowerShell)
# =============================================================================
# This script handles virtual environment activation, dependency installation,
# and starts the required services for the Agentic Assistants framework.
#
# Usage:
#   .\scripts\start-enhanced.ps1              # Full startup with env check
#   .\scripts\start-enhanced.ps1 -SkipDeps    # Skip dependency installation
#   .\scripts\start-enhanced.ps1 -Full        # Start all services via Docker
#   .\scripts\start-enhanced.ps1 -Help        # Show help
# =============================================================================

param(
    [switch]$Full,
    [switch]$Ollama,
    [switch]$MLFlow,
    [switch]$NoOllama,
    [switch]$NoMLFlow,
    [switch]$SkipDeps,
    [switch]$SkipEnvCheck,
    [switch]$Help
)

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

function Write-Banner {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "           AGENTIC ASSISTANTS FRAMEWORK                        " -ForegroundColor Cyan
    Write-Host "     Multi-Agent Experimentation & MLOps Platform              " -ForegroundColor Cyan
    Write-Host "                 Enhanced Startup v2.0                         " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Usage {
    Write-Host "Usage: .\scripts\start-enhanced.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Full          Start all services via Docker Compose"
    Write-Host "  -Ollama        Start only Ollama"
    Write-Host "  -MLFlow        Start only MLFlow"
    Write-Host "  -NoOllama      Don't start Ollama"
    Write-Host "  -NoMLFlow      Don't start MLFlow"
    Write-Host "  -SkipDeps      Skip dependency installation check"
    Write-Host "  -SkipEnvCheck  Skip virtual environment activation"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
}

function Write-Section($title) {
    Write-Host ""
    Write-Host "=== $title ===" -ForegroundColor Yellow
}

function Write-Step($message) {
    Write-Host "  -> $message" -ForegroundColor White
}

function Write-Success($message) {
    Write-Host "  [OK] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "  [WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "  [ERROR] $message" -ForegroundColor Red
}

function Test-VirtualEnvironment {
    # Check for Poetry virtual environment
    try {
        $poetryEnv = & poetry env info --path 2>$null
        if ($poetryEnv -and (Test-Path $poetryEnv)) {
            return @{Type = "Poetry"; Path = $poetryEnv}
        }
    } catch {}
    
    # Check for py11_venv
    $py11VenvPath = Join-Path $ProjectDir "py11_venv"
    if (Test-Path $py11VenvPath) {
        return @{Type = "Manual"; Path = $py11VenvPath}
    }
    
    # Check if we're already in a virtual environment
    if ($env:VIRTUAL_ENV) {
        return @{Type = "Active"; Path = $env:VIRTUAL_ENV}
    }
    
    return $null
}

function Activate-VirtualEnvironment($venvInfo) {
    if (-not $venvInfo) { return $false }
    
    switch ($venvInfo.Type) {
        "Poetry" {
            Write-Step "Using Poetry virtual environment..."
            try {
                # For Poetry, we'll use poetry shell or run commands through poetry
                $env:VIRTUAL_ENV = $venvInfo.Path
                Write-Success "Poetry environment detected at $($venvInfo.Path)"
                return $true
            } catch {
                Write-Warning "Failed to activate Poetry environment"
                return $false
            }
        }
        "Manual" {
            Write-Step "Activating manual virtual environment..."
            $activateScript = Join-Path $venvInfo.Path "Scripts\Activate.ps1"
            if (Test-Path $activateScript) {
                try {
                    & $activateScript
                    Write-Success "Activated virtual environment at $($venvInfo.Path)"
                    return $true
                } catch {
                    Write-Warning "Failed to activate virtual environment: $_"
                    return $false
                }
            } else {
                Write-Warning "Activation script not found at $activateScript"
                return $false
            }
        }
        "Active" {
            Write-Success "Already in virtual environment: $($venvInfo.Path)"
            return $true
        }
    }
    return $false
}

function Test-Dependencies {
    Write-Step "Checking Python dependencies..."
    
    # Check if we can import key packages
    $packages = @("agentic_assistants", "mlflow", "langchain", "crewai")
    $missingPackages = @()
    
    foreach ($package in $packages) {
        try {
            $result = python -c "import $package" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        } catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -eq 0) {
        Write-Success "All required packages are installed"
        return $true
    } else {
        Write-Warning "Missing packages: $($missingPackages -join ', ')"
        return $false
    }
}

function Install-Dependencies {
    Write-Step "Installing dependencies..."
    
    # Check if poetry.lock exists
    $lockFile = Join-Path $ProjectDir "poetry.lock"
    if (Test-Path $lockFile) {
        Write-Step "Found poetry.lock, using Poetry for installation..."
        try {
            poetry install
            Write-Success "Dependencies installed via Poetry"
            return $true
        } catch {
            Write-Warning "Poetry install failed, trying pip fallback..."
        }
    }
    
    # Fallback to pip install if pyproject.toml exists
    $pyprojectFile = Join-Path $ProjectDir "pyproject.toml"
    if (Test-Path $pyprojectFile) {
        Write-Step "Installing project in development mode..."
        try {
            python -m pip install -e .
            Write-Success "Project installed in development mode"
            return $true
        } catch {
            Write-Error "Failed to install dependencies"
            return $false
        }
    }
    
    Write-Error "No pyproject.toml found for dependency installation"
    return $false
}

function Write-QuickStartGuide {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Magenta
    Write-Host "                    QUICK START GUIDE                          " -ForegroundColor Magenta
    Write-Host "================================================================" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Host "AVAILABLE COMMANDS:" -ForegroundColor Cyan
    Write-Host "  agentic --help                 # Show all available commands"
    Write-Host "  agentic ollama pull llama3.2   # Download a language model"
    Write-Host "  agentic config show             # Show current configuration"
    Write-Host "  agentic run <script.py>         # Run a Python script with the framework"
    Write-Host ""
    
    Write-Host "EXAMPLE SCRIPTS:" -ForegroundColor Cyan
    Write-Host "  .\examples\simple_ollama_chat.py      # Basic Ollama chat example"
    Write-Host "  .\examples\crewai_research_team.py     # CrewAI multi-agent example"
    Write-Host "  .\examples\langgraph_workflow.py       # LangGraph workflow example"
    Write-Host "  .\examples\context_loading_demo.py     # Context loading demonstration"
    Write-Host ""
    
    Write-Host "JUPYTER NOTEBOOKS:" -ForegroundColor Cyan
    Write-Host "  jupyter lab                     # Start Jupyter Lab"
    Write-Host "  Open: .\notebooks\01_getting_started.ipynb"
    Write-Host ""
    
    Write-Host "WEB INTERFACES:" -ForegroundColor Cyan
    if ($StartMLFlow -or (-not $NoMLFlow)) {
        Write-Host "  MLFlow UI:    http://localhost:5000    # Experiment tracking"
    }
    Write-Host "  Jaeger UI:    http://localhost:16686   # Distributed tracing (if Docker)"
    Write-Host ""
    
    Write-Host "CONFIGURATION:" -ForegroundColor Cyan
    Write-Host "  1. Copy env.example to .env and customize settings"
    Write-Host "  2. Configure Ollama models: agentic ollama pull <model-name>"
    Write-Host "  3. Set up API keys in .env for external services"
    Write-Host ""
    
    Write-Host "TROUBLESHOOTING:" -ForegroundColor Cyan
    Write-Host "  * Check logs: Get-Content mlflow.log"
    Write-Host "  * Restart services: .\scripts\stop.ps1 && .\scripts\start-enhanced.ps1"
    Write-Host "  * Reinstall deps: poetry install --no-cache"
    Write-Host "  * Check environment: poetry env info"
    Write-Host ""
    
    Write-Host "DOCUMENTATION:" -ForegroundColor Cyan
    Write-Host "  * Architecture: .\docs\architecture.md"
    Write-Host "  * API Reference: .\docs\api_reference.md"
    Write-Host "  * CLI Reference: .\docs\cli_reference.md"
    Write-Host ""
    
    Write-Host "Ready to start experimenting with multi-agent AI!" -ForegroundColor Green
    Write-Host ""
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
Write-Step "Working directory: $ProjectDir"

# Virtual Environment Check and Activation
if (-not $SkipEnvCheck) {
    Write-Section "Virtual Environment Setup"
    
    $venvInfo = Test-VirtualEnvironment
    if ($venvInfo) {
        $envActivated = Activate-VirtualEnvironment $venvInfo
        if (-not $envActivated) {
            Write-Warning "Continuing without virtual environment activation"
        }
    } else {
        Write-Warning "No virtual environment found. Consider running:"
        Write-Host "  poetry install  # Create and use Poetry environment"
        Write-Host "  # OR"
        Write-Host "  python -m venv venv && .\venv\Scripts\Activate.ps1"
    }
}

# Dependency Check and Installation
if (-not $SkipDeps) {
    Write-Section "Dependency Management"
    
    $depsOk = Test-Dependencies
    if (-not $depsOk) {
        Write-Warning "Some dependencies are missing. Attempting automatic installation..."
        $installSuccess = Install-Dependencies
        if (-not $installSuccess) {
            Write-Error "Failed to install dependencies. Some features may not work."
            Write-Host "Manual installation options:"
            Write-Host "  poetry install    # Recommended"
            Write-Host "  pip install -e .  # Alternative"
        }
    }
}

# Load environment variables if .env exists
Write-Section "Environment Configuration"
if (Test-Path ".env") {
    Write-Step "Loading environment from .env"
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    Write-Success "Environment variables loaded"
} else {
    Write-Warning ".env file not found. Consider copying env.example to .env"
    if (Test-Path "env.example") {
        Write-Host "You can copy env.example to .env manually to get started."
    }
}

# Docker Compose mode
if ($Full) {
    Write-Section "Docker Services"
    Write-Step "Starting services via Docker Compose..."
    
    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if (-not $dockerCompose) {
        Write-Error "docker-compose not found. Please install Docker."
        exit 1
    }
    
    docker-compose up -d
    
    Write-Success "Docker services started"
    Write-Host ""
    Write-Host "Services:"
    Write-Host "  - MLFlow:  http://localhost:5000"
    Write-Host "  - Jaeger:  http://localhost:16686"
    Write-Host ""
    Write-Host "To view logs: docker-compose logs -f"
    Write-Host "To stop:      .\scripts\stop.ps1"
    
    Write-QuickStartGuide
    exit 0
}

# Service Startup
Write-Section "Service Management"

# Start Ollama
if ($StartOllama) {
    Write-Step "Starting Ollama..."
    
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaCmd) {
        # Check if already running
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
            Write-Success "Ollama is already running"
        }
        catch {
            # Start Ollama
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
            
            Write-Host "  Waiting for Ollama to start" -NoNewline
            for ($i = 0; $i -lt 30; $i++) {
                try {
                    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -ErrorAction SilentlyContinue
                    Write-Host ""
                    Write-Success "Ollama started successfully"
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
        Write-Error "Ollama not found. Install from https://ollama.ai"
    }
}

# Start MLFlow
if ($StartMLFlow) {
    Write-Step "Starting MLFlow..."
    
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
            Write-Success "MLFlow is already running"
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
                    Write-Success "MLFlow started successfully"
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
        Write-Error "MLFlow not installed. Run: poetry install"
    }
}

Write-Section "Startup Complete"
Write-Success "All services are ready!"

Write-QuickStartGuide