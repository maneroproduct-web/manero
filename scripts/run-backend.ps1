# Runs the Manero API. Launched by start.ps1, but you can run it directly.
# Press Ctrl+C to stop.

$root = Split-Path $PSScriptRoot -Parent
Set-Location (Join-Path $root "backend")

Write-Host ""
Write-Host "  Manero API  -  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
