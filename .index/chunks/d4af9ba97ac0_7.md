# Chunk: d4af9ba97ac0_7

- source: `scripts/start-dev.ps1`
- lines: 453-516
- chunk: 8/8

```
   Write-Host "  - Data:            http://localhost:8080/api/v1/data"
    Write-Host "  - Config:          http://localhost:8080/api/v1/config"
    Write-Host ""
    if ($script:SkipTheia) {
        Write-Host "NOTE: Theia IDE requires Visual Studio Build Tools on Windows." -ForegroundColor Yellow
        Write-Host "      Install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
        Write-Host ""
    }
    Write-Host "To stop all services: .\scripts\stop-dev.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Banner
Set-Location $ProjectDir

if (-not $FrontendOnly) {
    $backendOk = Start-PythonBackend
    if (-not $backendOk) {
        Write-Error "Failed to start backend services"
    }
}

if (-not $BackendOnly) {
    switch ($UIChoice.ToLower()) {
        "theia" {
            $frontendOk = Start-TheiaFrontend
        }
        "jupyterlab" {
            $frontendOk = Start-JupyterLabUI
        }
        "webui" {
            $frontendOk = Start-WebUI
        }
        "none" {
            Write-Warning "UI disabled (--UIChoice none)."
            $frontendOk = $true
        }
        default {
            Write-Warning "Unknown UI choice '$UIChoice'. Skipping UI."
            $frontendOk = $true
        }
    }
    if (-not $frontendOk) {
        Write-Error "Failed to start frontend"
    }
}

Show-Summary

if (-not $NoBrowser -and -not $BackendOnly) {
    switch ($UIChoice.ToLower()) {
        "webui" { Open-Browser "http://localhost:$WebUIPort" }
        "jupyterlab" { Open-Browser "http://localhost:$JupyterPort/lab" }
        "theia" { Open-Browser "http://localhost:3000" }
    }
}
```
