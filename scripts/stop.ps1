# =============================================================================
# Agentic Assistants - Shutdown Script (Windows PowerShell)
# =============================================================================
# This script stops services started by the Agentic Assistants framework.
#
# Usage:
#   .\scripts\stop.ps1              # Stop MLFlow (preserves Ollama)
#   .\scripts\stop.ps1 -All         # Stop all services including Ollama
#   .\scripts\stop.ps1 -Docker      # Stop Docker Compose services
# =============================================================================

param(
    [switch]$All,
    [switch]$Docker,
    [switch]$Ollama,
    [switch]$MLFlow,
    [switch]$Help
)

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

function Write-Usage {
    Write-Host "Usage: .\scripts\stop.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -All           Stop all services including Ollama"
    Write-Host "  -Docker        Stop Docker Compose services"
    Write-Host "  -Ollama        Stop only Ollama"
    Write-Host "  -MLFlow        Stop only MLFlow"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\stop.ps1              # Stop MLFlow (preserves Ollama)"
    Write-Host "  .\scripts\stop.ps1 -All         # Stop all services"
    Write-Host "  .\scripts\stop.ps1 -Docker      # Stop Docker services"
}

if ($Help) {
    Write-Usage
    exit 0
}

# Determine what to stop
$StopOllama = $false
$StopMLFlow = $true

if ($All) {
    $StopOllama = $true
    $StopMLFlow = $true
}

if ($Ollama) {
    $StopOllama = $true
    $StopMLFlow = $false
}

if ($MLFlow) {
    $StopOllama = $false
    $StopMLFlow = $true
}

Write-Host "Stopping Agentic Assistants services..." -ForegroundColor Blue
Write-Host ""

# Change to project directory
Set-Location $ProjectDir

# Docker Compose mode
if ($Docker) {
    Write-Host "Stopping Docker Compose services..." -ForegroundColor Yellow
    
    $dockerCompose = Get-Command docker-compose -ErrorAction SilentlyContinue
    if ($dockerCompose) {
        docker-compose down
        Write-Host "✓ Docker services stopped" -ForegroundColor Green
    }
    else {
        Write-Host "Error: docker-compose not found" -ForegroundColor Red
    }
    exit 0
}

# Stop MLFlow
if ($StopMLFlow) {
    Write-Host "Stopping MLFlow..." -ForegroundColor Yellow
    
    if (Test-Path ".mlflow.pid") {
        $pid = Get-Content ".mlflow.pid"
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $pid -Force
                Remove-Item ".mlflow.pid"
                Write-Host "  ✓ MLFlow stopped (PID: $pid)" -ForegroundColor Green
            }
            else {
                Remove-Item ".mlflow.pid"
                Write-Host "  ! MLFlow was not running" -ForegroundColor Yellow
            }
        }
        catch {
            Remove-Item ".mlflow.pid" -ErrorAction SilentlyContinue
            Write-Host "  ! Error stopping MLFlow" -ForegroundColor Yellow
        }
    }
    else {
        # Try to find MLFlow process
        $mlflowProcesses = Get-Process -Name "mlflow" -ErrorAction SilentlyContinue
        if ($mlflowProcesses) {
            $mlflowProcesses | Stop-Process -Force
            Write-Host "  ✓ MLFlow stopped" -ForegroundColor Green
        }
        else {
            Write-Host "  ! No MLFlow process found" -ForegroundColor Yellow
        }
    }
}

# Stop Ollama
if ($StopOllama) {
    Write-Host "Stopping Ollama..." -ForegroundColor Yellow
    
    $ollamaProcesses = Get-Process -Name "ollama*" -ErrorAction SilentlyContinue
    if ($ollamaProcesses) {
        $ollamaProcesses | Stop-Process -Force
        Write-Host "  ✓ Ollama stopped" -ForegroundColor Green
    }
    else {
        Write-Host "  ! No Ollama process found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Shutdown complete!" -ForegroundColor Green

