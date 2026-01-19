'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowUpRight, TrendingUp, Star, Trophy, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, GlassCard, MetricCard } from '@/components/ui';
import { DistributionChart } from '@/components/charts';
import {
  getActiveTournament,
  getFormMovers,
  getPredictionsSummary,
  getTopPicks,
  Tournament,
  TournamentProbabilities,
  Player,
} from '@/lib/api';
import { useAppStore } from '@/lib/store';

// Mock data for demonstration
const mockTopPicks = [
  { name: 'Jannik Sinner', tier: 'A', winProb: 0.28, elo: 2150, form: 45 },
  { name: 'Carlos Alcaraz', tier: 'A', winProb: 0.24, elo: 2120, form: 38 },
  { name: 'Novak Djokovic', tier: 'A', winProb: 0.18, elo: 2080, form: -12 },
  { name: 'Daniil Medvedev', tier: 'A', winProb: 0.08, elo: 1980, form: 15 },
];

const mockFormMovers = [
  { name: 'Ben Shelton', delta: 85, elo: 1820 },
  { name: 'Tommy Paul', delta: 62, elo: 1785 },
  { name: 'Holger Rune', delta: -45, elo: 1890 },
];

const mockRoundDistribution = [
  { label: 'R1', value: 128 },
  { label: 'R2', value: 64 },
  { label: 'R3', value: 32 },
  { label: 'R4', value: 16 },
  { label: 'QF', value: 8 },
  { label: 'SF', value: 4 },
  { label: 'F', value: 2 },
];

export function HomePage() {
  const { tour, selectedTournamentId, setSelectedTournamentId } = useAppStore();
  const [activeTournament, setActiveTournament] = useState<Tournament | null>(null);
  const [topPicks, setTopPicks] = useState<TournamentProbabilities[]>([]);
  const [formMovers, setFormMovers] = useState<Player[]>([]);
  const [predictionSummary, setPredictionSummary] = useState<{
    finalists: TournamentProbabilities[];
    semifinalists: TournamentProbabilities[];
    quarterfinalists: TournamentProbabilities[];
  } | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        const active = await getActiveTournament(tour);
        if (!mounted) return;
        setActiveTournament(active);
        if (active && !selectedTournamentId) {
          setSelectedTournamentId(active.id);
        }

        const targetId = selectedTournamentId || active?.id;
        if (targetId) {
          const [top, summary] = await Promise.all([
            getTopPicks(targetId),
            getPredictionsSummary(targetId),
          ]);
          if (!mounted) return;
          setTopPicks(top);
          setPredictionSummary(summary);
        }

        const movers = await getFormMovers(tour, 6);
        if (!mounted) return;
        setFormMovers(movers);
      } catch (err) {
        // Keep defaults if API is not available
      }
    };

    loadData();
    return () => {
      mounted = false;
    };
  }, [tour, selectedTournamentId, setSelectedTournamentId]);

  const displayTopPicks = topPicks.length
    ? topPicks.slice(0, 4).map((p, idx) => ({
        name: p.player_name,
        tier: 'A',
        winProb: p.win_prob,
        elo: 0,
        form: 0,
      }))
    : mockTopPicks;

  const displayFormMovers = formMovers.length
    ? formMovers.slice(0, 4).map((p) => ({
        name: p.name,
        delta: p.form || 0,
        elo: p.elo || 0,
      }))
    : mockFormMovers;

  const tournamentLabel = useMemo(() => {
    if (activeTournament) {
      return `${activeTournament.name} ${activeTournament.season_year}`;
    }
    return 'Australian Open 2026';
  }, [activeTournament]);

  return (
    <div className="space-y-8">
      {/* Tournament Spotlight Hero */}
      <GlassCard className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-secondary/10" />
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="chip chip-primary">{tour.toUpperCase()}</span>
              <span className="text-sm text-muted-foreground">Grand Slam</span>
            </div>
            <h1 className="font-display text-4xl font-bold text-foreground mb-2">
              {tournamentLabel}
            </h1>
            <p className="text-muted-foreground">
              Melbourne • Hard Court • Jan 13–26, 2026
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground mb-1">Favorite to Win</p>
            <p className="font-display text-2xl font-bold text-primary">
              {displayTopPicks[0]?.name || 'TBD'}
            </p>
            <p className="text-lg font-mono text-foreground">
              {displayTopPicks[0]?.winProb
                ? `${(displayTopPicks[0].winProb * 100).toFixed(1)}%`
                : '—'}
            </p>
          </div>
        </div>
      </GlassCard>

      {/* KPI Strip */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          label="Total Players"
          value="128"
          delta="Draw Complete"
          deltaType="positive"
        />
        <MetricCard
          label="Matches Simulated"
          value="10.2K"
          delta="+2.4K today"
          deltaType="positive"
        />
        <MetricCard
          label="Avg Elo (Top 32)"
          value="1,892"
          delta="+12 vs 2025"
          deltaType="positive"
        />
        <MetricCard
          label="Upset Watch"
          value="7"
          delta="R1 matches"
          deltaType="neutral"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Top Picks */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-accent" />
              Top Picks by Win Probability
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {displayTopPicks.map((player, idx) => (
                <div
                  key={player.name}
                  className={`player-card ${idx === 0 ? 'glow-primary' : ''}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`tier-badge tier-${player.tier.toLowerCase()}`}>
                          {player.tier}
                        </span>
                        {idx === 0 && (
                          <Star className="h-4 w-4 text-accent fill-accent" />
                        )}
                      </div>
                      <h3 className="font-medium text-foreground">{player.name}</h3>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-mono font-bold text-primary">
                        {(player.winProb * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-muted-foreground">Win Prob</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Elo:</span>{' '}
                      <span className="font-mono">{player.elo}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-muted-foreground">Form:</span>
                      <span
                        className={`font-mono ${
                          player.form > 0 ? 'text-primary' : 'text-danger'
                        }`}
                      >
                        {player.form > 0 ? '+' : ''}
                        {player.form}
                      </span>
                    </div>
                  </div>
                  {/* Probability bar */}
                  <div className="mt-3 prob-bar">
                    <div
                      className="prob-bar-fill bg-primary"
                      style={{ width: `${player.winProb * 100 * 3}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Form Movers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-secondary" />
              Form Movers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {displayFormMovers.map((player) => (
                <div
                  key={player.name}
                  className="flex items-center justify-between p-3 rounded-lg bg-elevated"
                >
                  <div>
                    <p className="font-medium text-foreground">{player.name}</p>
                    <p className="text-sm text-muted-foreground font-mono">
                      Elo {player.elo}
                    </p>
                  </div>
                  <div
                    className={`flex items-center gap-1 font-mono text-lg ${
                      player.delta > 0 ? 'text-primary' : 'text-danger'
                    }`}
                  >
                    {player.delta > 0 ? '+' : ''}
                    {player.delta}
                    {player.delta > 0 ? (
                      <ArrowUpRight className="h-4 w-4" />
                    ) : (
                      <ArrowUpRight className="h-4 w-4 rotate-90" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Prediction Summary */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-accent" />
              Round Progression Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <DistributionChart
              data={mockRoundDistribution}
              height={250}
              color="#4CC9F0"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <a
              href="/brackets"
              className="flex items-center justify-between p-3 rounded-lg bg-elevated hover:bg-elevated/80 transition-colors group"
            >
              <span className="text-foreground">View Full Bracket</span>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
            <a
              href="/matchups"
              className="flex items-center justify-between p-3 rounded-lg bg-elevated hover:bg-elevated/80 transition-colors group"
            >
              <span className="text-foreground">Simulate Matchup</span>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
            <a
              href="/scorito"
              className="flex items-center justify-between p-3 rounded-lg bg-elevated hover:bg-elevated/80 transition-colors group"
            >
              <span className="text-foreground">Scorito Optimizer</span>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
            <a
              href="/sim-lab"
              className="flex items-center justify-between p-3 rounded-lg bg-elevated hover:bg-elevated/80 transition-colors group"
            >
              <span className="text-foreground">Open Sim Lab</span>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

