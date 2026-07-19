#!/usr/bin/env bash
# Stops the Manero database from Git Bash. See start.sh for why this wrapper
# exists. The API and website stop with Ctrl+C in their own windows.

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v cygpath >/dev/null 2>&1; then
  script="$(cygpath -w "$here/stop.ps1")"
else
  script="$here/stop.ps1"
fi

exec powershell -ExecutionPolicy Bypass -File "$script"
