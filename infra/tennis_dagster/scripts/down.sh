#!/usr/bin/env bash
set -euo pipefail

# Stop ONLY the tennis_dagster stack.
# This will not touch other docker stacks because we use an isolated compose project directory.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[tennis_dagster down] Stopping tennis_dagster containers only..."
docker compose \
  --project-directory "${ROOT_DIR}" \
  --env-file "${ROOT_DIR}/tennis_dagster.env" \
  -f "${ROOT_DIR}/docker-compose.yml" \
  down

echo "[tennis_dagster down] Done."


