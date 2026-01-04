# =============================================================================
# Agentic Assistants - Stop Development Services (Windows PowerShell)
# =============================================================================
# Stops all running development services
#
# Usage:
#   .\scripts\stop-dev.ps1        # Stop all services
#   .\scripts\stop-dev.ps1 -Force # Force kill all processes on ports
# =============================================================================

param(
    [switch]$Force
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Set-Location $ProjectDir

Write-Host ""
Write-Host "Stopping development services..." -ForegroundColor Cyan
Write-Host ""

$stopped = $false

# Stop Theia
$theiaPath = Join-Path $ProjectDir ".theia.pid"
if (Test-Path $theiaPath) {
    $pid = Get-Content $theiaPath
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Stopped Theia (PID: $pid)" -ForegroundColor Green
            $stopped = $true
        }
    } catch {}
    Remove-Item $theiaPath -ErrorAction SilentlyContinue
}

# Stop Backend
$backendPath = Join-Path $ProjectDir ".backend.pid"
if (Test-Path $backendPath) {
    $pid = Get-Content $backendPath
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Stopped Backend (PID: $pid)" -ForegroundColor Green
            $stopped = $true
        }
    } catch {}
    Remove-Item $backendPath -ErrorAction SilentlyContinue
}

# Stop MLFlow
$mlflowPath = Join-Path $ProjectDir ".mlflow.pid"
if (Test-Path $mlflowPath) {
    $pid = Get-Content $mlflowPath
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Stopped MLFlow (PID: $pid)" -ForegroundColor Green
            $stopped = $true
        }
    } catch {}
    Remove-Item $mlflowPath -ErrorAction SilentlyContinue
}

# Kill any remaining processes on our ports (if Force flag or if PIDs didn't work)
if ($Force -or -not $stopped) {
    Write-Host ""
    Write-Host "  Checking for processes on development ports..." -ForegroundColor Yellow
    
    $ports = @(3000, 5000, 8080)
    foreach ($port in $ports) {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            $pid = $conn.OwningProcess
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "  [OK] Stopped process on port $port (PID: $pid)" -ForegroundColor Green
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    $stopped = $true
                }
            } catch {}
        }
    }
}

# Clean up log files (optional)
$logFiles = @("backend.log", "backend.log.err", "mlflow.log", "mlflow.log.err", "theia.log", "theia.log.err")
foreach ($log in $logFiles) {
    $logPath = Join-Path $ProjectDir $log
    if (Test-Path $logPath) {
        # Don't delete, just mention them
        # Remove-Item $logPath -ErrorAction SilentlyContinue
    }
}

Write-Host ""
if ($stopped) {
    Write-Host "All development services stopped." -ForegroundColor Green
} else {
    Write-Host "No running services found." -ForegroundColor Yellow
}
Write-Host ""

