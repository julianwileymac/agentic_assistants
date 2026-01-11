# Chunk: d4af9ba97ac0_5

- source: `scripts/start-dev.ps1`
- lines: 327-406
- chunk: 6/8

```

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

function Start-WebUI {
    Write-Section "Starting Web UI (Next.js)"

    $webuiDir = Join-Path $ProjectDir "webui"
    if (-not (Test-Path $webuiDir)) {
        Write-Error "Web UI directory not found at $webuiDir"
        return $false
    }

    Set-Location $webuiDir

    if (-not (Test-Path "node_modules")) {
        Write-Step "Installing Web UI dependencies..."
        & npm install | Select-Object -Last 5
    } else {
        Write-Step "Dependencies already installed"
    }

    $env:PORT = $WebUIPort
    $webuiLog = Join-Path $ProjectDir "webui.log"
    $webuiProcess = Start-Process -FilePath "npm" -ArgumentList "run","dev","--","--hostname","127.0.0.1","--port",$WebUIPort -RedirectStandardOutput $webuiLog -RedirectStandardError "$webuiLog.err" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    if ($webuiProcess) {
        $webuiProcess.Id | Out-File (Join-Path $ProjectDir ".webui.pid")
        Write-Success "Web UI started on http://localhost:$WebUIPort (PID: $($webuiProcess.Id))"
        return $true
    } else {
        Write-Error "Failed to start Web UI"
        return $false
    }
}

function Start-JupyterLabUI {
    Write-Section "Starting JupyterLab"
    Set-Location $ProjectDir

    if (-not (Test-Path "notebooks")) { New-Item -ItemType Directory -Path "notebooks" | Out-Null }
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
    if (-not (Test-Path "mlruns")) { New-Item -ItemType Directory -Path "mlruns" | Out-Null }

    $jupyterLog = Join-Path $ProjectDir "jupyterlab.log"
```
