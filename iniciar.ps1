$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not $env:PORT) { $env:PORT = '5002' }
python app.py
