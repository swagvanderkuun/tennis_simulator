'use client';

import { useEffect, useState } from 'react';
import { ArrowLeftRight, Play, Info, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, TierBadge } from '@/components/ui';
import { WinProbabilityGauge, RadarChart, DistributionChart } from '@/components/charts';
import { cn, formatElo } from '@/lib/utils';
import { getPlayers, simulateMatch, Player, MatchSimResult } from '@/lib/api';
import { useAppStore } from '@/lib/store';

// Mock players for selector
const mockPlayers = [
  { id: 1, name: 'Jannik Sinner', tier: 'A', elo: 2150, helo: 2180, celo: 2020, gelo: 2080, form: 45 },
  { id: 2, name: 'Carlos Alcaraz', tier: 'A', elo: 2120, helo: 2090, celo: 2180, gelo: 2150, form: 38 },
  { id: 3, name: 'Novak Djokovic', tier: 'A', elo: 2080, helo: 2100, celo: 2050, gelo: 2120, form: -12 },
  { id: 4, name: 'Daniil Medvedev', tier: 'A', elo: 1980, helo: 2020, celo: 1890, gelo: 1920, form: 15 },
];

// Mock explainability factors
const mockFactors = [
  { name: 'Overall Elo', p1: 2150, p2: 2120, weight: 0.45, contribution: 0.013 },
  { name: 'Hard Court Elo', p1: 2180, p2: 2090, weight: 0.25, contribution: 0.022 },
  { name: 'Clay Court Elo', p1: 2020, p2: 2180, weight: 0.20, contribution: -0.032 },
  { name: 'Grass Court Elo', p1: 2080, p2: 2150, weight: 0.10, contribution: -0.007 },
  { name: 'Form Adjustment', p1: 45, p2: 38, weight: 1.0, contribution: 0.008 },
];

// Mock score distribution
const mockScoreDistribution = [
  { label: '3-0', value: 28 },
  { label: '3-1', value: 35 },
  { label: '3-2', value: 22 },
  { label: '2-3', value: 8 },
  { label: '1-3', value: 5 },
  { label: '0-3', value: 2 },
];

export function MatchupsPage() {
  const { tour, playersByTour, playersLoadedAt, setPlayersForTour } = useAppStore();
  const [players, setPlayers] = useState<Player[]>([]);
  const [player1, setPlayer1] = useState<Player | null>(null);
  const [player2, setPlayer2] = useState<Player | null>(null);
  const [surface, setSurface] = useState<'hard' | 'clay' | 'grass'>('hard');
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState<MatchSimResult | null>(null);

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
        setPlayers(mockPlayers as unknown as Player[]);
        setPlayer1(mockPlayers[0] as unknown as Player);
        setPlayer2(mockPlayers[1] as unknown as Player);
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
    simulateMatch(player1.name, player2.name, tour)
      .then((result) => setSimResult(result))
      .catch(() => setSimResult(null))
      .finally(() => setIsSimulating(false));
  };

  // Auto-simulate when players change
  useEffect(() => {
    if (player1 && player2) {
      handleSimulate();
    }
  }, [player1?.id, player2?.id, tour]);

  const swapPlayers = () => {
    if (!player1 || !player2) return;
    const temp = player1;
    setPlayer1(player2);
    setPlayer2(temp);
    setSimResult(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl font-bold text-foreground">Match Simulation</h1>
        <div className="flex items-center gap-2">
          {['hard', 'clay', 'grass'].map((s) => (
            <button
              key={s}
              onClick={() => {
                setSurface(s as typeof surface);
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
        </div>
      </div>

      {/* Player Selection */}
      <div className="grid grid-cols-11 gap-4 items-center">
        {/* Player 1 */}
        <Card className="col-span-5">
          <CardContent className="pt-6">
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
            <div className="mt-4 grid grid-cols-4 gap-2">
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
                  {(player1?.form || 0) > 0 ? '+' : ''}{player1?.form || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Swap button */}
        <div className="col-span-1 flex justify-center">
          <Button variant="outline" size="icon" onClick={swapPlayers}>
            <ArrowLeftRight className="h-5 w-5" />
          </Button>
        </div>

        {/* Player 2 */}
        <Card className="col-span-5">
          <CardContent className="pt-6">
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
            <div className="mt-4 grid grid-cols-4 gap-2">
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
                  {(player2?.form || 0) > 0 ? '+' : ''}{player2?.form || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Win Probability & Simulate */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="col-span-2">
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
            <DistributionChart
              data={mockScoreDistribution}
              height={220}
              color="#4CC9F0"
            />
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
          <div className="grid grid-cols-5 gap-4">
            {(simResult?.factors?.length ? simResult.factors : mockFactors).map((factor) => (
              <div key={factor.name} className="p-4 rounded-lg bg-elevated">
                <p className="text-sm font-medium text-foreground mb-2">{factor.name}</p>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-primary font-mono">
                    {'player1_value' in factor ? factor.player1_value : factor.p1}
                  </span>
                  <span className="text-xs text-muted-foreground">vs</span>
                  <span className="text-xs text-secondary font-mono">
                    {'player2_value' in factor ? factor.player2_value : factor.p2}
                  </span>
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
            height={350}
          />
        </CardContent>
      </Card>
    </div>
  );
}

