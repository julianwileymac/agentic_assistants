# =============================================================================
# Agentic Assistants - Development Startup Script (Windows PowerShell)
# =============================================================================
# This script starts all services for development:
#   1. Python backend (FastAPI + WebSocket on port 8080)
#   2. Theia frontend (port 3000)
#   3. MLFlow server (port 5000)
#   4. Opens browser to Theia UI
#
# Usage:
#   .\scripts\start-dev.ps1              # Start all services
#   .\scripts\start-dev.ps1 -BackendOnly # Start only Python backend
#   .\scripts\start-dev.ps1 -FrontendOnly # Start only Theia frontend
#   .\scripts\start-dev.ps1 -NoBrowser   # Don't open browser
# =============================================================================

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectDir "frontend"

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
    Write-Host "  -FrontendOnly  Start only the Theia frontend"
    Write-Host "  -NoBrowser     Don't open browser after startup"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Services:"
    Write-Host "  Python Backend:  http://localhost:8080"
    Write-Host "  Theia IDE:       http://localhost:3000"
    Write-Host "  MLFlow:          http://localhost:5000"
    Write-Host ""
}

function Start-PythonBackend {
    Write-Section "Starting Python Backend"
    
    Set-Location $ProjectDir
    
    # Check for virtual environment
    $venvPath = Join-Path $ProjectDir "py11_venv"
    $poetryVenv = $null
    
    try {
        $poetryVenv = & poetry env info --path 2>$null
    } catch {}
    
    if ($poetryVenv -and (Test-Path $poetryVenv)) {
        Write-Step "Using Poetry virtual environment"
        $env:VIRTUAL_ENV = $poetryVenv
        $env:Path = "$poetryVenv\Scripts;$env:Path"
    } elseif (Test-Path $venvPath) {
        Write-Step "Using manual virtual environment"
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
        }
    } else {
        Write-Step "No virtual environment found, using system Python"
    }
    
    # Check if agentic_assistants package is installed
    $packageCheck = python -c "import agentic_assistants" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "agentic_assistants package not installed"
        Write-Step "Installing package..."
        
        if ((Test-Path "pyproject.toml") -and (Get-Command poetry -ErrorAction SilentlyContinue)) {
            & poetry install --no-root 2>&1 | Select-Object -Last 5
            & poetry install 2>&1 | Select-Object -Last 5
        } else {
            & pip install -e . 2>&1 | Select-Object -Last 5
        }
        
        # Check again
        $packageCheck = python -c "import agentic_assistants" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install package. Try manually: poetry install or pip install -e ."
            Write-Error "Error: $packageCheck"
            return $false
        }
        Write-Success "Package installed"
    }
    
    # Create mlruns directory if it doesn't exist
    if (-not (Test-Path "mlruns")) {
        New-Item -ItemType Directory -Path "mlruns" | Out-Null
    }
    
    # Start MLFlow
    Write-Step "Starting MLFlow server..."
    $mlflowLogFile = Join-Path $ProjectDir "mlflow.log"
    $mlflowProcess = Start-Process -FilePath "mlflow" -ArgumentList "server", "--host", "127.0.0.1", "--port", "5000", "--backend-store-uri", "./mlruns" -RedirectStandardOutput $mlflowLogFile -RedirectStandardError "$mlflowLogFile.err" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    if ($mlflowProcess) {
        $mlflowProcess.Id | Out-File ".mlflow.pid"
        Write-Success "MLFlow started on port 5000 (PID: $($mlflowProcess.Id))"
    } else {
        Write-Warning "MLFlow may not have started"
    }
    
    # Start FastAPI backend
    Write-Step "Starting FastAPI backend..."
    $backendLogFile = Join-Path $ProjectDir "backend.log"
    $backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "agentic_assistants.server.rest:create_rest_app", "--factory", "--host", "127.0.0.1", "--port", "8080", "--reload" -RedirectStandardOutput $backendLogFile -RedirectStandardError "$backendLogFile.err" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    if ($backendProcess) {
        $backendProcess.Id | Out-File ".backend.pid"
        Write-Success "Backend started on port 8080 (PID: $($backendProcess.Id))"
    } else {
        Write-Error "Failed to start backend process"
        return $false
    }
    
    # Wait for backend to be ready
    Write-Host "  Waiting for backend" -NoNewline
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 1
        
        # Check if process is still running
        if (-not (Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Error "Backend process died. Check backend.log for errors."
            if (Test-Path $backendLogFile) {
                Write-Host "Last 10 lines of backend.log:" -ForegroundColor Yellow
                Get-Content $backendLogFile -Tail 10 | ForEach-Object { Write-Host "  $_" }
            }
            return $false
        }
        
        # Check if port is listening
        try {
            $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port 8080 -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($connection) {
                Start-Sleep -Seconds 2  # Give it a moment to be fully ready
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 2 -ErrorAction Stop
                    if ($response.StatusCode -eq 200) {
                        Write-Host ""
                        Write-Success "Backend is ready"
                        return $true
                    }
                } catch {}
            }
        } catch {}
        
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Warning "Backend health check timed out, but process is running. Continuing..."
    Write-Host "  Check backend.log if you encounter issues" -ForegroundColor Yellow
    return $true
}

function Start-TheiaFrontend {
    Write-Section "Starting Theia Frontend"
    
    # Check if frontend directory exists
    if (-not (Test-Path $FrontendDir)) {
        Write-Warning "Frontend directory not found. Theia IDE is not set up yet."
        Write-Host "  To set up Theia, run: cd frontend && yarn install && yarn build"
        return $false
    }
    
    Set-Location $FrontendDir
    
    # Check if Node.js is installed
    try {
        $nodeVersion = & node --version
        Write-Step "Node.js version: $nodeVersion"
    } catch {
        Write-Error "Node.js is not installed. Please install Node.js 18 or 20 LTS to use Theia IDE."
        return $false
    }
    
    # Check Node.js version - must be 18.x or 20.x (not 22+ due to native module issues)
    $nodeMajor = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
    if ($nodeMajor -gt 20) {
        Write-Error "Node.js $nodeVersion is too new. Theia requires Node.js 18 or 20 LTS."
        Write-Warning "Please install Node.js 20 LTS:"
        Write-Host "  - Windows: Download from https://nodejs.org/en/download/"
        Write-Host "  - Or use nvm-windows: nvm install 20 && nvm use 20"
        Write-Host ""
        Write-Step "Skipping Theia frontend due to incompatible Node.js version."
        return $false
    } elseif ($nodeMajor -lt 18) {
        Write-Error "Node.js $nodeVersion is too old. Theia requires Node.js 18 or 20 LTS."
        Write-Step "Skipping Theia frontend due to incompatible Node.js version."
        return $false
    }
    
    # Enable Corepack for Yarn if needed
    try {
        & corepack enable 2>$null
    } catch {}
    
    # Fix: Check for interfering yarn.lock in parent directories
    if (-not (Test-Path "yarn.lock")) {
        Write-Step "Creating yarn.lock to prevent workspace conflicts..."
        New-Item -ItemType File -Path "yarn.lock" -Force | Out-Null
    }
    
    # Check for .yarnrc.yml
    if (-not (Test-Path ".yarnrc.yml")) {
        Write-Step "Creating .yarnrc.yml configuration..."
        @"
nodeLinker: node-modules
enableGlobalCache: true
"@ | Out-File -FilePath ".yarnrc.yml" -Encoding UTF8
    }
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Step "Installing dependencies (this may take 10-15 minutes)..."
        Write-Host "  This is a one-time setup. Please be patient..." -ForegroundColor Yellow
        
        # Set Corepack to non-interactive mode
        $env:COREPACK_ENABLE_DOWNLOAD_PROMPT = "0"
        
        # Warn about native modules on Windows
        Write-Warning "Some native modules may fail to build on Windows."
        Write-Step "If installation fails, you may need Visual Studio Build Tools."
        Write-Step "Download from: https://visualstudio.microsoft.com/downloads/"
        Write-Host ""
        
        $yarnLogFile = Join-Path $ProjectDir "yarn-install.log"
        & yarn install 2>&1 | Tee-Object -FilePath $yarnLogFile | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Installation failed (native modules need compilation)."
            Write-Host ""
            Write-Error "Theia requires Visual Studio Build Tools on Windows."
            Write-Host ""
            Write-Host "  To install Visual Studio Build Tools:" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
            Write-Host "  2. Run the installer"
            Write-Host "  3. Select 'Desktop development with C++'"
            Write-Host "  4. Complete installation and restart your terminal"
            Write-Host "  5. Run this script again"
            Write-Host ""
            Write-Host "  Alternative: Use Docker for the full IDE experience:" -ForegroundColor Yellow
            Write-Host "  docker-compose up -d agentic-ide"
            Write-Host ""
            Write-Warning "Continuing without Theia IDE..."
            Write-Step "You can still use the Python backend and MLFlow"
            $script:SkipTheia = $true
            return $true
        } else {
            Write-Success "Dependencies installed"
            $script:SkipTheia = $false
        }
    } else {
        Write-Step "Dependencies already installed"
        $script:SkipTheia = $false
    }
    
    # Skip if native modules failed
    if ($script:SkipTheia) {
        return $true
    }
    
    # Build if lib doesn't exist
    $BuildApp = "browser-app"
    $browserLib = Join-Path $FrontendDir "$BuildApp\lib"
    if (-not (Test-Path $browserLib)) {
        Write-Step "Building Theia - this may take 5-10 minutes..."
        Write-Host "  This is a one-time build. Please be patient..." -ForegroundColor Yellow
        
        & yarn workspace $BuildApp build 2>&1 | Select-Object -Last 10
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build Theia. Try manually: cd frontend && yarn workspace $BuildApp build"
            return $false
        }
        Write-Success "Theia built successfully"
    } else {
        Write-Step "Theia already built"
    }
    
    # Start Theia
    Write-Step "Starting Theia IDE..."
    $theiaLogFile = Join-Path $ProjectDir "theia.log"
    $browserAppDir = Join-Path $FrontendDir $BuildApp
    
    $theiaProcess = Start-Process -FilePath "yarn" -ArgumentList "start" -WorkingDirectory $browserAppDir -RedirectStandardOutput $theiaLogFile -RedirectStandardError "$theiaLogFile.err" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    if ($theiaProcess) {
        $theiaProcess.Id | Out-File (Join-Path $ProjectDir ".theia.pid")
        Write-Success "Theia started on port 3000 (PID: $($theiaProcess.Id))"
    } else {
        Write-Error "Failed to start Theia"
        return $false
    }
    
    # Wait for Theia to be ready
    Write-Host "  Waiting for Theia to start" -NoNewline
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 1
        
        # Check if process is still running
        if (-not (Get-Process -Id $theiaProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host ""
            Write-Error "Theia process died. Check theia.log for errors."
            return $false
        }
        
        # Check if port is listening
        try {
            $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port 3000 -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($connection) {
                Write-Host ""
                Write-Success "Theia is ready"
                return $true
            }
        } catch {}
        
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Warning "Theia may still be starting. Check http://localhost:3000 in a moment."
    return $true
}

function Open-Browser {
    param([string]$Url)
    
    Write-Section "Opening Browser"
    Write-Step "Opening $Url"
    Start-Process $Url
}

function Show-Summary {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "       DEVELOPMENT ENVIRONMENT READY                          " -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services Running:" -ForegroundColor Cyan
    if ($script:SkipTheia) {
        Write-Host "  - Theia IDE:       " -NoNewline
        Write-Host "Not started (native modules need compilation)" -ForegroundColor Yellow
    } else {
        Write-Host "  - Theia IDE:       http://localhost:3000"
    }
    Write-Host "  - Python Backend:  http://localhost:8080"
    Write-Host "  - MLFlow:          http://localhost:5000"
    Write-Host "  - WebSocket:       ws://localhost:8080/ws"
    Write-Host ""
    Write-Host "API Endpoints:" -ForegroundColor Cyan
    Write-Host "  - Experiments:     http://localhost:8080/api/v1/experiments"
    Write-Host "  - Artifacts:       http://localhost:8080/api/v1/artifacts"
    Write-Host "  - Sessions:        http://localhost:8080/api/v1/sessions"
    Write-Host "  - Data:            http://localhost:8080/api/v1/data"
    Write-Host "  - Config:          http://localhost:8080/api/v1/config"
    Write-Host ""
    if ($script:SkipTheia) {
        Write-Host "NOTE: Theia IDE requires Visual Studio Build Tools on Windows." -ForegroundColor Yellow
        Write-Host "      Install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
        Write-Host ""
    }
    Write-Host "To stop all services: .\scripts\stop-dev.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Banner
Set-Location $ProjectDir

if (-not $FrontendOnly) {
    $backendOk = Start-PythonBackend
    if (-not $backendOk) {
        Write-Error "Failed to start backend services"
    }
}

if (-not $BackendOnly) {
    $frontendOk = Start-TheiaFrontend
    if (-not $frontendOk) {
        Write-Error "Failed to start frontend"
    }
}

Show-Summary

if (-not $NoBrowser -and -not $BackendOnly) {
    Open-Browser "http://localhost:3000"
}

