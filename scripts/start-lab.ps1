<#
Simple JupyterLab launcher for Agentic Assistants (Windows PowerShell)

Usage:
  .\scripts\start-lab.ps1 [-Port 8888]
#>

param(
    [int]$Port = 8888
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host "Starting JupyterLab from $ProjectDir" -ForegroundColor Cyan
Write-Host "Port: $Port"

Set-Location $ProjectDir

# Ensure directories exist
New-Item -ItemType Directory -Path "notebooks" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "data" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "mlruns" -ErrorAction SilentlyContinue | Out-Null

# Launch JupyterLab
$logPath = Join-Path $ProjectDir "jupyterlab.log"
$jupyterCmd = "jupyter"
$args = @(
    "lab",
    "--ip", "127.0.0.1",
    "--port", "$Port",
    "--no-browser",
    "--NotebookApp.token=''",
    "--NotebookApp.password=''",
    "--NotebookApp.notebook_dir=$ProjectDir"
)

Start-Process -FilePath $jupyterCmd -ArgumentList $args -RedirectStandardOutput $logPath -RedirectStandardError $logPath -PassThru -WindowStyle Hidden | ForEach-Object {
    $_.Id | Out-File ".jupyter.pid" -Encoding ascii
    Write-Host "JupyterLab started (PID: $($_.Id)) at http://localhost:$Port/lab" -ForegroundColor Green
    Write-Host "Logs: $logPath"
}
