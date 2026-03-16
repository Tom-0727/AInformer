#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_FILE="${ROOT_DIR}/deploy/cron/ainformer.cron"

crontab "${CRON_FILE}"
echo "Installed crontab from ${CRON_FILE}"
crontab -l
