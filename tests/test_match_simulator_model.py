import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, five_set_probability


def _player(name: str, *, elo=None, helo=None, celo=None, gelo=None) -> Player:
    return Player(
        name=name,
        country="X",
        seeding=None,
        tier=Tier.A,
        elo=elo,
        helo=helo,
        celo=celo,
        gelo=gelo,
    )


def test_weighted_rating_missing_surface_falls_back_to_base():
    sim = EloMatchSimulator()
    p_only_elo = _player("A", elo=2000.0, helo=None, celo=None, gelo=None)
    p_all_equal = _player("B", elo=2000.0, helo=2000.0, celo=2000.0, gelo=2000.0)

    r1 = sim.calculate_weighted_rating(p_only_elo)
    r2 = sim.calculate_weighted_rating(p_all_equal)
    assert r1 == pytest.approx(2000.0, abs=1e-9)
    assert r2 == pytest.approx(2000.0, abs=1e-9)


def test_weighted_rating_when_overall_missing_uses_first_available_as_base():
    sim = EloMatchSimulator()
    p = _player("A", elo=None, helo=2100.0, celo=None, gelo=None)
    assert sim.calculate_weighted_rating(p) == pytest.approx(2100.0, abs=1e-9)


def test_win_probability_monotonic_in_elo():
    sim = EloMatchSimulator()
    p1 = _player("P1", elo=2000.0, helo=2000.0, celo=2000.0, gelo=2000.0)
    p2 = _player("P2", elo=2000.0, helo=2000.0, celo=2000.0, gelo=2000.0)

    p_equal = sim.calculate_win_probability(p1, p2, "women")
    assert p_equal == pytest.approx(0.5, abs=1e-12)

    p2.elo = 2100.0
    p2.helo = 2100.0
    p2.celo = 2100.0
    p2.gelo = 2100.0
    p_lower = sim.calculate_win_probability(p1, p2, "women")
    assert p_lower < 0.5


def test_form_adjustment_moves_probability():
    sim = EloMatchSimulator()
    p1 = _player("P1", elo=2000.0, helo=2000.0, celo=2000.0, gelo=2000.0)
    p2 = _player("P2", elo=2000.0, helo=2000.0, celo=2000.0, gelo=2000.0)
    p1.form = +40.0
    p2.form = -40.0
    p = sim.calculate_win_probability(p1, p2, "women")
    assert p > 0.5


def test_five_set_probability_sanity_and_monotone():
    assert five_set_probability(0.0) == pytest.approx(0.0, abs=1e-12)
    assert five_set_probability(1.0) == pytest.approx(1.0, abs=1e-12)

    mid = five_set_probability(0.5)
    # Should be close to fair
    assert mid == pytest.approx(0.5, abs=0.03)

    ps = [i / 20 for i in range(1, 20)]  # 0.05..0.95
    outs = [five_set_probability(p) for p in ps]
    # In range and monotone increasing
    assert all(0.0 <= o <= 1.0 for o in outs)
    assert all(outs[i] <= outs[i + 1] + 1e-12 for i in range(len(outs) - 1))


