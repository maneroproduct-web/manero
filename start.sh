#!/usr/bin/env bash
# Starts the Manero application: database, backend API, and frontend website.
#
#   ./start.sh
#
# Works on Windows (Git Bash), Linux and macOS.
#
#   Windows  - hands off to start.ps1, which opens a window per service.
#              .ps1 files can only be interpreted by PowerShell, so running
#              them directly in bash gives "command not found" and syntax
#              errors. This wrapper does the handoff for you.
#   Linux /  - runs the services natively in the background, logging to
#   macOS      logs/ and recording PIDs so ./stop.sh can shut them down.
#
# See START.md for the manual step-by-step and troubleshooting.

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------- Windows ---

case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    if command -v cygpath >/dev/null 2>&1; then
      script="$(cygpath -w "$here/start.ps1")"
    else
      script="$here/start.ps1"
    fi
    exec powershell -ExecutionPolicy Bypass -File "$script"
    ;;
esac

# ------------------------------------------------------------ Linux/macOS ---

PGPORT=5433
PGDATA="$here/.pgdata"
LOGS="$here/logs"
RUN="$here/.run"

mkdir -p "$LOGS" "$RUN"

say()  { printf '%s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

port_open() {
  # bash's /dev/tcp works without netcat or lsof being installed.
  (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null
}

wait_for_port() {
  local port=$1 name=$2 pid=$3 tries=${4:-60}
  for _ in $(seq 1 "$tries"); do
    sleep 0.5
    # If the process died, the port will never open — say so now rather than
    # timing out in thirty seconds with a vaguer message.
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
      fail "$name exited during startup. Last lines of its log:
$(tail -n 15 "$LOGS/$name.log" 2>/dev/null || echo '  (no log)')"
    fi
    port_open "$port" && return 0
  done
  fail "$name did not come up on port $port. See $LOGS/$name.log"
}

need() { command -v "$1" >/dev/null 2>&1 || fail "$2"; }

say ""
say "  Manero"
say "  ------"

# --- 1. Database ------------------------------------------------------------

printf '\n[1/3] Database ... '

if port_open "$PGPORT"; then
  say "already running"
else
  need pg_ctl "pg_ctl not found. Install PostgreSQL, e.g.
  Debian/Ubuntu:  sudo apt install postgresql
  macOS (brew):   brew install postgresql@17
On Debian/Ubuntu the binaries are not on PATH by default; add them with:
  export PATH=\"/usr/lib/postgresql/17/bin:\$PATH\""

  # First run on this machine: create the project's own cluster. It lives in
  # the repo, is separate from any system PostgreSQL, and holds only this
  # project's development data.
  if [ ! -d "$PGDATA" ]; then
    say ""
    say "      No database found - creating one in .pgdata (first run only) ..."
    initdb -D "$PGDATA" -U postgres -E UTF8 --locale=C \
           --auth-local=trust --auth-host=trust >"$LOGS/initdb.log" 2>&1 \
      || fail "initdb failed. See $LOGS/initdb.log"
    printf '      '
  fi

  pg_ctl -D "$PGDATA" -o "-p $PGPORT" -l "$PGDATA/server.log" start \
      >/dev/null 2>&1 || true
  wait_for_port "$PGPORT" "database" "" 40
  say "started on port $PGPORT"
fi

# Create the app's role and database if this cluster is brand new. Both guarded,
# so this is a no-op on every run after the first.
if ! psql -U postgres -h 127.0.0.1 -p "$PGPORT" -d postgres -tAc \
       "SELECT 1 FROM pg_roles WHERE rolname='manero'" 2>/dev/null | grep -q 1; then
  say "      Creating the 'manero' user and database ..."
  psql -U postgres -h 127.0.0.1 -p "$PGPORT" -d postgres \
       -c "CREATE ROLE manero LOGIN PASSWORD 'manero';" >/dev/null
  psql -U postgres -h 127.0.0.1 -p "$PGPORT" -d postgres \
       -c "CREATE DATABASE manero OWNER manero;" >/dev/null
fi

# --- 2. Backend -------------------------------------------------------------

printf '[2/3] Backend  ... '

if port_open 8000; then
  say "already running"
else
  venv="$here/backend/.venv/bin/python"
  [ -x "$venv" ] || fail "Python environment missing. Create it with:
  cd backend
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt"

  # Migrations are cheap when there is nothing to do, and skipping them is the
  # classic cause of \"relation does not exist\" on a fresh clone.
  (cd "$here/backend" && "$venv" -m alembic upgrade head) \
      >"$LOGS/migrate.log" 2>&1 \
    || fail "Database migration failed. See $LOGS/migrate.log"

  (cd "$here/backend" && exec "$venv" -m uvicorn app.main:app --reload --port 8000) \
      >"$LOGS/backend.log" 2>&1 &
  echo $! >"$RUN/backend.pid"

  wait_for_port 8000 "backend" "$(cat "$RUN/backend.pid")"
  say "started on port 8000"
fi

# --- 3. Frontend ------------------------------------------------------------

printf '[3/3] Website  ... '

if port_open 5173; then
  say "already running"
else
  [ -d "$here/frontend/node_modules" ] || fail "Frontend dependencies missing. Install them with:
  cd frontend && npm install"

  (cd "$here/frontend" && exec npm run dev) >"$LOGS/frontend.log" 2>&1 &
  echo $! >"$RUN/frontend.pid"

  wait_for_port 5173 "frontend" "$(cat "$RUN/frontend.pid")"
  say "started on port 5173"
fi

say ""
say "  Shop      http://localhost:5173"
say "  API docs  http://localhost:8000/docs"
say ""
say "  Logs      $LOGS/backend.log, $LOGS/frontend.log"
say "  To stop   ./stop.sh"
say ""
