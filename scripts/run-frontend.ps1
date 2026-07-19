# Runs the Manero website. Launched by start.ps1, but you can run it directly.
# Press Ctrl+C to stop.

$root = Split-Path $PSScriptRoot -Parent
Set-Location (Join-Path $root "frontend")

Write-Host ""
Write-Host "  Manero website  -  http://localhost:5173" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

npm run dev
