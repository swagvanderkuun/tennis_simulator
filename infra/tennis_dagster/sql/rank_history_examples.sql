-- Example queries to compare Elo rankings over time.
-- Run inside tennis_dagster_postgres:
--   docker exec -i tennis_dagster_postgres psql -U tennis -d tennis_simulator < infra/tennis_dagster/sql/rank_history_examples.sql

-- Current ratings table (always overwritten/upserted on scrape)
SELECT gender, count(*) AS rows, min(as_of) AS as_of_min, max(as_of) AS as_of_max
FROM tennis.elo_current
GROUP BY 1
ORDER BY 1;

-- Latest two successful snapshots per gender
WITH latest AS (
  SELECT
    gender,
    id AS snapshot_id,
    scraped_at,
    row_number() OVER (PARTITION BY gender ORDER BY scraped_at DESC) AS rn
  FROM tennis.elo_snapshots
  WHERE status = 'success'
)
SELECT gender, snapshot_id, scraped_at
FROM latest
WHERE rn <= 2
ORDER BY gender, scraped_at DESC;

-- Elo-rank movement between the latest two snapshots (per gender)
WITH latest AS (
  SELECT
    gender,
    id AS snapshot_id,
    scraped_at,
    row_number() OVER (PARTITION BY gender ORDER BY scraped_at DESC) AS rn
  FROM tennis.elo_snapshots
  WHERE status = 'success'
),
pair AS (
  SELECT
    gender,
    max(CASE WHEN rn = 1 THEN snapshot_id END) AS s_new,
    max(CASE WHEN rn = 2 THEN snapshot_id END) AS s_old
  FROM latest
  WHERE rn <= 2
  GROUP BY gender
),
old_r AS (
  SELECT
    p.gender,
    pl.canonical_name,
    r.elo_rank AS elo_rank_old
  FROM pair p
  JOIN tennis.elo_ratings r ON r.snapshot_id = p.s_old
  JOIN tennis.players pl ON pl.id = r.player_id
),
new_r AS (
  SELECT
    p.gender,
    pl.canonical_name,
    r.elo_rank AS elo_rank_new
  FROM pair p
  JOIN tennis.elo_ratings r ON r.snapshot_id = p.s_new
  JOIN tennis.players pl ON pl.id = r.player_id
)
SELECT
  n.gender,
  n.canonical_name,
  o.elo_rank_old,
  n.elo_rank_new,
  (o.elo_rank_old - n.elo_rank_new) AS elo_rank_change_positive_is_improvement
FROM new_r n
JOIN old_r o
  ON o.gender = n.gender
 AND o.canonical_name = n.canonical_name
WHERE o.elo_rank_old IS NOT NULL AND n.elo_rank_new IS NOT NULL
ORDER BY n.gender, elo_rank_change_positive_is_improvement DESC, n.elo_rank_new ASC
LIMIT 50;

-- Full history for a single player (edit the name)
-- Example:
--   \set player 'Iga Swiatek'
--   \set gender 'women'
\echo '--- Set these psql vars before running this section, e.g.:'
\echo \"\\set player 'Iga Swiatek'\\n\\set gender 'women'\"
-- SELECT
--   s.scraped_at,
--   r.elo_rank,
--   r.elo,
--   r.yelo,
--   r.rank AS tour_rank
-- FROM tennis.players p
-- JOIN tennis.elo_ratings r ON r.player_id = p.id
-- JOIN tennis.elo_snapshots s ON s.id = r.snapshot_id
-- WHERE p.gender = :'gender' AND p.canonical_name = :'player' AND s.status = 'success'
-- ORDER BY s.scraped_at;


