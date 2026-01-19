"""
Scorito router
"""
from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path

from app.db.session import get_db
from app.db.cache import cache_get, cache_set
from app.schemas.scorito import ScoritoRequest, ScoritoResult, ScoritoValuePick, ScoringRules
from app.services.match_simulator import EloMatchSimulator, PlayerLite, EloWeights

router = APIRouter()


def parse_scorito_scoring() -> Tuple[dict, list]:
    """Load Scorito scoring rules from data/import/scoring.txt if available"""
    scoring_path = None
    here = Path(__file__).resolve()
    for idx in range(1, 6):
        try:
            candidate = here.parents[idx] / "data" / "import" / "scoring.txt"
            if candidate.exists():
                scoring_path = candidate
                break
        except IndexError:
            break
    if scoring_path is None:
        scoring_path = here.parent / "data" / "import" / "scoring.txt"
    if scoring_path.exists():
        lines = scoring_path.read_text().splitlines()
        header = lines[0].strip().split("\t")[1:]
        scoring = {}
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.strip().split("\t")
            tier = parts[0].upper()
            points = [int(x) for x in parts[1:]]
            scoring[tier] = points
        return scoring, header
    # Fallback to defaults
    scoring = ScoringRules().model_dump()
    header = ["R1", "R2", "R3", "R4", "QF", "SF", "F"]
    return scoring, header


def _round_stage_mapping(rounds: set[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    numeric = []
    for r in rounds:
        if r.startswith("R"):
            try:
                numeric.append(int(r[1:]))
            except ValueError:
                pass
    numeric = sorted(set(numeric), reverse=True)
    stage_prefix = ["R1", "R2", "R3", "R4"]
    for i, n in enumerate(numeric[:4]):
        mapping[f"R{n}"] = stage_prefix[i]
    if "QF" in rounds:
        mapping["QF"] = "QF"
    if "SF" in rounds:
        mapping["SF"] = "SF"
    if "F" in rounds:
        mapping["F"] = "F"
    return mapping


def _simulate_draw_tree_once(
    *,
    nodes: list[dict],
    player_map: dict[str, PlayerLite],
    gender: str,
    simulator: EloMatchSimulator,
    all_player_names: set[str],
):
    by_id = {n["id"]: n for n in nodes}
    rounds = {n["round"] for n in nodes}
    stage_map = _round_stage_mapping(rounds)

    finals = [n for n in nodes if n["round"] == "F"]
    if not finals:
        raise RuntimeError("No final match found")
    root = sorted(finals, key=lambda x: x["match_index"])[0]

    # Initialize ALL players as not having reached any stage yet (will default to R1 loss)
    reached_stage: dict[str, str] = {}
    
    # Pre-populate all players with base stage R1 (ensures everyone appears)
    # Players who advance will have their stage updated
    for name in all_player_names:
        reached_stage[name] = "R1"

    def note_reached(player_name: str, match_round: str):
        stage = stage_map.get(match_round)
        if not stage:
            return
        order = ["R1", "R2", "R3", "R4", "QF", "SF", "F"]
        prev = reached_stage.get(player_name)
        if prev is None or order.index(stage) > order.index(prev):
            reached_stage[player_name] = stage

    def get_player(name: str) -> PlayerLite:
        return player_map.get(
            name,
            PlayerLite(name=name, tier="D", elo=1500, helo=1500, celo=1500, gelo=1500, form=0.0),
        )

    match_results: list[dict] = []

    def simulate_match(p1_name: str, p1_bye: bool, p2_name: str, p2_bye: bool, match_round: str) -> str:
        # Both players reach this round
        if p1_name and not p1_bye:
            note_reached(p1_name, match_round)
        if p2_name and not p2_bye:
            note_reached(p2_name, match_round)
        if p1_bye and not p2_bye:
            return p2_name
        if p2_bye and not p1_bye:
            return p1_name
        pl1 = get_player(p1_name)
        pl2 = get_player(p2_name)
        winner, _, _ = simulator.simulate_match(pl1, pl2, gender)
        loser_name = pl2.name if winner.name == pl1.name else pl1.name
        match_results.append(
            {
                "winner": winner.name,
                "loser": loser_name,
                "stage": match_round,
            }
        )
        return winner.name

    def dfs(match_id: int) -> str:
        n = by_id[match_id]
        rnd = n["round"]
        if n["child_match1_id"] is None and n["child_match2_id"] is None:
            p1_name = n["p1_name"] or ""
            p2_name = n["p2_name"] or ""
            p1_bye = bool(n["p1_bye"]) if n["p1_bye"] is not None else (str(p1_name).upper() == "BYE")
            p2_bye = bool(n["p2_bye"]) if n["p2_bye"] is not None else (str(p2_name).upper() == "BYE")
            return simulate_match(p1_name, p1_bye, p2_name, p2_bye, rnd)
        w1 = dfs(int(n["child_match1_id"]))
        w2 = dfs(int(n["child_match2_id"]))
        note_reached(w1, rnd)
        note_reached(w2, rnd)
        pl1 = get_player(w1)
        pl2 = get_player(w2)
        winner, _, _ = simulator.simulate_match(pl1, pl2, gender)
        loser_name = pl2.name if winner.name == pl1.name else pl1.name
        match_results.append(
            {
                "winner": winner.name,
                "loser": loser_name,
                "stage": rnd,
            }
        )
        return winner.name

    winner_name = dfs(int(root["id"]))
    if winner_name:
        reached_stage[winner_name] = "F"
    return winner_name, reached_stage, match_results


@router.get("/scoring_rules")
async def get_scoring_rules():
    cache_key = "scorito:scoring_rules"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    scoring, rounds = parse_scorito_scoring()
    payload = {"scoring": scoring, "rounds": rounds}
    cache_set(cache_key, payload, ttl=300)
    return payload


@router.post("/optimize", response_model=List[ScoritoResult])
async def optimize_scorito_lineup(
    request: ScoritoRequest,
    db: Session = Depends(get_db),
):
    """Optimize Scorito lineup for a tournament (simulate full draw)"""
    # Resolve snapshot + tour
    snap_sql = """
        SELECT snap.id as snapshot_id, ds.tour
        FROM tennis.draw_snapshots snap
        JOIN tennis.draw_sources ds ON ds.id = snap.source_id
        WHERE ds.id = :tournament_id AND snap.status = 'success'
        ORDER BY snap.scraped_at DESC, snap.id DESC
        LIMIT 1
    """
    snap = db.execute(text(snap_sql), {"tournament_id": request.tournament_id}).mappings().first()
    if not snap:
        raise HTTPException(status_code=404, detail="No draw snapshot found for tournament")

    gender = "men" if snap["tour"] == "atp" else "women"
    snapshot_id = snap["snapshot_id"]

    # Load draw nodes
    nodes_sql = """
        SELECT
          m.id,
          m.round,
          m.match_index,
          m.child_match1_id,
          m.child_match2_id,
          e1.player_name AS p1_name,
          e1.is_bye AS p1_bye,
          e2.player_name AS p2_name,
          e2.is_bye AS p2_bye
        FROM tennis.draw_matches m
        LEFT JOIN tennis.draw_entries e1 ON e1.id = m.entry1_id
        LEFT JOIN tennis.draw_entries e2 ON e2.id = m.entry2_id
        WHERE m.snapshot_id = :snapshot_id
    """
    nodes = db.execute(text(nodes_sql), {"snapshot_id": snapshot_id}).mappings().all()
    if not nodes:
        raise HTTPException(status_code=404, detail="No draw matches found")

    # Load players + tier assignments (active tier set)
    player_sql = """
        WITH active_set AS (
          SELECT id
          FROM tennis.tier_sets
          WHERE gender = :gender AND active = 1
          ORDER BY created_at DESC, id DESC
          LIMIT 1
        )
        SELECT
          c.player_name AS name,
          COALESCE(ta.tier, 'D') AS tier,
          c.elo, c.helo, c.celo, c.gelo,
          c.form AS raw_form,
          c.form_4w AS form_4w,
          c.form_12w AS form_12w,
          COALESCE(
            c.form,
            0.75 * COALESCE(c.form_4w, 0) + 0.25 * COALESCE(c.form_12w, 0),
            0
          ) AS form
        FROM tennis.elo_current c
        LEFT JOIN active_set s ON true
        LEFT JOIN tennis.tier_assignments ta
          ON ta.tier_set_id = s.id AND ta.player_id = c.player_id
        WHERE c.gender = :gender
    """
    rows = db.execute(text(player_sql), {"gender": gender}).mappings().all()
    player_map = {
        r["name"]: PlayerLite(
            name=r["name"],
            tier=r["tier"],
            elo=r.get("elo"),
            helo=r.get("helo"),
            celo=r.get("celo"),
            gelo=r.get("gelo"),
            form=r.get("form") or 0.0,
        )
        for r in rows
    }
    player_meta = {
        r["name"]: {
            "form_trend": r.get("raw_form") if r.get("raw_form") is not None else r.get("form"),
        }
        for r in rows
    }

    scoring = request.scoring.model_dump()
    rounds = ["R1", "R2", "R3", "R4", "QF", "SF", "F"]
    stage_to_index = {lab: i for i, lab in enumerate(rounds)}

    # Collect all player names from the draw
    all_player_names: set[str] = set()
    for n in nodes:
        p1_name = n.get("p1_name")
        p2_name = n.get("p2_name")
        p1_bye = n.get("p1_bye")
        p2_bye = n.get("p2_bye")
        if p1_name and not p1_bye and str(p1_name).upper() != "BYE":
            all_player_names.add(p1_name)
        if p2_name and not p2_bye and str(p2_name).upper() != "BYE":
            all_player_names.add(p2_name)

    from collections import defaultdict, Counter
    player_points = defaultdict(list)
    elim_idxs_by_player = defaultdict(list)
    elim_pair_by_player = defaultdict(Counter)
    winner_counts = Counter()
    faced_by_player_stage = defaultdict(lambda: defaultdict(Counter))
    wins_by_player_stage = defaultdict(lambda: defaultdict(Counter))
    weights = request.weights or EloWeights()
    simulator = EloMatchSimulator(weights=weights)

    # Build draw tree helpers for path difficulty
    by_id = {int(n["id"]): n for n in nodes}
    parent_of: dict[int, int] = {}
    for n in nodes:
        pid = int(n["id"])
        c1 = n.get("child_match1_id")
        c2 = n.get("child_match2_id")
        if c1 is not None:
            parent_of[int(c1)] = pid
        if c2 is not None:
            parent_of[int(c2)] = pid

    leaf_match_by_player: dict[str, int] = {}
    leaf_set_cache: dict[int, set[str]] = {}

    def leaf_players(match_id: int) -> set[str]:
        if match_id in leaf_set_cache:
            return leaf_set_cache[match_id]
        n = by_id[match_id]
        c1 = n.get("child_match1_id")
        c2 = n.get("child_match2_id")
        if c1 is None and c2 is None:
            out: set[str] = set()
            for key_name, key_bye in (("p1_name", "p1_bye"), ("p2_name", "p2_bye")):
                nm = (n.get(key_name) or "").strip()
                if not nm:
                    continue
                is_bye = bool(n.get(key_bye)) if n.get(key_bye) is not None else (nm.upper() == "BYE")
                if is_bye or nm.upper() == "BYE":
                    continue
                out.add(nm)
                leaf_match_by_player.setdefault(nm, match_id)
            leaf_set_cache[match_id] = out
            return out
        out = set()
        if c1 is not None:
            out |= leaf_players(int(c1))
        if c2 is not None:
            out |= leaf_players(int(c2))
        leaf_set_cache[match_id] = out
        return out

    finals = [n for n in nodes if str(n.get("round")) == "F"]
    root_id = int(sorted(finals, key=lambda x: x["match_index"])[0]["id"]) if finals else int(nodes[0]["id"])
    leaf_players(root_id)

    rounds_set = {str(n.get("round")) for n in nodes if n.get("round")}
    stage_map = _round_stage_mapping(rounds_set)

    def opponent_avg_elo(names: set[str]) -> float:
        values = []
        for nm in names:
            pl = player_map.get(nm)
            if pl and pl.elo is not None:
                values.append(float(pl.elo))
            else:
                values.append(1500.0)
        if not values:
            return 0.0
        return sum(values) / float(len(values))

    path_rounds_by_player: dict[str, dict[str, float]] = {}
    path_round_opponents_by_player: dict[str, dict[str, list[str]]] = {}
    for player_name, leaf_id in leaf_match_by_player.items():
        cur = leaf_id
        path_rounds: dict[str, float] = {}
        path_round_opps: dict[str, list[str]] = {}

        # Include R1 opponent from leaf match if present
        leaf_node = by_id.get(leaf_id)
        if leaf_node:
            round_label = stage_map.get(str(leaf_node.get("round")))
            p1_name = (leaf_node.get("p1_name") or "").strip()
            p2_name = (leaf_node.get("p2_name") or "").strip()
            p1_bye = bool(leaf_node.get("p1_bye")) if leaf_node.get("p1_bye") is not None else (p1_name.upper() == "BYE")
            p2_bye = bool(leaf_node.get("p2_bye")) if leaf_node.get("p2_bye") is not None else (p2_name.upper() == "BYE")
            if round_label:
                opp = ""
                if player_name == p1_name and not p2_bye:
                    opp = p2_name
                elif player_name == p2_name and not p1_bye:
                    opp = p1_name
                if opp:
                    path_round_opps[round_label] = [opp]
                    path_rounds[round_label] = opponent_avg_elo({opp})
        while cur in parent_of:
            parent = parent_of[cur]
            pn = by_id[parent]
            round_label = stage_map.get(str(pn.get("round")))
            sib = None
            if pn.get("child_match1_id") is not None and int(pn["child_match1_id"]) == cur:
                sib = pn.get("child_match2_id")
            else:
                sib = pn.get("child_match1_id")
            if round_label and sib is not None:
                opps = leaf_players(int(sib))
                if opps:
                    path_rounds[round_label] = opponent_avg_elo(opps)
                    path_round_opps[round_label] = sorted(opps)[:4]
            cur = parent
        path_rounds_by_player[player_name] = path_rounds
        path_round_opponents_by_player[player_name] = path_round_opps

    # Elo sparkline data for players in draw
    sparkline_map: dict[str, list[float]] = {}
    if all_player_names:
        spark_sql = """
            WITH recent AS (
              SELECT id, scraped_at
              FROM tennis.elo_snapshots
              WHERE gender = :gender
              ORDER BY scraped_at DESC
              LIMIT 8
            )
            SELECT r.player_name, array_agg(r.elo ORDER BY s.scraped_at) AS elos
            FROM tennis.elo_ratings r
            JOIN tennis.elo_snapshots s ON s.id = r.snapshot_id
            JOIN recent rs ON rs.id = s.id
            WHERE r.player_name = ANY(:names)
            GROUP BY r.player_name
        """
        spark_rows = db.execute(
            text(spark_sql),
            {"gender": gender, "names": list(all_player_names)},
        ).mappings().all()
        for r in spark_rows:
            elos = r.get("elos") or []
            sparkline_map[r["player_name"]] = [float(x) for x in elos if x is not None]

    for _ in range(request.num_simulations):
        winner, reached, match_results = _simulate_draw_tree_once(
            nodes=nodes,
            player_map=player_map,
            gender=gender,
            simulator=simulator,
            all_player_names=all_player_names,
        )
        if winner:
            reached[winner] = "F"
            winner_counts[winner] += 1
        for name, stage in reached.items():
            tier = str(player_map.get(name, PlayerLite(name=name, tier="D")).tier).upper()
            round_index = stage_to_index.get(stage, 0)
            tier_scoring = scoring.get(tier, [0] * len(rounds))
            total_points = sum(tier_scoring[: round_index + 1]) if round_index >= 0 else 0
            player_points[name].append(total_points)

        elim_stage_by_player: dict[str, str] = {}
        for mr in match_results:
            w_name = mr.get("winner")
            l_name = mr.get("loser")
            stage_raw = mr.get("stage")
            stage = stage_map.get(stage_raw) if stage_raw else None
            if not w_name or not l_name or not stage:
                continue
            elim_stage_by_player[l_name] = stage
            elim_pair_by_player[l_name][(stage, w_name)] += 1
            faced_by_player_stage[w_name][stage][l_name] += 1
            faced_by_player_stage[l_name][stage][w_name] += 1
            wins_by_player_stage[w_name][stage][l_name] += 1

        # Ensure every player has an elimination stage entry
        for name in all_player_names:
            if winner and name == winner:
                elim_stage = "F"
            else:
                elim_stage = elim_stage_by_player.get(name) or reached.get(name) or "R1"
            elim_idx = int(stage_to_index.get(elim_stage, 0))
            elim_idxs_by_player[name].append(elim_idx)

    def round_label_from_idx(idx: int) -> str:
        idx_i = max(0, min(idx, len(rounds) - 1))
        return rounds[idx_i]

    results = []
    for name, pts in player_points.items():
        avg_points = sum(pts) / len(pts) if pts else 0.0
        tier = str(player_map.get(name, PlayerLite(name=name, tier="D")).tier).upper()
        elim_idxs = elim_idxs_by_player.get(name, [])
        if elim_idxs:
            mean_idx = sum(elim_idxs) / len(elim_idxs)
            median_idx = sorted(elim_idxs)[len(elim_idxs) // 2]
            mode_idx = Counter(elim_idxs).most_common(1)[0][0]
            avg_round = mean_idx + 1
            median_round = median_idx
            mode_round = round_label_from_idx(mode_idx)
        else:
            avg_round = 0.0
            median_round = None
            mode_round = None

        if pts:
            sorted_pts = sorted(pts)
            def percentile(pct: float) -> float:
                if not sorted_pts:
                    return 0.0
                idx = int(round((len(sorted_pts) - 1) * pct))
                return float(sorted_pts[max(0, min(idx, len(sorted_pts) - 1))])
            mean = avg_points
            variance = sum((float(x) - mean) ** 2 for x in sorted_pts) / float(len(sorted_pts))
            points_std = variance ** 0.5
            points_p10 = percentile(0.10)
            points_p50 = percentile(0.50)
            points_p90 = percentile(0.90)
        else:
            points_std = 0.0
            points_p10 = points_p50 = points_p90 = 0.0

        risk_adj_value = avg_points / max(points_std, 1.0) if avg_points else 0.0

        path_rounds = path_rounds_by_player.get(name, {})
        path_vals = list(path_rounds.values())
        path_avg = sum(path_vals) / len(path_vals) if path_vals else 0.0
        path_peak = max(path_vals) if path_vals else 0.0

        elim_pair_counter = elim_pair_by_player.get(name)
        if elim_pair_counter:
            (elim_stage, eliminator), elim_times = elim_pair_counter.most_common(1)[0]
            elim_rate = elim_times / float(request.num_simulations)
            eliminator_name = str(eliminator)
        else:
            elim_rate = None
            eliminator_name = None

        elim_round_probs: dict[str, float] = {}
        if elim_idxs:
            counts = Counter(elim_idxs)
            for idx, count in counts.items():
                label = round_label_from_idx(int(idx))
                elim_round_probs[label] = count / float(len(elim_idxs))

        def compute_sim_strength(player: PlayerLite) -> float:
            base = (
                (player.elo or 1500) * weights.elo_weight
                + (player.helo or player.elo or 1500) * weights.helo_weight
                + (player.celo or player.elo or 1500) * weights.celo_weight
                + (player.gelo or player.elo or 1500) * weights.gelo_weight
            )
            form = player.form or 0.0
            form_adj = min(weights.form_elo_cap, abs(form) * weights.form_elo_scale)
            form_adj = form_adj if form >= 0 else -form_adj
            return float(base + form_adj)

        filtered_path_round_opps: dict[str, list[dict[str, float]]] = {}
        for round_label, stage_faced in faced_by_player_stage.get(name, {}).items():
            stage_wins = wins_by_player_stage.get(name, {}).get(round_label, Counter())
            kept = []
            for opp, count in stage_faced.items():
                meet_prob = count / float(request.num_simulations)
                if meet_prob >= 0.10:
                    wins = stage_wins.get(opp, 0)
                    win_prob = wins / float(max(count, 1))
                    kept.append(
                        {
                            "opponent": opp,
                            "meet_prob": meet_prob,
                            "win_prob": win_prob,
                        }
                    )
            if kept:
                kept.sort(key=lambda x: x["meet_prob"], reverse=True)
                filtered_path_round_opps[round_label] = kept

        # Path strength: average sim strength of opponents met (weighted by meet prob)
        opp_strength_num = 0.0
        opp_strength_den = 0.0
        for round_label, opps in filtered_path_round_opps.items():
            for o in opps:
                opp_player = player_map.get(o["opponent"], PlayerLite(name=o["opponent"], tier="D"))
                opp_strength = compute_sim_strength(opp_player)
                opp_strength_num += opp_strength * o["meet_prob"]
                opp_strength_den += o["meet_prob"]
        path_strength = opp_strength_num / opp_strength_den if opp_strength_den else 0.0

        results.append(
            ScoritoResult(
                player_name=name,
                tier=tier,
                expected_points=avg_points,
                avg_round=float(avg_round),
                win_probability=winner_counts[name] / float(request.num_simulations) if request.num_simulations else 0.0,
                value_score=avg_points / 100.0 if avg_points else 0.0,
                median_round=median_round,
                mode_round=mode_round,
                eliminator=eliminator_name,
                elim_rate=elim_rate,
                points_std=points_std,
                points_p10=points_p10,
                points_p50=points_p50,
                points_p90=points_p90,
                risk_adj_value=risk_adj_value,
                form_trend=player_meta.get(name, {}).get("form_trend"),
                path_difficulty_avg=path_avg,
                path_difficulty_peak=path_peak,
                path_rounds=path_rounds,
                path_round_opponents=filtered_path_round_opps,
                elo_sparkline=sparkline_map.get(name, []),
                elim_round_probs=elim_round_probs,
                simulation_strength=compute_sim_strength(player_map.get(name, PlayerLite(name=name, tier="D"))),
                path_strength=path_strength,
            )
        )
    results.sort(key=lambda r: r.expected_points, reverse=True)
    return results


@router.get("/value_picks", response_model=List[ScoritoValuePick])
async def get_value_picks(
    tournament_id: int = Query(...),
    tour: str = Query("atp"),
    db: Session = Depends(get_db),
):
    """Get value picks for a tournament"""
    # Placeholder implementation
    return []


@router.post("/score", response_model=dict)
async def calculate_score(
    player_name: str = Query(...),
    round_reached: str = Query(...),
    tier: str = Query(...),
    db: Session = Depends(get_db),
):
    """Calculate score for a player reaching a specific round"""
    # Default scoring
    scoring = {
        "A": [10, 20, 30, 40, 60, 80, 100],
        "B": [20, 40, 60, 80, 100, 120, 140],
        "C": [30, 60, 90, 120, 140, 160, 180],
        "D": [60, 90, 120, 160, 180, 200, 200],
    }
    
    round_map = {"R1": 0, "R2": 1, "R3": 2, "R4": 3, "QF": 4, "SF": 5, "F": 6}
    
    tier_upper = tier.upper()
    if tier_upper not in scoring:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    
    round_upper = round_reached.upper()
    if round_upper not in round_map:
        raise HTTPException(status_code=400, detail=f"Invalid round: {round_reached}")
    
    round_idx = round_map[round_upper]
    total_points = sum(scoring[tier_upper][:round_idx + 1])
    
    return {
        "player_name": player_name,
        "tier": tier_upper,
        "round_reached": round_upper,
        "total_points": total_points,
    }

