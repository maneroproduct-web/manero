# Stops the Manero application.
#
#   .\stop.ps1
#
# The API and website run in their own windows - Ctrl+C in those, or close them.
# This script stops the database, which has no window of its own.

$pgCtl  = "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe"
$pgData = Join-Path $PSScriptRoot ".pgdata"

Write-Host "`nStopping the database ..." -NoNewline

if (-not (Test-Path $pgData)) {
    Write-Host " data folder not found, nothing to stop." -ForegroundColor DarkGray
    return
}

$status = & $pgCtl -D $pgData status 2>&1
if ($status -match "no server running") {
    Write-Host " already stopped." -ForegroundColor DarkGray
} else {
    & $pgCtl -D $pgData stop | Out-Null
    Write-Host " stopped." -ForegroundColor Green
}

Write-Host "`nIf the API or website are still running, press Ctrl+C in their windows.`n" -ForegroundColor DarkGray
