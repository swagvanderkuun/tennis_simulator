#!/usr/bin/env bash
set -euo pipefail

# Preflight checks for the tennis_dashboard stack.
# HARD POLICY: never touch other stacks; only inspect for conflicts.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/tennis_dashboard.env"
ENV_EXAMPLE="${ROOT_DIR}/tennis_dashboard.env.example"

RESERVED_CONTAINERS=(
  "tennis_dashboard_streamlit"
)

log() { echo "[tennis_dashboard preflight] $*"; }
die() { echo "[tennis_dashboard preflight] ERROR: $*" >&2; exit 1; }

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

docker_container_exists() {
  docker ps -a --format '{{.Names}}' | grep -qx "$1"
}

docker_container_compose_project() {
  docker inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' "$1" 2>/dev/null || true
}

port_in_use() {
  local ip="$1"
  local port="$2"
  # Check host listeners
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "(${ip}|0.0.0.0|\\[::\\]):${port}\$"; then
    return 0
  fi
  # Check docker published ports (best-effort)
  if docker ps --format '{{.Ports}}' | grep -Eq "(:|\\.)${port}->"; then
    return 0
  fi
  return 1
}

main() {
  require_cmd docker
  require_cmd ss

  if [[ ! -f "${ENV_FILE}" ]]; then
    log "No ${ENV_FILE} found; creating from example."
    cp "${ENV_EXAMPLE}" "${ENV_FILE}"
  fi

  # shellcheck disable=SC1090
  set -a
  source "${ENV_FILE}"
  set +a

  : "${DASHBOARD_BIND_IP:=100.73.243.20}"
  : "${DASHBOARD_PORT:=8501}"

  log "Checking reserved container names..."
  for name in "${RESERVED_CONTAINERS[@]}"; do
    if docker_container_exists "$name"; then
      project="$(docker_container_compose_project "$name")"
      if [[ "$project" != "tennis_dashboard" ]]; then
        die "Container name already exists: ${name} (compose project='${project:-unknown}'). Refusing to run."
      fi
      log "Found existing ${name} (compose project=tennis_dashboard). Preflight will proceed (idempotent run)."
    fi
  done

  log "Checking bind address..."
  if ! ip -4 addr show | grep -q "${DASHBOARD_BIND_IP}"; then
    die "DASHBOARD_BIND_IP=${DASHBOARD_BIND_IP} not found on host. Set it to your server's Tailscale IP (tailscale0)."
  fi

  log "Checking port availability on ${DASHBOARD_BIND_IP}:${DASHBOARD_PORT}..."
  if port_in_use "${DASHBOARD_BIND_IP}" "${DASHBOARD_PORT}"; then
    die "Port ${DASHBOARD_PORT} appears to be in use. Choose a free DASHBOARD_PORT in tennis_dashboard.env."
  fi

  log "Preflight OK."
  log "Dashboard will be reachable at http://${DASHBOARD_BIND_IP}:${DASHBOARD_PORT}"
}

main "$@"


