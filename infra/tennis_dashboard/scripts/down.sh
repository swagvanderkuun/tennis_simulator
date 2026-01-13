#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[tennis_dashboard down] Stopping tennis_dashboard containers only..."
docker compose \
  --project-directory "${ROOT_DIR}" \
  --env-file "${ROOT_DIR}/tennis_dashboard.env" \
  -f "${ROOT_DIR}/docker-compose.yml" \
  down

echo "[tennis_dashboard down] Done."


