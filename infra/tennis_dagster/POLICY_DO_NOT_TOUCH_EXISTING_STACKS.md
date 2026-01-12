# Policy: Do Not Touch Existing Dagster/Postgres Stacks

This repository contains (or may be used alongside) **other** Dagster and Postgres Docker stacks.

## Hard rules

- **NEVER stop, restart, remove, or reconfigure any existing Dagster containers.**
- **NEVER stop, restart, remove, or reconfigure any existing Postgres containers.**
- This stack must be **isolated** via:
  - **Unique `container_name`s** (no collisions)
  - **Non-default host ports** (no collisions)
- If conflicts are detected, we **fail fast** or **switch to free ports**.
  - We do **not** resolve conflicts by touching other containers.

## What this stack is allowed to do

- Create and manage only these containers:
  - `tennis_dagster_postgres`
  - `tennis_dagster_webserver`
  - `tennis_dagster_daemon`
- Bind only its own host ports (defaults: **Dagit 3001**, **Postgres 5433**).

## How conflicts are prevented

The startup scripts in `infra/tennis_dagster/scripts/`:

- **Inspect** Docker for existing containers with the reserved names above.
- **Inspect** the host for port usage (including ports already exposed by other Docker containers).
- If a conflict exists, scripts will:
  - **Exit** with a clear message, or
  - **Auto-pick** the next available port in a safe range and write it to `infra/tennis_dagster/.env`.


