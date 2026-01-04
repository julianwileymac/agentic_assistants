#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start JupyterLab with all supporting services (MLFlow, Backend API, OTEL Collector).

.DESCRIPTION
    This script starts the complete Agentic Assistants development environment:
    - MLFlow tracking server (port 5000)
    - Backend API server (port 8080)
    - OpenTelemetry collector (optional, port 4317)
    - JupyterLab IDE (port 3000)

.PARAMETER SkipMLFlow
    Skip starting the MLFlow server

.PARAMETER SkipBackend
    Skip starting the backend API server

.PARAMETER SkipOTEL
    Skip starting the OpenTelemetry collector

.PARAMETER Port
    JupyterLab port (default: 3000)

.EXAMPLE
    .\start-lab.ps1
    .\start-lab.ps1 -SkipMLFlow
    .\start-lab.ps1 -Port 8888
#>

param(
    [switch]$SkipMLFlow,
    [switch]$SkipBackend,
    [switch]$SkipOTEL,
    [int]$Port = 3000
)

$ErrorActionPreference = "Stop"

# Paths
$Root = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$Root = Resolve-Path (Join-Path $Root "..")
$Venv = Join-Path $Root ".venv-lab"
$Py = $Env:LAB_PYTHON
if (-not $Py) { $Py = "python" }

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Status($Message) {
    Write-Host "[*] " -NoNewline -ForegroundColor Cyan
    Write-Host $Message
}

function Write-Success($Message) {
    Write-Host "[+] " -NoNewline -ForegroundColor Green
    Write-Host $Message
}

function Write-Warning($Message) {
    Write-Host "[!] " -NoNewline -ForegroundColor Yellow
    Write-Host $Message
}

function Write-Error($Message) {
    Write-Host "[-] " -NoNewline -ForegroundColor Red
    Write-Host $Message
}

# Store background job IDs for cleanup
$script:BackgroundJobs = @()

function Stop-BackgroundServices {
    Write-Status "Stopping background services..."
    foreach ($job in $script:BackgroundJobs) {
        if ($job -and (Get-Job -Id $job.Id -ErrorAction SilentlyContinue)) {
            Stop-Job -Id $job.Id -ErrorAction SilentlyContinue
            Remove-Job -Id $job.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Also stop any remaining processes
    Get-Process -Name "mlflow" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Register cleanup on script exit
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-BackgroundServices }

trap {
    Stop-BackgroundServices
    break
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Agentic Assistants - JupyterLab Environment  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Status "Checking Python version..."
$pyVersion = & $Py -c "import sys; v=sys.version_info; print(str(v.major)+'.'+str(v.minor))"
if (-not $pyVersion) {
    Write-Error "Could not determine Python version for '$Py'"
    exit 1
}
$parts = $pyVersion.Split(".")
if ([int]$parts[0] -gt 3 -or (([int]$parts[0] -eq 3) -and ([int]$parts[1] -ge 13))) {
    Write-Error "Python $pyVersion detected. Please use Python 3.10-3.12 (set LAB_PYTHON to an appropriate interpreter, e.g., py -3.11)."
    exit 1
}
Write-Success "Python $pyVersion detected"

# Create/update virtual environment
Write-Status "Setting up virtual environment..."
if (-not (Test-Path $Venv)) {
    & $Py -m venv $Venv
    & "$Venv\Scripts\python.exe" -m pip install --upgrade pip -q
    Write-Success "Created virtual environment"
} else {
    Write-Success "Virtual environment exists"
}

# Install requirements
Write-Status "Installing requirements..."
& "$Venv\Scripts\python.exe" -m pip install -r (Join-Path $Root "lab/requirements.txt") -q
Write-Success "Requirements installed"

# Start MLFlow server
if (-not $SkipMLFlow) {
    Write-Status "Starting MLFlow server on port 5000..."
    
    $mlflowRunning = Test-NetConnection -ComputerName localhost -Port 5000 -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($mlflowRunning) {
        Write-Success "MLFlow already running on port 5000"
    } else {
        $mlflowLog = Join-Path $Root "mlflow.log"
        $mlflowCmd = {
            param($VenvPath, $RootPath, $LogPath)
            & "$VenvPath\Scripts\mlflow.exe" server `
                --host 127.0.0.1 `
                --port 5000 `
                --backend-store-uri "sqlite:///$RootPath/mlruns/mlflow.db" `
                --default-artifact-root "$RootPath/mlruns/artifacts" `
                2>&1 | Out-File -FilePath $LogPath -Append
        }
        $mlflowJob = Start-Job -ScriptBlock $mlflowCmd -ArgumentList $Venv, $Root, $mlflowLog
        $script:BackgroundJobs += $mlflowJob
        
        # Wait for MLFlow to start
        $attempts = 0
        while ($attempts -lt 10) {
            Start-Sleep -Seconds 1
            $attempts++
            $mlflowRunning = Test-NetConnection -ComputerName localhost -Port 5000 -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($mlflowRunning) {
                Write-Success "MLFlow server started (Job ID: $($mlflowJob.Id))"
                break
            }
        }
        if (-not $mlflowRunning) {
            Write-Warning "MLFlow may not have started. Check $mlflowLog for details."
        }
    }
}

# Start Backend API server
if (-not $SkipBackend) {
    Write-Status "Starting Backend API server on port 8080..."
    
    $backendRunning = Test-NetConnection -ComputerName localhost -Port 8080 -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($backendRunning) {
        Write-Success "Backend API already running on port 8080"
    } else {
        $backendLog = Join-Path $Root "backend.log"
        $backendCmd = {
            param($VenvPath, $RootPath, $LogPath)
            $env:PYTHONPATH = "$RootPath\src"
            & "$VenvPath\Scripts\python.exe" -m uvicorn `
                agentic_assistants.server.app:create_app `
                --factory `
                --host 127.0.0.1 `
                --port 8080 `
                2>&1 | Out-File -FilePath $LogPath -Append
        }
        $backendJob = Start-Job -ScriptBlock $backendCmd -ArgumentList $Venv, $Root, $backendLog
        $script:BackgroundJobs += $backendJob
        
        # Wait for backend to start
        $attempts = 0
        while ($attempts -lt 10) {
            Start-Sleep -Seconds 1
            $attempts++
            $backendRunning = Test-NetConnection -ComputerName localhost -Port 8080 -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($backendRunning) {
                Write-Success "Backend API server started (Job ID: $($backendJob.Id))"
                break
            }
        }
        if (-not $backendRunning) {
            Write-Warning "Backend API may not have started. Check $backendLog for details."
        }
    }
}

# Check for OTEL Collector (optional - uses Docker)
if (-not $SkipOTEL) {
    Write-Status "Checking OpenTelemetry Collector..."
    
    $otelRunning = Test-NetConnection -ComputerName localhost -Port 4317 -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($otelRunning) {
        Write-Success "OTEL Collector running on port 4317"
    } else {
        # Check if Docker is available
        $dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue
        if ($dockerAvailable) {
            Write-Status "Starting OTEL Collector via Docker..."
            docker run -d --name agentic-otel-collector `
                -p 4317:4317 -p 4318:4318 -p 8888:8888 `
                -v "$Root/docker/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml:ro" `
                otel/opentelemetry-collector-contrib:0.91.0 `
                --config=/etc/otelcol-contrib/config.yaml 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "OTEL Collector started via Docker"
            } else {
                Write-Warning "Could not start OTEL Collector. Tracing will be disabled."
            }
        } else {
            Write-Warning "Docker not available. OTEL Collector not started. Tracing will be disabled."
            Write-Warning "To enable tracing, install Docker and run: docker-compose up -d otel-collector jaeger"
        }
    }
}

# Set environment variables
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
$env:AGENTIC_BACKEND_URL = "http://localhost:8080"
$env:OTEL_EXPORTER_OTLP_ENDPOINT = "http://localhost:4317"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   Services Status                              " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  MLFlow:      http://localhost:5000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8080" -ForegroundColor White
Write-Host "  OTEL:        http://localhost:4317 (gRPC)" -ForegroundColor White
Write-Host "  JupyterLab:  http://localhost:$Port" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Start JupyterLab
Write-Status "Starting JupyterLab on port $Port..."
$configPath = Join-Path $Root "lab/jupyter_lab_config.py"

# Update port in config if different from default
if ($Port -ne 3000) {
    $env:JUPYTERLAB_PORT = $Port
}

& "$Venv\Scripts\jupyter.exe" lab --config $configPath --port $Port

# Cleanup on exit
Stop-BackgroundServices
