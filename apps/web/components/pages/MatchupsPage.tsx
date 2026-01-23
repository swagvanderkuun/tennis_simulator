'use client';

import { useEffect, useState } from 'react';
import { ArrowLeftRight, Play, Info, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, TierBadge } from '@/components/ui';
import { WinProbabilityGauge, RadarChart } from '@/components/charts';
import { cn, formatElo } from '@/lib/utils';
import { getPlayers, simulateMatch, Player, MatchSimResult } from '@/lib/api';
import { useAppStore } from '@/lib/store';

const FORM_PRESETS = ['elo-only', 'default-form', 'form-heavy'] as const;
type FormPreset = (typeof FORM_PRESETS)[number];

export function MatchupsPage() {
  const { tour, surface, setSurface, playersByTour, playersLoadedAt, setPlayersForTour } = useAppStore();
  const [players, setPlayers] = useState<Player[]>([]);
  const [player1, setPlayer1] = useState<Player | null>(null);
  const [player2, setPlayer2] = useState<Player | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState<MatchSimResult | null>(null);
  const [formPreset, setFormPreset] = useState<FormPreset>('default-form');

  useEffect(() => {
    let mounted = true;
    const loadPlayers = async () => {
      try {
        const cacheAge = playersLoadedAt[tour]
          ? Date.now() - (playersLoadedAt[tour] as number)
          : null;
        const cacheFresh = cacheAge !== null && cacheAge < 5 * 60 * 1000;
        if (cacheFresh && playersByTour[tour].length > 0) {
          setPlayers(playersByTour[tour]);
          if (playersByTour[tour].length >= 2) {
            setPlayer1(playersByTour[tour][0]);
            setPlayer2(playersByTour[tour][1]);
          }
          return;
        }

        // Request a reasonable chunk of players
        const data = await getPlayers({ tour, limit: 300 });
        if (!mounted) return;
        setPlayers(data);
        if (data.length >= 2) {
          setPlayer1(data[0]);
          setPlayer2(data[1]);
        }
        setPlayersForTour(tour, data);
      } catch (err) {
        setPlayers([]);
        setPlayer1(null);
        setPlayer2(null);
      }
    };
    loadPlayers();
    return () => {
      mounted = false;
    };
  }, [tour]);

  const handleSimulate = () => {
    if (!player1 || !player2) return;
    setIsSimulating(true);
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
    simulateMatch(player1.name, player2.name, tour, { ...baseWeights, ...formWeights })
      .then((result) => setSimResult(result))
      .catch(() => setSimResult(null))
      .finally(() => setIsSimulating(false));
  };

  // Auto-simulate when players change
  useEffect(() => {
    if (player1 && player2) {
      handleSimulate();
    }
  }, [player1?.id, player2?.id, tour, surface, formPreset]);

  const swapPlayers = () => {
    if (!player1 || !player2) return;
    const temp = player1;
    setPlayer1(player2);
    setPlayer2(temp);
    setSimResult(null);
  };

  const player1Prob = simResult?.player1_win_prob ?? 0.5;
  const player2Prob = simResult?.player2_win_prob ?? 0.5;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <h1 className="font-display text-3xl font-bold text-foreground">Match Simulation</h1>
        <div className="flex flex-wrap items-center gap-2">
          {(['overall', 'hard', 'clay', 'grass'] as const).map((s) => (
            <button
              key={s}
              onClick={() => {
                setSurface(s);
                setSimResult(null);
              }}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors',
                surface === s
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-elevated text-muted-foreground hover:text-foreground'
              )}
            >
              {s}
            </button>
          ))}
          {FORM_PRESETS.map((p) => (
            <button
              key={p}
              onClick={() => {
                setFormPreset(p);
                setSimResult(null);
              }}
              className={cn(
                'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                formPreset === p
                  ? 'bg-secondary/20 text-secondary'
                  : 'bg-elevated text-muted-foreground hover:text-foreground'
              )}
            >
              {p === 'elo-only' ? 'Elo‑only' : p === 'form-heavy' ? 'Form‑heavy' : 'Default form'}
            </button>
          ))}
        </div>
      </div>

      {/* Player Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-11 gap-4 items-center">
        {/* Player 1 */}
        <Card className="lg:col-span-5">
          <CardContent className="pt-6">
            {players.length === 0 ? (
              <div className="text-sm text-muted-foreground">No players loaded.</div>
            ) : (
            <select
              value={player1?.id || ''}
              onChange={(e) => {
                const p = players.find((p) => p.id === Number(e.target.value));
                if (p) {
                  setPlayer1(p);
                  setSimResult(null);
                }
              }}
              className="w-full p-3 rounded-lg bg-elevated border border-border text-lg font-medium focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {players.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            )}
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Tier</p>
                <TierBadge tier={player1?.tier || 'D'} className="mt-1" />
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Elo</p>
                <p className="font-mono text-primary">{formatElo(player1?.elo)}</p>
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground capitalize">{surface}</p>
                <p className="font-mono text-secondary">
                  {formatElo(
                    surface === 'hard'
                      ? player1?.helo
                      : surface === 'clay'
                      ? player1?.celo
                      : player1?.gelo
                  )}
                </p>
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Form</p>
                <p className={cn('font-mono', (player1?.form || 0) > 0 ? 'text-primary' : 'text-danger')}>
                  {(player1?.form || 0) > 0 ? '+' : ''}{(player1?.form || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Swap button */}
        <div className="lg:col-span-1 flex justify-center">
          <Button variant="outline" size="icon" onClick={swapPlayers}>
            <ArrowLeftRight className="h-5 w-5" />
          </Button>
        </div>

        {/* Player 2 */}
        <Card className="lg:col-span-5">
          <CardContent className="pt-6">
            {players.length === 0 ? (
              <div className="text-sm text-muted-foreground">No players loaded.</div>
            ) : (
            <select
              value={player2?.id || ''}
              onChange={(e) => {
                const p = players.find((p) => p.id === Number(e.target.value));
                if (p) {
                  setPlayer2(p);
                  setSimResult(null);
                }
              }}
              className="w-full p-3 rounded-lg bg-elevated border border-border text-lg font-medium focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {players.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            )}
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Tier</p>
                <TierBadge tier={player2?.tier || 'D'} className="mt-1" />
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Elo</p>
                <p className="font-mono text-primary">{formatElo(player2?.elo)}</p>
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground capitalize">{surface}</p>
                <p className="font-mono text-secondary">
                  {formatElo(
                    surface === 'hard'
                      ? player2?.helo
                      : surface === 'clay'
                      ? player2?.celo
                      : player2?.gelo
                  )}
                </p>
              </div>
              <div className="text-center p-2 rounded bg-elevated">
                <p className="text-xs text-muted-foreground">Form</p>
                <p className={cn('font-mono', (player2?.form || 0) > 0 ? 'text-primary' : 'text-danger')}>
                  {(player2?.form || 0) > 0 ? '+' : ''}{(player2?.form || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Win Probability & Simulate */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Win Probability</CardTitle>
          </CardHeader>
          <CardContent>
            <WinProbabilityGauge
              player1Name={player1?.name || 'Player 1'}
              player2Name={player2?.name || 'Player 2'}
              player1Prob={simResult?.player1_win_prob ?? 0.5}
              height={200}
            />
            <div className="flex justify-center mt-4">
              <Button
                size="lg"
                onClick={handleSimulate}
                disabled={isSimulating}
                className="gap-2"
              >
                <Play className="h-5 w-5" />
                {isSimulating ? 'Simulating...' : 'Simulate Match'}
              </Button>
            </div>
            {simResult && (
              <div className="mt-4 p-4 rounded-lg bg-primary/10 text-center animate-fade-in">
                <p className="text-sm text-muted-foreground mb-1">Match Result</p>
                <p className="text-xl font-display font-bold text-primary">
                  🏆 {simResult.winner_name} wins
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Score Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Score Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{player1?.name || 'Player 1'}</span>
                <span className="font-mono text-primary">{(player1Prob * 100).toFixed(1)}%</span>
              </div>
              <div className="h-2 rounded-full bg-elevated overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-500"
                  style={{ width: `${Math.min(100, player1Prob * 100)}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-sm pt-1">
                <span className="text-muted-foreground">{player2?.name || 'Player 2'}</span>
                <span className="font-mono text-secondary">{(player2Prob * 100).toFixed(1)}%</span>
              </div>
              <div className="h-2 rounded-full bg-elevated overflow-hidden">
                <div
                  className="h-full rounded-full bg-secondary transition-all duration-500"
                  style={{ width: `${Math.min(100, player2Prob * 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground pt-1">
                Match win split based on current simulation settings.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Explainability Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-secondary" />
            Why This Probability?
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!simResult?.factors?.length && (
            <div className="text-sm text-muted-foreground">
              Run a simulation to see factor breakdown.
            </div>
          )}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {(simResult?.factors || []).map((factor) => (
              <div key={factor.name} className="p-4 rounded-lg bg-elevated">
                <p className="text-sm font-medium text-foreground mb-2">{factor.name}</p>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-primary font-mono">{factor.player1_value}</span>
                  <span className="text-xs text-muted-foreground">vs</span>
                  <span className="text-xs text-secondary font-mono">{factor.player2_value}</span>
                </div>
                <div className="h-2 rounded-full bg-surface overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full',
                      factor.contribution > 0 ? 'bg-primary' : 'bg-secondary'
                    )}
                    style={{
                      width: `${Math.min(100, Math.abs(factor.contribution) * 1000)}%`,
                      marginLeft: factor.contribution > 0 ? '50%' : 'auto',
                      marginRight: factor.contribution < 0 ? '50%' : 'auto',
                    }}
                  />
                </div>
                <p className="text-xs text-center mt-1 text-muted-foreground">
                  Weight: {(factor.weight * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Radar Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Surface Profile Comparison</CardTitle>
        </CardHeader>
        <CardContent>
              <RadarChart
            data={[
              {
                    name: player1?.name || 'Player 1',
                    values: [
                      player1?.elo || 0,
                      player1?.helo || 0,
                      player1?.celo || 0,
                      player1?.gelo || 0,
                      (player1?.form || 0) + 1500,
                    ],
                color: '#38E07C',
              },
              {
                    name: player2?.name || 'Player 2',
                    values: [
                      player2?.elo || 0,
                      player2?.helo || 0,
                      player2?.celo || 0,
                      player2?.gelo || 0,
                      (player2?.form || 0) + 1500,
                    ],
                color: '#4CC9F0',
              },
            ]}
            indicators={[
              { name: 'Overall', max: 2500 },
              { name: 'Hard', max: 2500 },
              { name: 'Clay', max: 2500 },
              { name: 'Grass', max: 2500 },
              { name: 'Form', max: 2000 },
            ]}
            height={280}
          />
        </CardContent>
      </Card>
    </div>
  );
}

