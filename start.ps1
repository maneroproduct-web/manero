# Starts the Manero application: database, backend API, and frontend website.
#
#   .\start.ps1
#
# The database runs in the background. The API and website each open their own
# window - closing a window stops that piece.
#
# See START.md for the manual step-by-step equivalent and troubleshooting.

$ErrorActionPreference = 'Stop'

$root    = $PSScriptRoot
$pgCtl   = "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe"
$pgData  = Join-Path $root ".pgdata"
$backend = Join-Path $root "backend"
$front   = Join-Path $root "frontend"

# Probes IPv4 and IPv6. Uvicorn binds 127.0.0.1 while Vite binds ::1, so
# checking only one makes a perfectly healthy server look like it never started.
# The address family must be set on the constructor: a default TcpClient is
# IPv4-only on Windows PowerShell and will never reach ::1, whatever address
# you hand Connect().
function Test-Port([int]$Port) {
    $targets = @(
        @{ Family = [Net.Sockets.AddressFamily]::InterNetwork;   Address = '127.0.0.1' },
        @{ Family = [Net.Sockets.AddressFamily]::InterNetworkV6; Address = '::1' }
    )
    foreach ($t in $targets) {
        $c = New-Object Net.Sockets.TcpClient($t.Family)
        try { $c.Connect($t.Address, $Port); return $true } catch { } finally { $c.Dispose() }
    }
    return $false
}

# Waits for a service to come up, watching BOTH the port and the process we
# launched. Watching the port alone is not enough: if something unrelated is
# already sitting on it, a server that crashed on startup still looks like a
# success — right up until that other thing goes away and you're left with
# nothing. If our process exits first, that's a failure, whatever the port says.
function Wait-Started {
    param([int]$Port, [System.Diagnostics.Process]$Proc, [string]$Name)

    foreach ($i in 1..60) {
        Start-Sleep -Milliseconds 500

        if ($Proc -and $Proc.HasExited) {
            throw "$Name stopped straight after starting. Its window stayed open " +
                  "with the error - read it there. Common cause: the port is " +
                  "already taken by an older copy still running."
        }
        if (Test-Port $Port) { return }
    }

    throw "$Name did not come up on port $Port within 30 seconds. Check the window that opened."
}

Write-Host ""
Write-Host "  Manero" -ForegroundColor Yellow
Write-Host "  ------" -ForegroundColor DarkYellow

# --- 1. Database -----------------------------------------------------------
Write-Host "`n[1/3] Database ..." -NoNewline
if (Test-Port 5433) {
    Write-Host " already running" -ForegroundColor DarkGray
} else {
    if (-not (Test-Path $pgCtl))  { throw "PostgreSQL not found at $pgCtl" }
    if (-not (Test-Path $pgData)) { throw "Data folder missing: $pgData (see README, 'Database')" }

    # Fire and poll. Two traps here, both of which hang forever:
    #   `& pg_ctl ... | Out-Null`  - the postgres server inherits the pipe
    #                                handle and never closes it.
    #   Start-Process -Wait        - waits for every handle on the redirect
    #                                files to be released, grandchildren too.
    # So: launch detached, and let the port poll below decide when it is up.
    Start-Process -FilePath $pgCtl -WindowStyle Hidden `
        -ArgumentList @('-D', "`"$pgData`"", '-o', '"-p 5433"',
                        '-l', "`"$(Join-Path $pgData 'server.log')`"", 'start')

    $ok = $false
    foreach ($i in 1..20) { Start-Sleep -Milliseconds 500; if (Test-Port 5433) { $ok = $true; break } }
    if (-not $ok) { throw "Database did not start. Check $pgData\server.log" }
    Write-Host " started on port 5433" -ForegroundColor Green
}

# --- 2. Backend ------------------------------------------------------------
Write-Host "[2/3] Backend  ..." -NoNewline
if (Test-Port 8000) {
    Write-Host " already running" -ForegroundColor DarkGray
} else {
    $venv = Join-Path $backend ".venv\Scripts\python.exe"
    if (-not (Test-Path $venv)) { throw "Virtual environment missing. See START.md troubleshooting." }

    # -File with a script path, not -Command with an inline string: an
    # -ArgumentList array is joined with spaces and NOT re-quoted, so a
    # multi-word -Command gets torn apart and silently never runs.
    $proc = Start-Process powershell -PassThru -ArgumentList @(
        '-NoExit', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $root "scripts\run-backend.ps1")
    )

    Wait-Started -Port 8000 -Proc $proc -Name "API"
    Write-Host " started on port 8000" -ForegroundColor Green
}

# --- 3. Frontend -----------------------------------------------------------
Write-Host "[3/3] Website  ..." -NoNewline
if (Test-Port 5173) {
    Write-Host " already running" -ForegroundColor DarkGray
} else {
    if (-not (Test-Path (Join-Path $front "node_modules"))) {
        throw "Frontend dependencies missing. Run 'npm install' in $front"
    }

    $proc = Start-Process powershell -PassThru -ArgumentList @(
        '-NoExit', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $root "scripts\run-frontend.ps1")
    )

    Wait-Started -Port 5173 -Proc $proc -Name "Website"
    Write-Host " started on port 5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "  Shop      http://localhost:5173" -ForegroundColor Cyan
Write-Host "  API docs  http://localhost:8000/docs" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  To stop:  Ctrl+C in the two windows, then" -ForegroundColor DarkGray
Write-Host "              ./stop.sh    (Git Bash)" -ForegroundColor DarkGray
Write-Host "              .\stop.ps1   (PowerShell)" -ForegroundColor DarkGray
Write-Host ""

Start-Process "http://localhost:5173"
