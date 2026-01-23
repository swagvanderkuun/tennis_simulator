'use client';

import { useEffect, useMemo, useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, TierBadge } from '@/components/ui';
import { cn } from '@/lib/utils';
import {
  getDrawEntries,
  getDrawSnapshot,
  getScoritoScoringRules,
  optimizeScoritoLineup,
  ScoritoResult,
} from '@/lib/api';
import { useAppStore } from '@/lib/store';

// Default scoring rules
const DEFAULT_SCORING = {
  A: [10, 20, 30, 40, 60, 80, 100],
  B: [20, 40, 60, 80, 100, 120, 140],
  C: [30, 60, 90, 120, 140, 160, 180],
  D: [60, 90, 120, 160, 180, 200, 200],
};

const ROUND_LABELS = ['R1', 'R2', 'R3', 'R4', 'QF', 'SF', 'F'];
const SCORING_STORAGE_KEY = 'scorito_scoring_rules_v1';
const FORM_PRESETS = ['elo-only', 'default-form', 'form-heavy'] as const;
type FormPreset = (typeof FORM_PRESETS)[number];

function MiniSparkline() {
  return null;
}

export function ScoritoPage() {
  const { selectedTournamentId, surface } = useAppStore();
  const [scoring, setScoring] = useState(DEFAULT_SCORING);
  const [roundLabels, setRoundLabels] = useState(ROUND_LABELS);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);
  const [results, setResults] = useState<ScoritoResult[]>([]);
  const [totalPlayers, setTotalPlayers] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedPlayer, setExpandedPlayer] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<string>('expected_points');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [formPreset, setFormPreset] = useState<FormPreset>('default-form');

  useEffect(() => {
    let mounted = true;
    const loadScoring = async () => {
      try {
        if (typeof window !== 'undefined') {
          const stored = window.localStorage.getItem(SCORING_STORAGE_KEY);
          if (stored) {
            const parsed = JSON.parse(stored) as {
              scoring: typeof DEFAULT_SCORING;
              rounds: typeof ROUND_LABELS;
            };
            if (parsed?.scoring && parsed?.rounds) {
              if (!mounted) return;
              setScoring(parsed.scoring);
              setRoundLabels(parsed.rounds);
              return;
            }
          }
        }

        const rules = await getScoritoScoringRules();
        if (!mounted) return;
        setScoring(rules.scoring as typeof DEFAULT_SCORING);
        setRoundLabels(rules.rounds as typeof ROUND_LABELS);
      } catch (err) {
        // Keep default scoring if API fails
      }
    };
    loadScoring();
    return () => {
      mounted = false;
    };
  }, []);

  const handleOptimize = async () => {
    if (!selectedTournamentId) return;
    setIsOptimizing(true);
    setErrorMessage(null);
    try {
      const snap = await getDrawSnapshot(selectedTournamentId);
      if (snap) {
        const entries = await getDrawEntries(snap.id);
        setTotalPlayers(entries.filter((e) => !e.is_bye).length);
      }
      const baseWeights =
        surface === 'hard'
          ? { elo_weight: 0.25, helo_weight: 0.5, celo_weight: 0.15, gelo_weight: 0.1 }
          : surface === 'clay'
          ? { elo_weight: 0.25, helo_weight: 0.15, celo_weight: 0.5, gelo_weight: 0.1 }
          : surface === 'grass'
          ? { elo_weight: 0.25, helo_weight: 0.15, celo_weight: 0.1, gelo_weight: 0.5 }
          : { elo_weight: 0.45, helo_weight: 0.25, celo_weight: 0.2, gelo_weight: 0.1 };
      const formWeights =
        formPreset === 'elo-only'
          ? { form_elo_scale: 0, form_elo_cap: 0 }
          : formPreset === 'form-heavy'
          ? { form_elo_scale: 1.5, form_elo_cap: 120 }
          : { form_elo_scale: 1.0, form_elo_cap: 80 };
      const data = await optimizeScoritoLineup({
        tournamentId: selectedTournamentId,
        scoring,
        weights: { ...baseWeights, ...formWeights },
      });
      setResults(data);
    } catch (err) {
      setResults([]);
      setErrorMessage('Optimizer failed to return results. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  };

  const displayResults = results;
  const filteredResultsBase = selectedTier
    ? displayResults.filter((r) => r.tier === selectedTier)
    : displayResults;

  const filteredResults = useMemo(() => {
    const sorted = [...filteredResultsBase].sort((a, b) => b.expected_points - a.expected_points);
    const dir = sortDir === 'asc' ? 1 : -1;
    const robustness = (r: ScoritoResult) => 100 / Math.max((r.points_std ?? 0) + 1, 1);
    const getValue = (r: ScoritoResult) => {
      switch (sortKey) {
        case 'player_name':
          return r.player_name;
        case 'simulation_strength':
          return r.simulation_strength ?? 0;
        case 'path_strength':
          return r.path_strength ?? 0;
        case 'form_trend':
          return r.form_trend ?? 0;
        case 'tier':
          return r.tier;
        case 'expected_points':
          return r.expected_points;
        case 'risk_adj_value':
          return r.risk_adj_value ?? 0;
        case 'robustness':
          return robustness(r);
        case 'avg_round':
          return r.avg_round;
        default:
          return r.expected_points;
      }
    };

    return [...sorted].sort((a, b) => {
      const va = getValue(a);
      const vb = getValue(b);
      if (typeof va === 'string' && typeof vb === 'string') {
        return va.localeCompare(vb) * dir;
      }
      return (Number(va) - Number(vb)) * dir;
    });
  }, [filteredResultsBase, sortKey, sortDir]);

  const dropOffIndices = useMemo(() => {
    const indices = new Set<number>();
    const numericKeys = new Set([
      'expected_points',
      'risk_adj_value',
      'robustness',
      'form_trend',
      'avg_round',
      'simulation_strength',
      'path_strength',
    ]);
    if (!numericKeys.has(sortKey)) return indices;
    const values = filteredResults.map((r) => {
      switch (sortKey) {
        case 'expected_points':
          return r.expected_points;
        case 'simulation_strength':
          return r.simulation_strength ?? 0;
        case 'path_strength':
          return r.path_strength ?? 0;
        case 'risk_adj_value':
          return r.risk_adj_value ?? 0;
        case 'robustness':
          return 100 / Math.max((r.points_std ?? 0) + 1, 1);
        case 'form_trend':
          return r.form_trend ?? 0;
        case 'avg_round':
          return r.avg_round;
        default:
          return 0;
      }
    });
    if (values.length < 2) return indices;
    const sortedVals = [...values].sort((a, b) => a - b);
    const p25 = sortedVals[Math.floor(sortedVals.length * 0.25)] ?? 0;
    const p75 = sortedVals[Math.floor(sortedVals.length * 0.75)] ?? 0;
    const iqr = Math.max(p75 - p25, 1);
    const absThreshold = Math.max(iqr * 0.25, 1);
    for (let i = 1; i < filteredResults.length; i += 1) {
      const prev = values[i - 1];
      const curr = values[i];
      const diff = sortDir === 'desc' ? prev - curr : curr - prev;
      const ratio = diff / Math.max(Math.abs(prev), 1);
      if (ratio >= 0.08 || diff >= absThreshold) {
        indices.add(i);
      }
    }
    return indices;
  }, [filteredResults, sortKey, sortDir]);

  const toggleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const tierInsights = useMemo(() => {
    if (!displayResults.length) return null;
    const tiers = ['A', 'B', 'C', 'D'] as const;
    return tiers.map((tier) => {
      const players = displayResults
        .filter((r) => r.tier === tier)
        .sort((a, b) => b.expected_points - a.expected_points);
      const top3 = players.slice(0, 3);
      const medianIdx = Math.floor(players.length / 2);
      const medianPoints = players.length ? players[medianIdx].expected_points : 0;
      return { tier, top3, medianPoints };
    });
  }, [displayResults]);

  useEffect(() => {
    if (!selectedTournamentId) {
      setTotalPlayers(0);
      setResults([]);
      setErrorMessage(null);
      return;
    }
    handleOptimize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTournamentId, surface, formPreset]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Scorito Optimizer</h1>
          <p className="text-muted-foreground">Find the best value picks for your fantasy team</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex flex-wrap items-center gap-1">
            {FORM_PRESETS.map((p) => (
              <button
                key={p}
                onClick={() => setFormPreset(p)}
                className={cn(
                  'px-3 py-1 rounded-full text-xs font-medium border',
                  formPreset === p
                    ? 'bg-primary text-background border-primary'
                    : 'bg-elevated text-muted-foreground border-border'
                )}
              >
                {p === 'elo-only' ? 'Elo‑only' : p === 'form-heavy' ? 'Form‑heavy' : 'Default form'}
              </button>
            ))}
          </div>
          <Button onClick={handleOptimize} disabled={isOptimizing} className="gap-2">
            <Sparkles className="h-4 w-4" />
            {isOptimizing ? 'Optimizing...' : 'Run Optimizer'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Optimizer Results */}
        <Card>
          <CardHeader>
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <CardTitle>
                Optimizer Results {totalPlayers ? `(All ${totalPlayers} players)` : ''}
              </CardTitle>
              <div className="flex flex-wrap items-center gap-2">
                {['A', 'B', 'C', 'D'].map((tier) => (
                  <button
                    key={tier}
                    onClick={() => setSelectedTier(selectedTier === tier ? null : tier)}
                    className={cn(
                      'tier-badge cursor-pointer transition-opacity',
                      `tier-${tier.toLowerCase()}`,
                      selectedTier && selectedTier !== tier && 'opacity-30'
                    )}
                  >
                    {tier}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {errorMessage && (
              <div className="mb-3 text-sm text-danger">{errorMessage}</div>
            )}
            <div className="w-full overflow-x-auto">
              <table className="data-table min-w-[900px]">
              <thead>
                <tr>
                  <th className="cursor-pointer" onClick={() => toggleSort('player_name')}>
                    Player
                  </th>
                  <th className="cursor-pointer" onClick={() => toggleSort('simulation_strength')}>
                    Sim Strength
                  </th>
                  <th className="cursor-pointer hidden md:table-cell" onClick={() => toggleSort('path_strength')}>
                    Path Strength
                  </th>
                  <th className="cursor-pointer" onClick={() => toggleSort('form_trend')}>
                    Form
                  </th>
                  <th className="cursor-pointer" onClick={() => toggleSort('tier')}>
                    Tier
                  </th>
                  <th className="cursor-pointer" onClick={() => toggleSort('expected_points')}>
                    Exp. Points
                  </th>
                  <th className="cursor-pointer hidden lg:table-cell" onClick={() => toggleSort('risk_adj_value')}>
                    <div>
                      <div>Risk‑Adj</div>
                      <div className="text-[10px] text-muted-foreground">pts / std dev</div>
                    </div>
                  </th>
                  <th className="cursor-pointer hidden lg:table-cell" onClick={() => toggleSort('robustness')}>
                    <div>
                      <div>Consistency</div>
                      <div className="text-[10px] text-muted-foreground">robustness</div>
                    </div>
                  </th>
                  <th className="cursor-pointer" onClick={() => toggleSort('avg_round')}>
                    Avg Round
                  </th>
                  <th className="hidden md:table-cell">Eliminator</th>
                </tr>
              </thead>
              <tbody>
                {isOptimizing && filteredResults.length === 0 && (
                  <>
                    {Array.from({ length: 8 }).map((_, idx) => (
                      <tr key={`loading-${idx}`}>
                        <td colSpan={10}>
                          <div className="skeleton h-8 w-full" />
                        </td>
                      </tr>
                    ))}
                  </>
                )}
                {!isOptimizing && filteredResults.length === 0 && (
                  <tr>
                    <td colSpan={10} className="p-4 text-sm text-muted-foreground">
                      No optimizer results yet. Click "Run Optimizer" to load all players.
                    </td>
                  </tr>
                )}
                {filteredResults.map((player, idx) => {
                  const name = (player as any).player_name || (player as any).name;
                  return (
                  <>
                  <tr
                    key={name}
                    className={cn(
                      'cursor-pointer',
                      dropOffIndices.has(idx) && 'border-t-2 border-danger/60'
                    )}
                    onClick={() => setExpandedPlayer(expandedPlayer === name ? null : name)}
                  >
                    <td>
                      <div className="flex items-center gap-2">
                        <div>
                          <span className="font-medium">{name}</span>
                          <div className="mt-1">
                            <MiniSparkline />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="font-mono text-muted-foreground">
                      {(player.simulation_strength ?? 0).toFixed(0)}
                    </td>
                    <td className="hidden md:table-cell font-mono text-muted-foreground">
                      {(player.path_strength ?? 0).toFixed(0)}
                    </td>
                    <td className={cn('font-mono', (player.form_trend ?? 0) >= 0 ? 'text-primary' : 'text-danger')}>
                      {(player.form_trend ?? 0) >= 0 ? '+' : ''}
                      {(player.form_trend ?? 0).toFixed(1)}
                    </td>
                    <td>
                      <TierBadge tier={player.tier} />
                    </td>
                    <td className="font-mono text-primary">{player.expected_points.toFixed(1)}</td>
                    <td className="hidden lg:table-cell font-mono text-muted-foreground">
                      {(player.risk_adj_value ?? 0).toFixed(2)}
                    </td>
                    <td className="hidden lg:table-cell font-mono text-muted-foreground">
                      {(100 / Math.max((player.points_std ?? 0) + 1, 1)).toFixed(1)}
                    </td>
                    <td className="font-mono">{player.avg_round.toFixed(1)}</td>
                    <td className="hidden md:table-cell text-sm text-muted-foreground">
                      {player.eliminator ? (
                        <span>
                          {player.eliminator}
                          {player.elim_rate !== null && player.elim_rate !== undefined
                            ? ` (${(player.elim_rate * 100).toFixed(0)}%)`
                            : ''}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                  {expandedPlayer === name && (
                    <tr>
                      <td colSpan={10} className="bg-elevated/60">
                        <div className="p-4 grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div>
                            <p className="text-xs text-muted-foreground mb-2">Path Map (avg opp Elo + elim%)</p>
                            <div className="flex items-center gap-2 flex-wrap">
                              {roundLabels.map((r) => {
                                const opponents = player.path_round_opponents?.[r] || [];
                                const topOpp = opponents[0]?.opponent;
                                return (
                                <div key={r} className="px-2 py-1 rounded bg-surface text-xs font-mono">
                                  <div>
                                    {r}:{' '}
                                    {player.path_rounds && player.path_rounds[r]
                                      ? player.path_rounds[r].toFixed(0)
                                      : '—'}
                                    {player.elim_round_probs && player.elim_round_probs[r] !== undefined
                                      ? ` · ${(player.elim_round_probs[r] * 100).toFixed(0)}%`
                                      : ''}
                                  </div>
                                  <div className="text-[10px] text-muted-foreground">
                                    {opponents.length
                                      ? opponents.map((o) => (
                                          <span
                                            key={o.opponent}
                                            className={cn(
                                              'mr-2',
                                              o.opponent === topOpp && 'text-primary font-medium'
                                            )}
                                          >
                                            {o.opponent} ({(o.win_prob * 100).toFixed(0)}% · {(o.meet_prob * 100).toFixed(0)}%)
                                          </span>
                                        ))
                                      : 'No frequent opponent'}
                                  </div>
                                </div>
                                );
                              })}
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-2">Round Tendencies</p>
                            <div className="text-sm text-muted-foreground">
                              Avg elim: {player.avg_round
                                ? roundLabels[Math.min(Math.max(0, Math.round(player.avg_round - 1)), roundLabels.length - 1)]
                                : '—'} ({player.avg_round.toFixed(2)}) · Median: {player.median_round !== null && player.median_round !== undefined
                                ? roundLabels[Math.min(Math.max(0, Math.round(player.median_round)), roundLabels.length - 1)]
                                : '—'} · Mode: {player.mode_round || '—'}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                  </>
                );})}
              </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
        </CardHeader>
        <CardContent>
          {!tierInsights && (
            <div className="text-sm text-muted-foreground">
              Run the optimizer to generate insights.
            </div>
          )}
          {tierInsights && (
            <div className="grid grid-cols-2 gap-4">
              {tierInsights.map(({ tier, top3, medianPoints }) => (
                <div key={tier} className="p-4 rounded-lg bg-elevated">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <TierBadge tier={tier} />
                      <span className="text-sm font-medium">Top 3 Picks</span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      median {medianPoints.toFixed(1)} pts
                    </span>
                  </div>
                  {top3.length === 0 && (
                    <div className="text-sm text-muted-foreground">No players in this tier.</div>
                  )}
                  {top3.map((p, idx) => (
                    <div key={p.player_name} className="flex items-center justify-between py-1">
                      <div className="text-sm font-medium">
                        {idx + 1}. {p.player_name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {p.expected_points.toFixed(1)} pts · risk {(p.risk_adj_value ?? 0).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

