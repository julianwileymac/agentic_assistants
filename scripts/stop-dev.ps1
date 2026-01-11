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

function Stop-ProcessTree {
    param(
        [int]$ProcessId,
        [string]$ServiceName
    )
    
    try {
        # First, get all child processes recursively
        $childProcesses = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ProcessId }
        
        foreach ($child in $childProcesses) {
            # Recursively kill children of children
            Stop-ProcessTree -ProcessId $child.ProcessId -ServiceName "$ServiceName child"
        }
        
        # Now kill the parent process
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Stopped $ServiceName (PID: $ProcessId)" -ForegroundColor Green
            return $true
        }
    } catch {
        # Process might already be gone
    }
    return $false
}

function Stop-ProcessOnPort {
    param(
        [int]$Port
    )
    
    $killed = $false
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            $procId = $conn.OwningProcess
            if ($procId -and $procId -ne 0) {
                $process = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($process) {
                    $processName = $process.ProcessName
                    # Kill the process tree
                    Stop-ProcessTree -ProcessId $procId -ServiceName "$processName on port $Port"
                    $killed = $true
                }
            }
        }
    } catch {}
    return $killed
}

# Stop Theia
$theiaPath = Join-Path $ProjectDir ".theia.pid"
if (Test-Path $theiaPath) {
    $procId = Get-Content $theiaPath -ErrorAction SilentlyContinue
    if ($procId) {
        if (Stop-ProcessTree -ProcessId ([int]$procId) -ServiceName "Theia") {
            $stopped = $true
        }
    }
    Remove-Item $theiaPath -ErrorAction SilentlyContinue
}

# Stop Backend (uvicorn spawns multiple workers)
$backendPath = Join-Path $ProjectDir ".backend.pid"
if (Test-Path $backendPath) {
    $procId = Get-Content $backendPath -ErrorAction SilentlyContinue
    if ($procId) {
        if (Stop-ProcessTree -ProcessId ([int]$procId) -ServiceName "Backend") {
            $stopped = $true
        }
    }
    Remove-Item $backendPath -ErrorAction SilentlyContinue
}

# Stop MLFlow
$mlflowPath = Join-Path $ProjectDir ".mlflow.pid"
if (Test-Path $mlflowPath) {
    $procId = Get-Content $mlflowPath -ErrorAction SilentlyContinue
    if ($procId) {
        if (Stop-ProcessTree -ProcessId ([int]$procId) -ServiceName "MLFlow") {
            $stopped = $true
        }
    }
    Remove-Item $mlflowPath -ErrorAction SilentlyContinue
}

# Stop Web UI (npm spawns node child processes)
$webuiPath = Join-Path $ProjectDir ".webui.pid"
if (Test-Path $webuiPath) {
    $procId = Get-Content $webuiPath -ErrorAction SilentlyContinue
    if ($procId) {
        if (Stop-ProcessTree -ProcessId ([int]$procId) -ServiceName "Web UI") {
            $stopped = $true
        }
    }
    Remove-Item $webuiPath -ErrorAction SilentlyContinue
}

# Stop JupyterLab
$jupyterPath = Join-Path $ProjectDir ".jupyter.pid"
if (Test-Path $jupyterPath) {
    $procId = Get-Content $jupyterPath -ErrorAction SilentlyContinue
    if ($procId) {
        if (Stop-ProcessTree -ProcessId ([int]$procId) -ServiceName "JupyterLab") {
            $stopped = $true
        }
    }
    Remove-Item $jupyterPath -ErrorAction SilentlyContinue
}

# Always check ports to catch orphaned processes
Write-Host ""
Write-Host "  Checking for processes on development ports..." -ForegroundColor Yellow

$ports = @(3000, 5000, 8080, 8888)
foreach ($port in $ports) {
    $result = Stop-ProcessOnPort -Port $port
    if ($result) {
        $stopped = $true
    }
}

# Additional cleanup: Find any node/python processes that might be related
if ($Force) {
    Write-Host ""
    Write-Host "  Force mode: Looking for related processes..." -ForegroundColor Yellow
    
    # Kill any node processes running from webui directory
    Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            if ($cmdLine -and ($cmdLine -like "*webui*" -or $cmdLine -like "*next*" -or $cmdLine -like "*3000*")) {
                if (Stop-ProcessTree -ProcessId $_.Id -ServiceName "Node (webui related)") {
                    $script:stopped = $true
                }
            }
        } catch {}
    }
    
    # Kill any uvicorn processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            if ($cmdLine -and ($cmdLine -like "*uvicorn*" -or $cmdLine -like "*agentic_assistants*")) {
                if (Stop-ProcessTree -ProcessId $_.Id -ServiceName "Python (backend related)") {
                    $script:stopped = $true
                }
            }
        } catch {}
    }
    
    # Kill any mlflow processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            if ($cmdLine -and $cmdLine -like "*mlflow*") {
                if (Stop-ProcessTree -ProcessId $_.Id -ServiceName "Python (mlflow related)") {
                    $script:stopped = $true
                }
            }
        } catch {}
    }
    
    # Kill any jupyter processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            if ($cmdLine -and $cmdLine -like "*jupyter*") {
                if (Stop-ProcessTree -ProcessId $_.Id -ServiceName "Python (jupyter related)") {
                    $script:stopped = $true
                }
            }
        } catch {}
    }
}

# Clean up log files (optional)
$logFiles = @("backend.log", "backend.log.err", "mlflow.log", "mlflow.log.err", "theia.log", "theia.log.err", "webui.log", "webui.log.err", "jupyterlab.log", "jupyterlab.log.err")
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
Write-Host "Tip: Use -Force flag to also kill orphaned node/python processes." -ForegroundColor Gray
Write-Host ""
