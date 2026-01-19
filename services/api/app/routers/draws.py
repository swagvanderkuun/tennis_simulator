"""
Draws router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.db.cache import cache_get, cache_set
from app.schemas.tournament import DrawSnapshot, DrawMatch, TournamentProbabilities, DrawEntry
from app.services.match_simulator import EloMatchSimulator, PlayerLite, EloWeights

router = APIRouter()


@router.get("/{tournament_id}/latest", response_model=Optional[DrawSnapshot])
async def get_latest_draw_snapshot(
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """Get the latest draw snapshot for a tournament"""
    cache_key = f"draws:latest_snapshot:{tournament_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return DrawSnapshot(**cached)
    sql = """
        SELECT id, source_id, scraped_at, status
        FROM tennis.draw_snapshots
        WHERE source_id = :tournament_id AND status = 'success'
        ORDER BY scraped_at DESC, id DESC
        LIMIT 1
    """
    
    try:
        result = db.execute(text(sql), {"tournament_id": tournament_id})
        row = result.mappings().first()
        if not row:
            return None
        data = dict(row)
        cache_set(cache_key, data, ttl=120)
        return DrawSnapshot(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{snapshot_id}/tree", response_model=List[DrawMatch])
async def get_draw_tree(
    snapshot_id: int,
    db: Session = Depends(get_db),
):
    """Get the draw match tree for a snapshot"""
    cache_key = f"draws:tree:{snapshot_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [DrawMatch(**row) for row in cached]
    sql = """
        SELECT
            m.id,
            m.round,
            m.match_index,
            m.child_match1_id,
            m.child_match2_id,
            e1.player_name as player1_name,
            COALESCE(e1.is_bye, 0) = 1 as player1_bye,
            e2.player_name as player2_name,
            COALESCE(e2.is_bye, 0) = 1 as player2_bye
        FROM tennis.draw_matches m
        LEFT JOIN tennis.draw_entries e1 ON e1.id = m.entry1_id
        LEFT JOIN tennis.draw_entries e2 ON e2.id = m.entry2_id
        WHERE m.snapshot_id = :snapshot_id
        ORDER BY m.round, m.match_index
    """
    
    try:
        result = db.execute(text(sql), {"snapshot_id": snapshot_id})
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        cache_set(cache_key, data, ttl=300)
        return [DrawMatch(**row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{snapshot_id}/entries", response_model=List[DrawEntry])
async def get_draw_entries(
    snapshot_id: int,
    db: Session = Depends(get_db),
):
    """Get draw entries (players) for a snapshot"""
    cache_key = f"draws:entries:{snapshot_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [DrawEntry(**row) for row in cached]
    sql = """
        SELECT id, part_index, slot_index, seed_text, player_name, is_bye
        FROM tennis.draw_entries
        WHERE snapshot_id = :snapshot_id
        ORDER BY part_index, slot_index
    """
    try:
        result = db.execute(text(sql), {"snapshot_id": snapshot_id})
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        cache_set(cache_key, data, ttl=300)
        return [DrawEntry(**row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{snapshot_id}/probabilities", response_model=List[TournamentProbabilities])
async def get_draw_probabilities(
    snapshot_id: int,
    num_simulations: int = Query(1000, ge=100, le=10000),
    db: Session = Depends(get_db),
):
    """Get tournament probabilities for all players in a draw"""
    cache_key = f"draws:probabilities:{snapshot_id}:{num_simulations}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [TournamentProbabilities(**row) for row in cached]
    # Load draw entries
    entries_sql = """
        SELECT part_index, slot_index, player_name, is_bye
        FROM tennis.draw_entries
        WHERE snapshot_id = :snapshot_id
        ORDER BY part_index, slot_index
    """
    # Load gender/tour from draw source
    gender_sql = """
        SELECT ds.tour
        FROM tennis.draw_snapshots snap
        JOIN tennis.draw_sources ds ON ds.id = snap.source_id
        WHERE snap.id = :snapshot_id
        LIMIT 1
    """
    try:
        tour_row = db.execute(text(gender_sql), {"snapshot_id": snapshot_id}).mappings().first()
        if not tour_row:
            raise HTTPException(status_code=404, detail="Draw snapshot not found")
        gender = "men" if tour_row["tour"] == "atp" else "women"

        entries = db.execute(text(entries_sql), {"snapshot_id": snapshot_id}).mappings().all()
        if not entries:
            return []

        # Load player ratings for all players in draw
        names = [e["player_name"] for e in entries if e["player_name"] and not e["is_bye"]]
        if not names:
            return []

        player_sql = """
            SELECT
              c.player_name as name,
              c.elo, c.helo, c.celo, c.gelo,
              COALESCE(
                c.form,
                0.75 * COALESCE(c.form_4w, 0) + 0.25 * COALESCE(c.form_12w, 0),
                0
              ) AS form
            FROM tennis.elo_current c
            WHERE c.gender = :gender AND c.player_name = ANY(:names)
        """
        rows = db.execute(
            text(player_sql),
            {"gender": gender, "names": names},
        ).mappings().all()
        player_map = {
            r["name"]: PlayerLite(
                name=r["name"],
                tier="D",
                elo=r.get("elo"),
                helo=r.get("helo"),
                celo=r.get("celo"),
                gelo=r.get("gelo"),
                form=r.get("form") or 0.0,
            )
            for r in rows
        }

        # Build ordered players list (with BYEs)
        ordered = []
        for e in entries:
            if int(e["is_bye"]) == 1 or str(e["player_name"]).upper() == "BYE":
                ordered.append({"is_bye": True, "name": "BYE"})
            else:
                name = e["player_name"]
                ordered.append({"is_bye": False, "player": player_map.get(name)})

        simulator = EloMatchSimulator(weights=EloWeights())

        from collections import Counter
        winners_c = Counter()
        finalists_c = Counter()
        semifinalists_c = Counter()
        quarterfinalists_c = Counter()

        def play_round(players_list):
            winners = []
            for i in range(0, len(players_list), 2):
                p1 = players_list[i]
                p2 = players_list[i + 1]
                if p1.get("is_bye"):
                    winners.append(p2)
                    continue
                if p2.get("is_bye"):
                    winners.append(p1)
                    continue
                pl1 = p1["player"] or PlayerLite(name="BYE", tier="D")
                pl2 = p2["player"] or PlayerLite(name="BYE", tier="D")
                winner, _, _ = simulator.simulate_match(pl1, pl2, gender)
                winners.append({"is_bye": False, "player": pl1 if winner.name == pl1.name else pl2})
            return winners

        for _ in range(num_simulations):
            current = ordered
            while len(current) > 1:
                next_players = play_round(current)
                if len(next_players) == 8:
                    for p in next_players:
                        if not p.get("is_bye") and p.get("player"):
                            quarterfinalists_c[p["player"].name] += 1
                if len(next_players) == 4:
                    for p in next_players:
                        if not p.get("is_bye") and p.get("player"):
                            semifinalists_c[p["player"].name] += 1
                if len(next_players) == 2:
                    for p in next_players:
                        if not p.get("is_bye") and p.get("player"):
                            finalists_c[p["player"].name] += 1
                if len(next_players) == 1:
                    p = next_players[0]
                    if not p.get("is_bye") and p.get("player"):
                        winners_c[p["player"].name] += 1
                current = next_players

        total = float(num_simulations)
        probabilities = []
        all_names = set([n for n in names])
        for name in all_names:
            probabilities.append(TournamentProbabilities(
                player_name=name,
                win_prob=winners_c[name] / total,
                final_prob=finalists_c[name] / total,
                semi_prob=semifinalists_c[name] / total,
                qf_prob=quarterfinalists_c[name] / total,
            ))

        probabilities.sort(key=lambda x: x.win_prob, reverse=True)
        cache_set(cache_key, [p.model_dump() for p in probabilities], ttl=300)
        return probabilities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

