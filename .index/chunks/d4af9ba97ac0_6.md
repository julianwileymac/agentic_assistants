# Chunk: d4af9ba97ac0_6

- source: `scripts/start-dev.ps1`
- lines: 401-458
- chunk: 7/8

```
w-Item -ItemType Directory -Path "notebooks" | Out-Null }
    if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
    if (-not (Test-Path "mlruns")) { New-Item -ItemType Directory -Path "mlruns" | Out-Null }

    $jupyterLog = Join-Path $ProjectDir "jupyterlab.log"
    $jupyterProcess = Start-Process -FilePath "jupyter" -ArgumentList "lab","--ip","127.0.0.1","--port",$JupyterPort,"--no-browser","--NotebookApp.token=''","--NotebookApp.password=''","--NotebookApp.notebook_dir=$ProjectDir" -RedirectStandardOutput $jupyterLog -RedirectStandardError "$jupyterLog.err" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    if ($jupyterProcess) {
        $jupyterProcess.Id | Out-File (Join-Path $ProjectDir ".jupyter.pid")
        Write-Success "JupyterLab started on http://localhost:$JupyterPort/lab (PID: $($jupyterProcess.Id))"
        return $true
    } else {
        Write-Error "Failed to start JupyterLab (is it installed?)"
        return $false
    }
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
    switch ($UIChoice.ToLower()) {
        "webui" { Write-Host "  - Web UI:          http://localhost:$WebUIPort" }
        "jupyterlab" { Write-Host "  - JupyterLab:      http://localhost:$JupyterPort/lab" }
        "theia" {
            if ($script:SkipTheia) {
                Write-Host "  - Theia IDE:       " -NoNewline
                Write-Host "Not started (native modules need compilation)" -ForegroundColor Yellow
            } else {
                Write-Host "  - Theia IDE:       http://localhost:3000"
            }
        }
        default { Write-Host "  - UI:              (disabled)" }
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
```
