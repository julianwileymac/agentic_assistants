# Chunk: d4af9ba97ac0_2

- source: `scripts/start-dev.ps1`
- lines: 139-211
- chunk: 3/8

```
.mlflow.pid"
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
```
