# tennis_dagster (isolated Dagster + Postgres stack)

This folder contains a **separate, isolated** Dagster + Postgres Docker stack dedicated to tennis scraping.

Read the policy first:

- `infra/tennis_dagster/POLICY_DO_NOT_TOUCH_EXISTING_STACKS.md`

## Why this exists

- You already run other Dagster/Postgres containers on this host.
- This stack is designed to **never** touch those containers and to **avoid port/name conflicts**.

## Quick start

1) Start safely (recommended):

```bash
./infra/tennis_dagster/scripts/up.sh
```

This runs a preflight that:

- refuses to run if container names would collide
- auto-selects free host ports if needed (writes `infra/tennis_dagster/tennis_dagster.env`)

2) Open Dagit:

- `http://localhost:<DAGSTER_WEB_PORT>`

## Run a draw scrape with a URL (manual initial draw)

In Dagit, run the job `scrape_draw_job` and provide run config:

```yaml
ops:
  scrape_draw_op:
    config:
      source_url: "https://www.tennisabstract.com/current/2026ATPAuckland.html"
```

## Stop this stack

```bash
./infra/tennis_dagster/scripts/down.sh
```

## Configuration

Copy and edit the env example:

```bash
cp infra/tennis_dagster/tennis_dagster.env.example infra/tennis_dagster/tennis_dagster.env
```

Ports are intentionally non-default:

- Dagit: defaults to **3001** (auto bumps within 3001-3099 if needed)
- Postgres: defaults to **5433** but will auto-bump to **5434-5499** if needed

## Notes

- Dagster instance storage uses the local filesystem under `infra/tennis_dagster/dagster_home/`.
- The Postgres in this stack is intended for **application data** (scraped Elo/draw DB).


