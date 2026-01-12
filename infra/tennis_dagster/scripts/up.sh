#!/usr/bin/env bash
set -euo pipefail

# Bring up the tennis_dagster stack safely.
#
# HARD POLICY:
# - This script must NEVER stop/restart/remove any existing containers.
# - It only starts containers defined in infra/tennis_dagster/docker-compose.yml.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/preflight.sh"

echo "[tennis_dagster up] Starting stack (no side-effects on other containers)..."
docker compose \
  --project-directory "${ROOT_DIR}" \
  --env-file "${ROOT_DIR}/tennis_dagster.env" \
  -f "${ROOT_DIR}/docker-compose.yml" \
  up -d --build

echo "[tennis_dagster up] Done."


