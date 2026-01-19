# tennis_dashboard (Streamlit on the server, Tailscale-only)

This is the **Phase 1** productionization: run Streamlit in Docker, bound only to your **Tailscale IP**, and connecting to the existing Postgres on the server.

Read policy first:
- `infra/tennis_dashboard/POLICY_DO_NOT_TOUCH_EXISTING_CONTAINERS.md`

## What it does

- Starts `tennis_dashboard_streamlit`
- Binds Streamlit to `DASHBOARD_BIND_IP:DASHBOARD_PORT` (default: `100.73.243.20:8501`)
- Uses **host networking** so the dashboard can connect to Postgres on `127.0.0.1:<POSTGRES_PORT>`

## Configure

```bash
cp infra/tennis_dashboard/tennis_dashboard.env.example infra/tennis_dashboard/tennis_dashboard.env
```

Edit:
- `DASHBOARD_BIND_IP` to your server's Tailscale IP (from `ip -4 addr show tailscale0`)
- `DASHBOARD_PORT` if 8501 is already taken
- `TENNIS_DB_URL` to match your Postgres port/user/pass/db (from `infra/tennis_dagster/tennis_dagster.env`)

## Start / stop

```bash
./infra/tennis_dashboard/scripts/up.sh
```

```bash
./infra/tennis_dashboard/scripts/down.sh
```

## Deploy workflow (git pull)

From the repo root:

```bash
git pull
./infra/tennis_dashboard/scripts/up.sh
```

This will rebuild the image and restart only `tennis_dashboard_streamlit`.





