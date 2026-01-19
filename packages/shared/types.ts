/**
 * Shared types for Tournament Studio
 * These types are used by both frontend and backend
 */

// Player types
export interface Player {
  id: number;
  name: string;
  tier: 'A' | 'B' | 'C' | 'D';
  elo: number | null;
  helo: number | null;
  celo: number | null;
  gelo: number | null;
  ranking: number | null;
  elo_rank: number | null;
  form: number | null;
  country?: string;
}

export interface PlayerEloHistoryPoint {
  date: string;
  elo: number;
  helo?: number;
  celo?: number;
  gelo?: number;
}

export interface PlayerEloHistory {
  player_id: number;
  player_name: string;
  history: PlayerEloHistoryPoint[];
}

// Tournament types
export interface Tournament {
  id: number;
  name: string;
  tour: 'atp' | 'wta';
  season_year: number;
  surface?: 'hard' | 'clay' | 'grass';
  source_url?: string;
}

export interface DrawSnapshot {
  id: number;
  source_id: number;
  scraped_at: string;
  status: 'success' | 'failed' | 'pending';
}

export interface DrawMatch {
  id: number;
  round: string;
  match_index: number;
  player1_name?: string;
  player2_name?: string;
  player1_bye: boolean;
  player2_bye: boolean;
  child_match1_id?: number;
  child_match2_id?: number;
  player1_prob?: number;
  player2_prob?: number;
  winner?: string;
}

// Simulation types
export interface EloWeights {
  elo_weight: number;
  helo_weight: number;
  celo_weight: number;
  gelo_weight: number;
  form_elo_scale: number;
  form_elo_cap: number;
}

export interface SimulationFactor {
  name: string;
  player1_value: number;
  player2_value: number;
  weight: number;
  contribution: number;
}

export interface MatchSimResult {
  player1_name: string;
  player2_name: string;
  player1_win_prob: number;
  player2_win_prob: number;
  winner_name: string;
  loser_name: string;
  rating_diff: number;
  factors: SimulationFactor[];
}

export interface TournamentProbabilities {
  player_name: string;
  win_prob: number;
  final_prob: number;
  semi_prob: number;
  qf_prob: number;
}

// Scorito types
export interface ScoringRules {
  A: number[];
  B: number[];
  C: number[];
  D: number[];
}

export interface ScoritoResult {
  player_name: string;
  tier: string;
  expected_points: number;
  avg_round: number;
  win_probability: number;
  value_score: number;
  median_round?: number;
  mode_round?: string;
  eliminator?: string;
  elim_rate?: number;
  points_std?: number;
  points_p10?: number;
  points_p50?: number;
  points_p90?: number;
  risk_adj_value?: number;
  form_trend?: number;
  path_difficulty_avg?: number;
  path_difficulty_peak?: number;
  path_rounds?: Record<string, number>;
  path_round_opponents?: Record<string, { opponent: string; meet_prob: number; win_prob: number }[]>;
  elo_sparkline?: number[];
  elim_round_probs?: Record<string, number>;
  simulation_strength?: number;
  path_strength?: number;
}

// Weight presets
export const DEFAULT_WEIGHT_PRESETS: Record<string, EloWeights> = {
  'Overall (default)': {
    elo_weight: 0.45,
    helo_weight: 0.25,
    celo_weight: 0.20,
    gelo_weight: 0.10,
    form_elo_scale: 100,
    form_elo_cap: 50,
  },
  'Hard Court Focus': {
    elo_weight: 0.25,
    helo_weight: 0.50,
    celo_weight: 0.15,
    gelo_weight: 0.10,
    form_elo_scale: 100,
    form_elo_cap: 50,
  },
  'Clay Court Focus': {
    elo_weight: 0.25,
    helo_weight: 0.15,
    celo_weight: 0.50,
    gelo_weight: 0.10,
    form_elo_scale: 100,
    form_elo_cap: 50,
  },
  'Grass Court Focus': {
    elo_weight: 0.25,
    helo_weight: 0.15,
    celo_weight: 0.10,
    gelo_weight: 0.50,
    form_elo_scale: 100,
    form_elo_cap: 50,
  },
  'Elo Only': {
    elo_weight: 1.0,
    helo_weight: 0.0,
    celo_weight: 0.0,
    gelo_weight: 0.0,
    form_elo_scale: 0,
    form_elo_cap: 0,
  },
};

// Round labels
export const ROUND_LABELS = ['R1', 'R2', 'R3', 'R4', 'QF', 'SF', 'F'] as const;
export type Round = typeof ROUND_LABELS[number];

// Default scoring rules
export const DEFAULT_SCORING: ScoringRules = {
  A: [10, 20, 35, 55, 80, 120, 180],
  B: [15, 30, 50, 80, 120, 180, 270],
  C: [20, 40, 70, 110, 170, 260, 400],
  D: [25, 50, 90, 150, 230, 350, 550],
};


