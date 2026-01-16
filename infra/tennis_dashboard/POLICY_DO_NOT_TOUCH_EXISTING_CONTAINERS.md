# Policy: Do Not Touch Existing Containers (Dagster/Postgres/Website)

This server already hosts other containers (including Dagster and an existing website).

## Hard rules

- **NEVER stop/restart/remove/reconfigure any existing Dagster containers** (e.g. `dagster_*`).
- **NEVER stop/restart/remove/reconfigure any existing Postgres containers**.
- **NEVER bind to ports already in use** by other containers (avoid conflicts).
- This dashboard stack must be isolated by:
  - Unique container names: `tennis_dashboard_streamlit`
  - Binding only to a chosen host IP + port (default is Tailscale IP only)

## Allowed actions

- Create/manage only the containers defined in `infra/tennis_dashboard/docker-compose.yml`.
- Inspect Docker state to detect conflicts.




