"""
Basic tests for the tennis simulator package.
"""

import sys
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tennis_simulator import (
    Player, Match, Tournament, Round, Gender, Tier, ScoritoGame,
    player_db, TournamentSimulator, PlayerSelector
)


def test_imports():
    """Test that all modules can be imported."""
    assert Player is not None
    assert Match is not None
    assert Tournament is not None
    assert Round is not None
    assert Gender is not None
    assert Tier is not None
    assert ScoritoGame is not None
    assert player_db is not None
    assert TournamentSimulator is not None
    assert PlayerSelector is not None


def test_player_creation():
    """Test creating a player."""
    player = Player(
        name="Novak Djokovic",
        country="SRB",
        seeding=1,
        tier=Tier.A,
        elo=2200,
        atp_rank=1
    )
    
    assert player.name == "Novak Djokovic"
    assert player.country == "SRB"
    assert player.seeding == 1
    assert player.tier == Tier.A
    assert player.elo == 2200
    assert player.atp_rank == 1
    assert player.current_round == Round.R64
    assert not player.eliminated


def test_player_database():
    """Test player database functionality."""
    # Test getting players by gender
    men_players = player_db.get_players_by_gender(Gender.MEN)
    women_players = player_db.get_players_by_gender(Gender.WOMEN)
    
    assert len(men_players) > 0
    assert len(women_players) > 0
    
    # Test getting players by tier
    tier_a_men = player_db.get_players_by_tier(Gender.MEN, Tier.A)
    assert len(tier_a_men) > 0
    
    # Test getting specific player
    djokovic = player_db.get_player_by_name("Novak Djokovic", Gender.MEN)
    assert djokovic is not None
    assert djokovic.name == "Novak Djokovic"


def test_tournament_creation():
    """Test creating a tournament."""
    tournament = Tournament(
        name="Wimbledon Men's",
        gender=Gender.MEN
    )
    
    assert tournament.name == "Wimbledon Men's"
    assert tournament.gender == Gender.MEN
    assert len(tournament.players) == 0
    assert not tournament.completed


def test_match_simulation():
    """Test match simulation."""
    player1 = Player("Player 1", "USA", 1, Tier.A, elo=2000)
    player2 = Player("Player 2", "ESP", 2, Tier.A, elo=1900)
    
    match = Match(player1, player2, Round.R64)
    
    # Simulate match
    winner = match.simulate()
    
    assert winner in [player1, player2]
    assert match.winner is not None
    assert match.loser is not None
    assert match.winner != match.loser


def test_scorito_game():
    """Test Scorito game creation."""
    game = ScoritoGame("Test Game")
    
    # Add player selections
    game.add_player_selection(Gender.MEN, Tier.A, ["Player 1", "Player 2", "Player 3"])
    game.add_player_selection(Gender.WOMEN, Tier.A, ["Player 4", "Player 5", "Player 6"])
    
    assert game.name == "Test Game"
    assert len(game.men_selection) > 0
    assert len(game.women_selection) > 0


def test_player_selector():
    """Test player selector creation."""
    selector = PlayerSelector()
    
    assert selector.selections["men"] == {}
    assert selector.selections["women"] == {}
    
    # Test validation
    assert not selector.validate_selection()  # Should be False for empty selection


def test_enum_values():
    """Test enum values."""
    assert Gender.MEN.value == "men"
    assert Gender.WOMEN.value == "women"
    
    assert Tier.A.value == "A"
    assert Tier.B.value == "B"
    assert Tier.C.value == "C"
    assert Tier.D.value == "D"
    
    assert Round.R64.value == "R64"
    assert Round.R32.value == "R32"
    assert Round.R16.value == "R16"
    assert Round.QF.value == "QF"
    assert Round.SF.value == "SF"
    assert Round.F.value == "F"
    assert Round.W.value == "W"


def test_player_methods():
    """Test player methods."""
    player = Player(
        name="Test Player",
        country="USA",
        seeding=1,
        tier=Tier.A,
        elo=2000,
        helo=1950,
        celo=1900,
        gelo=2050,
        yelo=2100,
        atp_rank=5
    )
    
    assert player.get_clean_name() == "Test Player"
    assert player.get_primary_rank() == 5
    assert player.get_best_elo() == 2100  # Should return yelo as highest
    assert player.get_grass_elo() == 2050  # Should return gelo
    assert player.is_seeded() is True


if __name__ == "__main__":
    pytest.main([__file__]) 