# Opens the project database in psql.
#
#   .\db.ps1                            interactive session
#   .\db.ps1 "SELECT * FROM orders"     run one query and exit
#
# Saves remembering the long psql path, the non-standard port (5433), and the
# credentials. See README "Looking at the database" for GUI options.

param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Query)

$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

if (-not (Test-Path $psql)) {
    Write-Host "psql not found at $psql" -ForegroundColor Red
    exit 1
}

$c = New-Object Net.Sockets.TcpClient
try { $c.Connect('127.0.0.1', 5433) }
catch {
    Write-Host "The database is not running on port 5433. Start it first:" -ForegroundColor Red
    Write-Host "  .\start.ps1"
    exit 1
}
finally { $c.Dispose() }

$env:PGPASSWORD = 'manero'

if ($Query) {
    & $psql -U manero -h 127.0.0.1 -p 5433 -d manero -w -c ($Query -join ' ')
} else {
    Write-Host "Connected to the 'manero' database. Type \dt to list tables, \q to quit." -ForegroundColor DarkGray
    & $psql -U manero -h 127.0.0.1 -p 5433 -d manero -w
}
