#!/usr/bin/env bash
# Opens the project database in psql.
#
#   ./db.sh                       interactive session
#   ./db.sh "SELECT * FROM orders"    run one query and exit
#
# Saves remembering the long psql path, the non-standard port (5433), and the
# credentials. See README "Looking at the database" for GUI options.

set -euo pipefail

PSQL="/c/Program Files/PostgreSQL/17/bin/psql.exe"
export PGPASSWORD=manero

if [ ! -x "$PSQL" ]; then
  echo "psql not found at $PSQL" >&2
  exit 1
fi

if ! (exec 3<>/dev/tcp/127.0.0.1/5433) 2>/dev/null; then
  echo "The database is not running on port 5433. Start it first:" >&2
  echo "  ./start.sh" >&2
  exit 1
fi

if [ $# -gt 0 ]; then
  exec "$PSQL" -U manero -h 127.0.0.1 -p 5433 -d manero -w -c "$*"
else
  echo "Connected to the 'manero' database. Type \\dt to list tables, \\q to quit."
  exec "$PSQL" -U manero -h 127.0.0.1 -p 5433 -d manero -w
fi
