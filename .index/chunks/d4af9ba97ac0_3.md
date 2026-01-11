# Chunk: d4af9ba97ac0_3

- source: `scripts/start-dev.ps1`
- lines: 202-275
- chunk: 4/8

```
est-Path $FrontendDir)) {
        Write-Warning "Frontend directory not found. Theia IDE is not set up yet."
        Write-Host "  To set up Theia, run: cd frontend && yarn install && yarn build"
        return $false
    }
    
    Set-Location $FrontendDir
    
    # Check if Node.js is installed
    try {
        $nodeVersion = & node --version
        Write-Step "Node.js version: $nodeVersion"
    } catch {
        Write-Error "Node.js is not installed. Please install Node.js 18 or 20 LTS to use Theia IDE."
        return $false
    }
    
    # Check Node.js version - must be 18.x or 20.x (not 22+ due to native module issues)
    $nodeMajor = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
    if ($nodeMajor -gt 20) {
        Write-Error "Node.js $nodeVersion is too new. Theia requires Node.js 18 or 20 LTS."
        Write-Warning "Please install Node.js 20 LTS:"
        Write-Host "  - Windows: Download from https://nodejs.org/en/download/"
        Write-Host "  - Or use nvm-windows: nvm install 20 && nvm use 20"
        Write-Host ""
        Write-Step "Skipping Theia frontend due to incompatible Node.js version."
        return $false
    } elseif ($nodeMajor -lt 18) {
        Write-Error "Node.js $nodeVersion is too old. Theia requires Node.js 18 or 20 LTS."
        Write-Step "Skipping Theia frontend due to incompatible Node.js version."
        return $false
    }
    
    # Enable Corepack for Yarn if needed
    try {
        & corepack enable 2>$null
    } catch {}
    
    # Fix: Check for interfering yarn.lock in parent directories
    if (-not (Test-Path "yarn.lock")) {
        Write-Step "Creating yarn.lock to prevent workspace conflicts..."
        New-Item -ItemType File -Path "yarn.lock" -Force | Out-Null
    }
    
    # Check for .yarnrc.yml
    if (-not (Test-Path ".yarnrc.yml")) {
        Write-Step "Creating .yarnrc.yml configuration..."
        @"
nodeLinker: node-modules
enableGlobalCache: true
"@ | Out-File -FilePath ".yarnrc.yml" -Encoding UTF8
    }
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Step "Installing dependencies (this may take 10-15 minutes)..."
        Write-Host "  This is a one-time setup. Please be patient..." -ForegroundColor Yellow
        
        # Set Corepack to non-interactive mode
        $env:COREPACK_ENABLE_DOWNLOAD_PROMPT = "0"
        
        # Warn about native modules on Windows
        Write-Warning "Some native modules may fail to build on Windows."
        Write-Step "If installation fails, you may need Visual Studio Build Tools."
        Write-Step "Download from: https://visualstudio.microsoft.com/downloads/"
        Write-Host ""
        
        $yarnLogFile = Join-Path $ProjectDir "yarn-install.log"
        & yarn install 2>&1 | Tee-Object -FilePath $yarnLogFile | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Installation failed (native modules need compilation)."
            Write-Host ""
```
