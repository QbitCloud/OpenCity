#!/usr/bin/env bash
# Refresh the OpenCity database: fetch the sources that are due, then write CSV exports.
#
#   scripts/refresh.sh                 # sources whose refresh interval has elapsed (what cron runs)
#   scripts/refresh.sh --all           # every enabled source now
#   scripts/refresh.sh -s smc_swm      # one source (repeatable)
#   scripts/refresh.sh --force         # ignore intervals and re-download already-seen documents
#   scripts/refresh.sh --no-export     # skip writing data/export/*.csv
#
# Safe to run from cron: only one refresh runs at a time (flock), output goes to
# data/logs/refresh-YYYY-MM-DD.log, and the exit code is non-zero if any source failed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${OPENCITY_DATA_DIR:-$ROOT/data}"
PY="${PYTHON:-python3}"
LOG_DIR="$DATA_DIR/logs"

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

# Build one command; it always has arguments, even on older macOS Bash.
refresh_command=("$PY" -m opencity refresh)
due_only=1
do_export=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      due_only=0
      ;;
    --due)
      due_only=1
      ;;
    -s|--source)
      if [[ $# -lt 2 ]]; then
        echo "missing source id after $1" >&2
        exit 2
      fi
      refresh_command+=(--source "$2")
      due_only=0
      shift
      ;;
    --force)
      refresh_command+=(--force)
      ;;
    --no-export)
      do_export=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1 (see --help)" >&2
      exit 2
      ;;
  esac
  shift
done

if [[ $due_only -eq 1 ]]; then
  refresh_command+=(--due)
fi

# --- preflight ---------------------------------------------------------------
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || { echo "python 3.9+ required (set PYTHON=...)" >&2; exit 2; }
command -v pdftotext >/dev/null || echo "warning: pdftotext not found (apt install poppler-utils); PDF sources will fail" >&2

if ! command -v flock >/dev/null; then
  echo "flock is required to prevent overlapping refreshes; install it before running this script" >&2
  exit 2
fi

mkdir -p "$LOG_DIR"
log="$LOG_DIR/refresh-$(date +%Y-%m-%d).log"

# --- one refresh at a time ---------------------------------------------------
exec 9>"$DATA_DIR/.refresh.lock"
if ! flock -n 9; then
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') another refresh is still running; skipping" >>"$log"
  exit 0
fi

# Show output on a terminal; stay quiet (log only) under cron.
out() {
  if [[ -t 1 ]]; then
    tee -a "$log"
  else
    cat >>"$log"
  fi
}

cd "$ROOT/pipeline"
set +e
{
  echo "=== $(date '+%Y-%m-%dT%H:%M:%S%z') ${refresh_command[*]}"
  "${refresh_command[@]}" 2>&1
} | out
status=${PIPESTATUS[0]}

if [[ $do_export -eq 1 ]]; then
  "$PY" -m opencity export 2>&1 | out
  [[ ${PIPESTATUS[0]} -eq 0 ]] || status=1
fi
set -e

find "$LOG_DIR" -name 'refresh-*.log' -mtime +60 -delete 2>/dev/null || true

if [[ $status -ne 0 ]]; then
  echo "refresh finished with errors (exit $status); see $log" >&2
fi
exit "$status"
