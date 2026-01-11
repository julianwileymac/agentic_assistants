# Chunk: d4af9ba97ac0_1

- source: `scripts/start-dev.ps1`
- lines: 74-148
- chunk: 2/8

```
    Write-Host "  Web UI:          http://localhost:3000 (default UI)"
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
```
