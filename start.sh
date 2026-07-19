#!/usr/bin/env bash
# Starts the Manero application from Git Bash / WSL-style shells.
#
#   ./start.sh
#
# The actual work lives in start.ps1 — .ps1 files can only be interpreted by
# PowerShell, so running them directly in bash produces "command not found" and
# syntax errors. This wrapper hands the script to PowerShell for you.

set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PowerShell needs a Windows-style path (C:\...), not a Git Bash one (/c/...).
if command -v cygpath >/dev/null 2>&1; then
  script="$(cygpath -w "$here/start.ps1")"
else
  script="$here/start.ps1"
fi

exec powershell -ExecutionPolicy Bypass -File "$script"
