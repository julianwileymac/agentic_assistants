###############################################################################
# Cybersecurity Hub - Windows Tool Installation Script
#
# Installs common cybersecurity tools on Windows systems.
# Requires: Administrator privileges, Chocolatey package manager
#
# Usage: .\install_windows.ps1 [-Category <category>]
#   Category: Network, Web, Exploit, Forensics, Password, All (default)
###############################################################################

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Network", "Web", "Exploit", "Forensics", "Password", "All")]
    [string]$Category = "All"
)

# Requires elevation
#Requires -RunAsAdministrator

Write-Host "====================================" -ForegroundColor Blue
Write-Host "Cybersecurity Hub Tool Installer" -ForegroundColor Blue
Write-Host "Windows Edition" -ForegroundColor Blue
Write-Host "====================================" -ForegroundColor Blue
Write-Host ""

$LogFile = "install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

Write-Host "Installation category: $Category" -ForegroundColor Blue
Write-Host "Log file: $LogFile" -ForegroundColor Blue
Write-Host ""

# Check for Chocolatey
function Test-Chocolatey {
    try {
        choco --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Install-Chocolatey {
    Write-Host "Installing Chocolatey package manager..." -ForegroundColor Yellow
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment
        $env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."
        Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
        refreshenv
        
        Write-Host "✓ Chocolatey installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to install Chocolatey: $_" -ForegroundColor Red
        return $false
    }
}

# Install tool via Chocolatey
function Install-Tool {
    param(
        [string]$ToolName,
        [string]$ChocoPackage
    )
    
    Write-Host "Installing $ToolName... " -NoNewline
    
    # Check if already installed
    $installed = choco list --local-only $ChocoPackage 2>&1 | Select-String -Pattern "^$ChocoPackage "
    
    if ($installed) {
        Write-Host "already installed" -ForegroundColor Yellow
        return $true
    }
    
    try {
        choco install $ChocoPackage -y --limit-output >> $LogFile 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ success" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "✗ failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ failed: $_" -ForegroundColor Red
        return $false
    }
}

# Install Python package via pip
function Install-PipPackage {
    param(
        [string]$ToolName,
        [string]$PipPackage
    )
    
    Write-Host "Installing $ToolName (via pip)... " -NoNewline
    
    try {
        python -m pip show $PipPackage > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "already installed" -ForegroundColor Yellow
            return $true
        }
        
        python -m pip install $PipPackage >> $LogFile 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ success" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "✗ failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ failed: $_" -ForegroundColor Red
        return $false
    }
}

# Check and install Chocolatey
if (-not (Test-Chocolatey)) {
    Write-Host "Chocolatey not found. Installing..." -ForegroundColor Yellow
    if (-not (Install-Chocolatey)) {
        Write-Host "Failed to install Chocolatey. Exiting." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ Chocolatey is installed" -ForegroundColor Green
}

Write-Host ""

# Network Tools
function Install-NetworkTools {
    Write-Host "=== Installing Network Tools ===" -ForegroundColor Blue
    Install-Tool "Nmap" "nmap"
    Install-Tool "Netcat" "netcat"
    Install-Tool "Wireshark" "wireshark"
    
    # Python-based
    Install-PipPackage "Scapy" "scapy"
    
    Write-Host ""
}

# Web Application Tools
function Install-WebTools {
    Write-Host "=== Installing Web Application Tools ===" -ForegroundColor Blue
    Install-Tool "OWASP ZAP" "zap"
    Install-Tool "Burp Suite Free" "burpsuite-free-edition"
    Install-PipPackage "SQLMap" "sqlmap"
    Install-PipPackage "Wfuzz" "wfuzz"
    
    Write-Host ""
}

# Exploitation Tools
function Install-ExploitTools {
    Write-Host "=== Installing Exploitation Tools ===" -ForegroundColor Blue
    Install-Tool "Metasploit Framework" "metasploit"
    
    # Python-based tools
    Install-PipPackage "Impacket" "impacket"
    
    Write-Host ""
}

# Forensics Tools
function Install-ForensicsTools {
    Write-Host "=== Installing Forensics Tools ===" -ForegroundColor Blue
    Install-Tool "Wireshark" "wireshark"
    Install-Tool "Sysinternals Suite" "sysinternals"
    
    # Volatility
    Install-PipPackage "Volatility3" "volatility3"
    
    Write-Host ""
}

# Password Tools
function Install-PasswordTools {
    Write-Host "=== Installing Password Attack Tools ===" -ForegroundColor Blue
    Install-Tool "Hashcat" "hashcat"
    Install-Tool "John the Ripper" "johntheripper"
    
    Write-Host ""
}

# WSL2 Setup for Linux tools
function Setup-WSL2 {
    Write-Host "=== Setting up WSL2 for Linux tools ===" -ForegroundColor Blue
    
    $wslInstalled = wsl --list 2>&1 | Select-String -Pattern "Ubuntu"
    
    if (-not $wslInstalled) {
        Write-Host "WSL2 not detected. Would you like to install Ubuntu in WSL2? [Y/n]: " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        
        if ($response -match '^[Yy]?$') {
            Write-Host "Enabling WSL features..." -ForegroundColor Yellow
            
            # Enable WSL feature
            dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
            
            # Enable Virtual Machine Platform
            dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
            
            # Install WSL2 kernel update
            Write-Host "Installing WSL2 kernel update..." -ForegroundColor Yellow
            $wslUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
            $wslUpdatePath = "$env:TEMP\wsl_update_x64.msi"
            Invoke-WebRequest -Uri $wslUpdateUrl -OutFile $wslUpdatePath
            Start-Process msiexec.exe -Wait -ArgumentList "/I $wslUpdatePath /quiet"
            
            # Set WSL2 as default
            wsl --set-default-version 2
            
            # Install Ubuntu
            Write-Host "Installing Ubuntu..." -ForegroundColor Yellow
            wsl --install -d Ubuntu
            
            Write-Host "✓ WSL2 and Ubuntu installed" -ForegroundColor Green
            Write-Host "! Please restart your computer and run this script again" -ForegroundColor Yellow
        }
        else {
            Write-Host "Skipping WSL2 setup" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✓ WSL2 with Ubuntu is already installed" -ForegroundColor Green
    }
    
    Write-Host ""
}

# Configure Windows Defender exclusions
function Configure-DefenderExclusions {
    Write-Host "=== Configuring Windows Defender Exclusions ===" -ForegroundColor Blue
    
    $toolsPath = "$env:ProgramData\chocolatey\lib"
    $scriptsPath = "$PWD"
    
    Write-Host "Adding Windows Defender exclusions for security tools..." -ForegroundColor Yellow
    Write-Host "This prevents false positives during security testing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Add exclusions? [Y/n]: " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -match '^[Yy]?$') {
        try {
            # Add path exclusions
            Add-MpPreference -ExclusionPath $toolsPath
            Add-MpPreference -ExclusionPath $scriptsPath
            
            # Add process exclusions for common tools
            $processes = @(
                "nmap.exe",
                "metasploit.exe",
                "msfconsole.exe",
                "hashcat.exe",
                "john.exe",
                "sqlmap.py"
            )
            
            foreach ($process in $processes) {
                Add-MpPreference -ExclusionProcess $process -ErrorAction SilentlyContinue
            }
            
            Write-Host "✓ Windows Defender exclusions configured" -ForegroundColor Green
        }
        catch {
            Write-Host "! Failed to configure some exclusions: $_" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Skipping Windows Defender exclusions" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Python setup
function Setup-Python {
    Write-Host "=== Checking Python Installation ===" -ForegroundColor Blue
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Python not found. Installing..." -ForegroundColor Yellow
        Install-Tool "Python" "python"
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    Write-Host ""
}

# Docker setup
function Setup-Docker {
    Write-Host "=== Setting up Docker Desktop ===" -ForegroundColor Blue
    
    $dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
    
    if (-not $dockerInstalled) {
        Write-Host "Would you like to install Docker Desktop? [Y/n]: " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        
        if ($response -match '^[Yy]?$') {
            Install-Tool "Docker Desktop" "docker-desktop"
            Write-Host "! Please restart your computer after installation" -ForegroundColor Yellow
        }
        else {
            Write-Host "Skipping Docker installation" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✓ Docker is already installed" -ForegroundColor Green
    }
    
    Write-Host ""
}

# Main installation logic
Setup-Python

switch ($Category) {
    "Network" {
        Install-NetworkTools
    }
    "Web" {
        Install-WebTools
    }
    "Exploit" {
        Install-ExploitTools
    }
    "Forensics" {
        Install-ForensicsTools
    }
    "Password" {
        Install-PasswordTools
    }
    "All" {
        Install-NetworkTools
        Install-WebTools
        Install-ExploitTools
        Install-ForensicsTools
        Install-PasswordTools
    }
}

# Optional components
Setup-WSL2
Setup-Docker
Configure-DefenderExclusions

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Log file: $LogFile" -ForegroundColor Blue
Write-Host ""
Write-Host "Important Notes:" -ForegroundColor Yellow
Write-Host "1. Some tools may require a system restart"
Write-Host "2. Ensure you have proper authorization before using these tools"
Write-Host "3. Windows Defender may flag some tools - exclusions recommended"
Write-Host "4. For Linux tools, use WSL2 Ubuntu"
Write-Host ""
Write-Host "Legal Warning:" -ForegroundColor Yellow
Write-Host "These tools are for educational and authorized security testing only."
Write-Host "Unauthorized access to computer systems is illegal."
Write-Host ""
