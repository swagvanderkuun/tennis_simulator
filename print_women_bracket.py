from src.tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator
from src.tennis_simulator.core.models import Gender, Round

sim = FixedDrawEloSimulator()
sim.setup_tournaments()
t = sim.women_tournament

print("WOMEN'S BRACKET UNTIL FINAL:")

current_players = t.players.copy()
round_name = Round.R64

while len(current_players) > 1:
    print(f"\n{round_name.name}:")
    for i in range(0, len(current_players), 2):
        if i + 1 < len(current_players):
            print(f"  {current_players[i].name} vs {current_players[i+1].name}")
    # For bracket display, just advance the first player of each pair (no simulation)
    winners = current_players[::2]
    current_players = winners
    round_name = sim._get_next_round(round_name)

# Print the final (if any players left)
if len(current_players) == 1:
    print(f"\nWINNER: {current_players[0].name}") 