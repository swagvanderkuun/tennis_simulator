from bracketool.single_elimination import SingleEliminationGen
from bracketool.domain import Competitor
from typing import List
from ..core.models import Player

def create_bracketool_competitors(players: List[Player]):
    return [
        Competitor(
            p.name,
            p.country if hasattr(p, 'country') else "UNK",
            p.yelo or p.elo or 1500
        )
        for p in players
    ]

def generate_bracket(players: List[Player], random_seed=42):
    competitors = create_bracketool_competitors(players)
    se = SingleEliminationGen(
        use_three_way_final=False,
        third_place_clash=True,
        use_rating=True,
        use_teams=False,
        random_seed=random_seed
    )
    return se.generate(competitors)

def get_competitor_name(clash, idx):
    # Try slots
    if hasattr(clash, "slots"):
        slot = clash.slots[idx]
        return slot.competitor.name if slot.competitor else "BYE"
    # Try competitor1/competitor2
    if hasattr(clash, f"competitor{idx+1}"):
        comp = getattr(clash, f"competitor{idx+1}")
        return comp.name if comp else "BYE"
    # Try competitors list
    if hasattr(clash, "competitors"):
        comp = clash.competitors[idx]
        return comp.name if comp else "BYE"
    return "BYE"

def simulate_bracketool_tournament(players, match_simulator, gender_label="men"):
    bracket = generate_bracket(players)
    name_to_player = {p.name: p for p in players}
    round_results = []
    for rnd_idx, clashes in enumerate(bracket.rounds):
        round_matches = []
        for clash in clashes:
            p1 = get_competitor_name(clash, 0)
            p2 = get_competitor_name(clash, 1)
            if p1 == "BYE":
                winner = p2
            elif p2 == "BYE":
                winner = p1
            else:
                player1 = name_to_player[p1]
                player2 = name_to_player[p2]
                winner_obj, _, _ = match_simulator.simulate_match(player1, player2)
                winner = winner_obj.name
            clash.winner = winner
            round_matches.append({
                "p1": p1,
                "p2": p2,
                "winner": winner
            })
        round_results.append(round_matches)
    return bracket, round_results 