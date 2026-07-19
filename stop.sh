#!/usr/bin/env bash
# Stops the Manero application.
#
#   ./stop.sh
#
# Windows      - stops the database via stop.ps1. The API and website run in
#                their own windows; press Ctrl+C there or close them.
# Linux/macOS  - stops the API and website (started in the background by
#                start.sh) and then the database.

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------- Windows ---

case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    if command -v cygpath >/dev/null 2>&1; then
      script="$(cygpath -w "$here/stop.ps1")"
    else
      script="$here/stop.ps1"
    fi
    exec powershell -ExecutionPolicy Bypass -File "$script"
    ;;
esac

# ------------------------------------------------------------ Linux/macOS ---

PGDATA="$here/.pgdata"
RUN="$here/.run"

stop_pidfile() {
  local name=$1 file="$RUN/$2.pid"

  printf 'Stopping %-9s ... ' "$name"
  if [ ! -f "$file" ]; then
    echo "not running"
    return
  fi

  local pid
  pid="$(cat "$file")"

  if ! kill -0 "$pid" 2>/dev/null; then
    echo "already stopped"
    rm -f "$file"
    return
  fi

  # Kill the whole process group: `npm run dev` spawns vite as a child, and
  # signalling only npm leaves vite holding port 5173.
  kill -TERM -- "-$(ps -o pgid= "$pid" | tr -d ' ')" 2>/dev/null || kill "$pid" 2>/dev/null || true

  for _ in $(seq 1 20); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.25
  done
  kill -9 "$pid" 2>/dev/null || true

  rm -f "$file"
  echo "stopped"
}

echo ""
stop_pidfile "website" frontend
stop_pidfile "API"     backend

printf 'Stopping %-9s ... ' "database"
if [ ! -d "$PGDATA" ]; then
  echo "no data directory, nothing to stop"
elif pg_ctl -D "$PGDATA" status >/dev/null 2>&1; then
  pg_ctl -D "$PGDATA" stop >/dev/null 2>&1 && echo "stopped" || echo "failed"
else
  echo "already stopped"
fi

echo ""
