"""
Shared Elo match simulator aligned with the legacy Streamlit dashboard.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import math
import random
import numpy


def five_set_probability(p3: float) -> float:
    """
    Convert best-of-3 probability to best-of-5 probability for men's matches.
    """
    roots = numpy.roots([-2, 3, 0, -1 * p3])
    p1 = None
    for root in roots:
        if abs(root.imag) < 1e-10 and 0 <= root.real <= 1:
            p1 = root.real
            break
    if p1 is None:
        return p3
    p5 = (p1**3) * (4 - 3 * p1 + (6 * (1 - p1) * (1 - p1)))
    return max(0.0, min(1.0, p5))


@dataclass
class EloWeights:
    """
    Elo weight configuration aligned with src/tennis_simulator/simulators/elo_match_simulator.py
    """
    elo_weight: float = 0.45
    helo_weight: float = 0.25
    celo_weight: float = 0.20
    gelo_weight: float = 0.10
    form_elo_scale: float = 1.0
    form_elo_cap: float = 80.0


@dataclass
class PlayerLite:
    name: str
    tier: str
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None
    form: Optional[float] = 0.0


class EloMatchSimulator:
    def __init__(self, weights: Optional[EloWeights] = None):
        self.weights = weights or EloWeights()

    def calculate_weighted_rating(self, player: PlayerLite) -> float:
        base = (
            player.elo
            if player.elo is not None
            else (player.helo if player.helo is not None else (player.celo if player.celo is not None else player.gelo))
        )
        if base is None:
            base = 1500.0
        elo = player.elo if player.elo is not None else base
        helo = player.helo if player.helo is not None else base
        celo = player.celo if player.celo is not None else base
        gelo = player.gelo if player.gelo is not None else base
        return (
            self.weights.elo_weight * float(elo)
            + self.weights.helo_weight * float(helo)
            + self.weights.celo_weight * float(celo)
            + self.weights.gelo_weight * float(gelo)
        )

    def calculate_form_elo_adjustment(self, player: PlayerLite) -> float:
        raw = getattr(player, "form", 0.0) or 0.0
        try:
            raw_f = float(raw)
        except Exception:
            raw_f = 0.0
        adj = raw_f * float(self.weights.form_elo_scale)
        cap = float(self.weights.form_elo_cap)
        if cap > 0:
            adj = max(-cap, min(cap, adj))
        return adj

    def calculate_win_probability(self, player1: PlayerLite, player2: PlayerLite, gender: str = "women") -> float:
        rating1 = self.calculate_weighted_rating(player1) + self.calculate_form_elo_adjustment(player1)
        rating2 = self.calculate_weighted_rating(player2) + self.calculate_form_elo_adjustment(player2)
        rating_diff = rating2 - rating1
        p = 1 / (1 + math.pow(10, rating_diff / 400))
        if gender.lower() == "men":
            p = five_set_probability(p)
        return p

    def simulate_match(self, player1: PlayerLite, player2: PlayerLite, gender: str = "women"):
        p1_win_prob = self.calculate_win_probability(player1, player2, gender)
        if random.random() < p1_win_prob:
            winner, loser = player1, player2
        else:
            winner, loser = player2, player1
        return winner, loser, {"player1_win_probability": p1_win_prob}


