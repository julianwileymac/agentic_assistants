# Chunk: d4af9ba97ac0_4

- source: `scripts/start-dev.ps1`
- lines: 268-337
- chunk: 5/8

```
       
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
```
