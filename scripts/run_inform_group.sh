#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <morning|noon|evening>" >&2
  exit 1
fi

GROUP="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs/cron"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

mkdir -p "${LOG_DIR}"

cd "${ROOT_DIR}"

echo "[${TIMESTAMP}] start group=${GROUP}"
/home/ubuntu/.local/bin/uv run python main.py --group "${GROUP}"
STATUS=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] end group=${GROUP} status=${STATUS}"
exit "${STATUS}"
