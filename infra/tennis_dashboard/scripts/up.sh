#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/preflight.sh"

echo "[tennis_dashboard up] Starting dashboard (no side-effects on other containers)..."
docker compose \
  --project-directory "${ROOT_DIR}" \
  --env-file "${ROOT_DIR}/tennis_dashboard.env" \
  -f "${ROOT_DIR}/docker-compose.yml" \
  up -d --build

echo "[tennis_dashboard up] Done."



