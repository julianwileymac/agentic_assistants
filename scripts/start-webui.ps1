# =============================================================================
# Agentic Assistants - Web UI Startup Script (Windows PowerShell)
# =============================================================================
# This script starts the Next.js web control panel.
#
# Usage:
#   .\scripts\start-webui.ps1              # Start web UI on port 3000
#   .\scripts\start-webui.ps1 -Port 3001   # Start on custom port
#   .\scripts\start-webui.ps1 -Dev         # Start in development mode
# =============================================================================

param(
    [int]$Port = 3000,
    [switch]$Dev,
    [switch]$Help
)

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$WebUIDir = Join-Path $ProjectDir "webui"

function Write-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║           🎛️  Agentic Control Panel                       ║" -ForegroundColor Blue
    Write-Host "║              Web UI Startup Script                        ║" -ForegroundColor Blue
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Usage {
    Write-Host "Usage: .\scripts\start-webui.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Port PORT     Port to run the web UI on (default: 3000)"
    Write-Host "  -Dev           Run in development mode with hot reload"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\start-webui.ps1              # Start on port 3000"
    Write-Host "  .\scripts\start-webui.ps1 -Port 3001   # Start on port 3001"
    Write-Host "  .\scripts\start-webui.ps1 -Dev         # Start in dev mode"
}

if ($Help) {
    Write-Usage
    exit 0
}

Write-Banner

# Check if webui directory exists
if (-not (Test-Path $WebUIDir)) {
    Write-Host "Error: Web UI directory not found at $WebUIDir" -ForegroundColor Red
    Write-Host "Please ensure the webui has been set up."
    exit 1
}

Set-Location $WebUIDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Set environment variable for port
$env:PORT = $Port

# Start the web UI
if ($Dev) {
    Write-Host "Starting Web UI in development mode on port $Port..." -ForegroundColor Green
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Hidden
} else {
    Write-Host "Building Web UI for production..." -ForegroundColor Yellow
    npm run build
    
    Write-Host "Starting Web UI on port $Port..." -ForegroundColor Green
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "start" -PassThru -WindowStyle Hidden
}

# Save PID
$process.Id | Out-File "$ProjectDir\.webui.pid"

# Wait for the server to start
Write-Host "  Waiting for Web UI to start" -NoNewline
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "  ✓ Web UI started successfully" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access the control panel at: http://localhost:$Port"
        Write-Host ""
        Write-Host "To stop: Stop-Process -Id $($process.Id) or .\scripts\stop-webui.ps1"
        
        # Open browser
        Start-Process "http://localhost:$Port"
        exit 0
    }
    catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
    }
}

Write-Host ""
Write-Host "Web UI is starting... Check http://localhost:$Port" -ForegroundColor Yellow

