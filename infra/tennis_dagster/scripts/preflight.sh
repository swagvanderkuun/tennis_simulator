#!/usr/bin/env bash
set -euo pipefail

# Preflight checks for the tennis_dagster stack.
#
# HARD POLICY:
# - We ONLY inspect Docker/ports.
# - We NEVER stop/restart/remove any existing containers.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/tennis_dagster.env"
ENV_EXAMPLE="${ROOT_DIR}/tennis_dagster.env.example"

RESERVED_CONTAINERS=(
  "tennis_dagster_postgres"
  "tennis_dagster_webserver"
  "tennis_dagster_daemon"
)

log() { echo "[tennis_dagster preflight] $*"; }
die() { echo "[tennis_dagster preflight] ERROR: $*" >&2; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

docker_container_exists() {
  docker ps -a --format '{{.Names}}' | grep -qx "$1"
}

docker_container_compose_project() {
  # Prints the compose project label if present, otherwise prints empty string.
  docker inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' "$1" 2>/dev/null || true
}

docker_host_port() {
  # Usage: docker_host_port <container_name> <container_port_proto>
  # Example: docker_host_port tennis_dagster_webserver 3000/tcp  -> 3001
  local name="$1"
  local port_proto="$2"
  local mapping
  mapping="$(docker port "$name" "$port_proto" 2>/dev/null | head -n 1 || true)"
  if [[ -z "$mapping" ]]; then
    echo ""
    return 0
  fi
  # mapping looks like "0.0.0.0:3001" or "[::]:3001"
  echo "$mapping" | awk -F: '{print $NF}'
}

port_in_use() {
  local port="$1"
  # Check TCP listeners (host processes)
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq ":${port}\$"; then
    return 0
  fi
  # Check docker published ports (in case bound to specific interfaces)
  if docker ps --format '{{.Ports}}' | grep -Eq "(:|\\.)${port}->"; then
    return 0
  fi
  return 1
}

find_free_port() {
  local start="$1"
  local end="$2"
  local p
  for p in $(seq "$start" "$end"); do
    if ! port_in_use "$p"; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

main() {
  require_cmd docker
  require_cmd ss

  log "Checking reserved container names..."
  stack_exists="true"
  for name in "${RESERVED_CONTAINERS[@]}"; do
    if docker_container_exists "$name"; then
      project="$(docker_container_compose_project "$name")"
      if [[ "$project" != "tennis_dagster" ]]; then
        die "Container name already exists: ${name} (compose project='${project:-unknown}'). Refusing to run to avoid touching other stacks."
      fi
      log "Found existing ${name} (compose project=tennis_dagster). Preflight will proceed (idempotent run)."
    else
      stack_exists="false"
    fi
  done

if [[ ! -f "${ENV_FILE}" ]]; then
    log "No ${ENV_FILE} found; creating from example."
    cp "${ENV_EXAMPLE}" "${ENV_FILE}"
  fi

  # shellcheck disable=SC1090
  set -a
  source "${ENV_FILE}"
  set +a

  : "${DAGSTER_WEB_PORT:=3001}"
  : "${POSTGRES_PORT:=5433}"

  # If the stack already exists, DO NOT "port-bump" due to ports being in use by this stack.
  # Instead, sync ENV_FILE to actual running ports so subsequent commands are consistent.
  if [[ "${stack_exists}" == "true" ]]; then
    log "Existing tennis_dagster stack detected; syncing env ports to the running containers."
    running_web_port="$(docker_host_port tennis_dagster_webserver 3000/tcp)"
    running_pg_port="$(docker_host_port tennis_dagster_postgres 5432/tcp)"

    if [[ -n "${running_web_port}" ]]; then
      DAGSTER_WEB_PORT="${running_web_port}"
    fi
    if [[ -n "${running_pg_port}" ]]; then
      POSTGRES_PORT="${running_pg_port}"
    fi

    log "Writing synced ports back to ${ENV_FILE}"
    if grep -q '^DAGSTER_WEB_PORT=' "${ENV_FILE}"; then
      sed -i "s/^DAGSTER_WEB_PORT=.*/DAGSTER_WEB_PORT=${DAGSTER_WEB_PORT}/" "${ENV_FILE}"
    else
      echo "DAGSTER_WEB_PORT=${DAGSTER_WEB_PORT}" >> "${ENV_FILE}"
    fi

    if grep -q '^POSTGRES_PORT=' "${ENV_FILE}"; then
      sed -i "s/^POSTGRES_PORT=.*/POSTGRES_PORT=${POSTGRES_PORT}/" "${ENV_FILE}"
    else
      echo "POSTGRES_PORT=${POSTGRES_PORT}" >> "${ENV_FILE}"
    fi

    log "Preflight OK."
    log "Dagit will be available on http://localhost:${DAGSTER_WEB_PORT}"
    log "Postgres will be bound on localhost:${POSTGRES_PORT}"
    return 0
  fi

  # Dagster web port: we keep 3001 if possible, otherwise bump in 3001-3099
  if port_in_use "${DAGSTER_WEB_PORT}"; then
    log "Port ${DAGSTER_WEB_PORT} is in use; searching for a free Dagster port..."
    new_port="$(find_free_port 3001 3099 || true)"
    [[ -n "${new_port}" ]] || die "No free port found in range 3001-3099 for Dagster."
    DAGSTER_WEB_PORT="${new_port}"
    log "Selected DAGSTER_WEB_PORT=${DAGSTER_WEB_PORT}"
  fi

  # Postgres port: must not collide; search 5434-5499 by default
  if port_in_use "${POSTGRES_PORT}"; then
    log "Port ${POSTGRES_PORT} is in use; searching for a free Postgres port..."
    new_pg_port="$(find_free_port 5434 5499 || true)"
    [[ -n "${new_pg_port}" ]] || die "No free port found in range 5434-5499 for Postgres."
    POSTGRES_PORT="${new_pg_port}"
    log "Selected POSTGRES_PORT=${POSTGRES_PORT}"
  fi

  # Persist chosen ports back into ENV_FILE (idempotent edits)
  # We never write secrets here beyond what user already put in the file.
  log "Writing resolved ports back to ${ENV_FILE}"
  if grep -q '^DAGSTER_WEB_PORT=' "${ENV_FILE}"; then
    sed -i "s/^DAGSTER_WEB_PORT=.*/DAGSTER_WEB_PORT=${DAGSTER_WEB_PORT}/" "${ENV_FILE}"
  else
    echo "DAGSTER_WEB_PORT=${DAGSTER_WEB_PORT}" >> "${ENV_FILE}"
  fi

  if grep -q '^POSTGRES_PORT=' "${ENV_FILE}"; then
    sed -i "s/^POSTGRES_PORT=.*/POSTGRES_PORT=${POSTGRES_PORT}/" "${ENV_FILE}"
  else
    echo "POSTGRES_PORT=${POSTGRES_PORT}" >> "${ENV_FILE}"
  fi

  log "Preflight OK."
  log "Dagit will be available on http://localhost:${DAGSTER_WEB_PORT}"
  log "Postgres will be bound on localhost:${POSTGRES_PORT}"
}

main "$@"


