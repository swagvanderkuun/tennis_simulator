'use client';

import { useEffect, useMemo, useState } from 'react';
import { Play, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '@/components/ui';
import { BracketTree } from '@/components/charts';
import { cn } from '@/lib/utils';
import {
  DrawMatch,
  getDrawMostLikely,
  getDrawProbabilities,
  getDrawSnapshot,
  getTournaments,
  TournamentProbabilities,
} from '@/lib/api';
import { useAppStore } from '@/lib/store';

export function BracketsPage() {
  const { tour, surface, setSurface, selectedTournamentId, setSelectedTournamentId } = useAppStore();
  const [selectedTournament, setSelectedTournament] = useState('—');
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<any>(null);
  const [drawMatches, setDrawMatches] = useState<DrawMatch[]>([]);
  const [probabilities, setProbabilities] = useState<TournamentProbabilities[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [formPreset, setFormPreset] = useState<'elo-only' | 'default-form' | 'form-heavy'>('default-form');
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    let mounted = true;
    const loadTournament = async () => {
      try {
        setIsLoading(true);
        if (!selectedTournamentId) {
          const list = await getTournaments(tour);
          if (!mounted) return;
          if (list.length > 0) {
            setSelectedTournamentId(list[0].id);
            setSelectedTournament(`${list[0].name} ${list[0].season_year}`);
          }
          return;
        }

        const snap = await getDrawSnapshot(selectedTournamentId);
        if (!mounted || !snap) return;
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

        const [tree, probs] = await Promise.all([
          getDrawMostLikely(snap.id, { ...baseWeights, ...formWeights }),
          getDrawProbabilities(snap.id, 1000),
        ]);
        if (!mounted) return;
        setDrawMatches(tree);
        setProbabilities(probs);
      } catch (err) {
        setDrawMatches([]);
        setProbabilities([]);
      } finally {
        if (mounted) {
          setIsLoading(false);
          setIsSimulating(false);
        }
      }
    };

    loadTournament();
    return () => {
      mounted = false;
    };
  }, [tour, selectedTournamentId, setSelectedTournamentId, surface, formPreset, refreshTick]);

  const buildTree = (matches: DrawMatch[]) => {
    if (!matches.length) return null;
    const byId = new Map<number, any>();
    matches.forEach((m) => {
      byId.set(m.id, {
        id: m.id,
        round: m.round,
        matchIndex: m.match_index,
        player1Name: m.player1_name || '',
        player2Name: m.player2_name || '',
        player1Bye: m.player1_bye,
        player2Bye: m.player2_bye,
        children: [],
      });
    });

    // Attach children
    matches.forEach((m) => {
      const node = byId.get(m.id);
      if (m.child_match1_id && byId.has(m.child_match1_id)) {
        node.children.push(byId.get(m.child_match1_id));
      }
      if (m.child_match2_id && byId.has(m.child_match2_id)) {
        node.children.push(byId.get(m.child_match2_id));
      }
    });

    // Root is final
    const finals = matches.filter((m) => m.round === 'F');
    const root = finals.length
      ? byId.get(finals.sort((a, b) => a.match_index - b.match_index)[0].id)
      : byId.get(matches[0].id);

    return root || null;
  };

  const bracketTree = useMemo(() => buildTree(drawMatches), [drawMatches]);
  const bracketDims = useMemo(() => {
    const rounds = new Set(drawMatches.map((m) => m.round)).size || 4;
    const leafCount = drawMatches.filter((m) => !m.child_match1_id && !m.child_match2_id).length || 16;
    return {
      width: Math.max(900, rounds * 220),
      height: Math.max(600, leafCount * 40),
    };
  }, [drawMatches]);

  const displayProbabilities = probabilities.length
    ? probabilities.slice(0, 10).map((p) => ({
        name: p.player_name,
        winProb: p.win_prob,
        finalProb: p.final_prob,
        semiProb: p.semi_prob,
        qfProb: p.qf_prob,
      }))
    : [];
  const upsetWatch = useMemo(() => {
    const candidates = drawMatches
      .filter(
        (m) =>
          m.player1_name &&
          m.player2_name &&
          typeof m.player1_prob === 'number' &&
          typeof m.player2_prob === 'number'
      )
      .map((m) => {
        const p1 = m.player1_prob ?? 0;
        const p2 = m.player2_prob ?? 0;
        const favorite = p1 >= p2 ? m.player1_name : m.player2_name;
        const underdog = p1 >= p2 ? m.player2_name : m.player1_name;
        const favoriteProb = Math.max(p1, p2);
        const underdogProb = Math.min(p1, p2);
        return {
          round: m.round,
          matchIndex: m.match_index,
          favorite,
          underdog,
          favoriteProb,
          underdogProb,
        };
      })
      .filter((m) => m.underdog && m.underdogProb > 0 && m.underdogProb <= 0.45)
      .sort((a, b) => b.underdogProb - a.underdogProb);

    return candidates.slice(0, 6);
  }, [drawMatches]);

  const handleSimulate = () => {
    setIsSimulating(true);
    setRefreshTick((v) => v + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Bracket View</h1>
          <p className="text-muted-foreground">{selectedTournament}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {(['overall', 'hard', 'clay', 'grass'] as const).map((s) => (
              <button
                key={s}
                onClick={() => {
                  setSurface(s);
                }}
                className={cn(
                  'px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-colors',
                  surface === s
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-elevated text-muted-foreground hover:text-foreground'
                )}
              >
                {s}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1">
            {(['elo-only', 'default-form', 'form-heavy'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setFormPreset(p)}
                className={cn(
                  'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                  formPreset === p
                    ? 'bg-secondary/20 text-secondary'
                    : 'bg-elevated text-muted-foreground hover:text-foreground'
                )}
              >
                {p === 'elo-only' ? 'Elo‑only' : p === 'form-heavy' ? 'Form‑heavy' : 'Default form'}
              </button>
            ))}
          </div>
          <Button onClick={handleSimulate} disabled={isSimulating} className="gap-2">
            <Play className="h-4 w-4" />
            {isSimulating ? 'Simulating...' : 'Refresh'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Bracket Tree */}
        <div className="col-span-3">
            {isLoading && (
              <div className="p-6">
                <div className="skeleton h-6 w-48 mb-4" />
                <div className="skeleton h-[560px] w-full" />
              </div>
            )}
            {!isLoading && bracketTree && (
              <BracketTree
                data={bracketTree}
                width={bracketDims.width}
                height={bracketDims.height}
                onNodeClick={(node) => setSelectedMatch(node)}
              />
            )}
            {!isLoading && !bracketTree && (
              <div className="p-6 text-sm text-muted-foreground">
                No draw data available for this tournament yet.
              </div>
            )}
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Probability Flow */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <TrendingUp className="h-4 w-4 text-primary" />
                Tournament Probabilities
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {isLoading && (
                <div className="space-y-3">
                  {Array.from({ length: 6 }).map((_, idx) => (
                    <div key={idx} className="skeleton h-8 w-full" />
                  ))}
                </div>
              )}
              {!isLoading && displayProbabilities.length === 0 && (
                <div className="text-sm text-muted-foreground">No probabilities available yet.</div>
              )}
              {displayProbabilities.map((p, idx) => (
                <div key={p.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{p.name}</span>
                    <span className="text-sm font-mono text-primary">
                      {(p.winProb * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-4 gap-1">
                    <div className="h-1.5 rounded-full bg-primary/80" style={{ opacity: p.qfProb }} />
                    <div className="h-1.5 rounded-full bg-primary/60" style={{ opacity: p.semiProb }} />
                    <div className="h-1.5 rounded-full bg-primary/40" style={{ opacity: p.finalProb }} />
                    <div className="h-1.5 rounded-full bg-primary" style={{ opacity: p.winProb * 2 }} />
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>QF</span>
                    <span>SF</span>
                    <span>F</span>
                    <span>W</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Upset Watch */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <AlertTriangle className="h-4 w-4 text-accent" />
                Upset Watch
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {isLoading && (
                <div className="space-y-2">
                  {Array.from({ length: 4 }).map((_, idx) => (
                    <div key={idx} className="skeleton h-8 w-full" />
                  ))}
                </div>
              )}
              {!isLoading && upsetWatch.length === 0 && (
                <div className="text-sm text-muted-foreground">
                  No likely upsets detected with the current presets.
                </div>
              )}
              {upsetWatch.map((m) => (
                <div key={`${m.round}-${m.matchIndex}`} className="rounded-md border border-border/60 p-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{m.round}</span>
                    <span>Match {m.matchIndex}</span>
                  </div>
                  <div className="mt-2 text-sm">
                    <span className="font-medium">{m.underdog}</span>
                    <span className="text-muted-foreground"> vs </span>
                    <span className="text-sm text-muted-foreground">{m.favorite}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between text-xs">
                    <span className="text-accent">Upset chance</span>
                    <span className="font-mono">{(m.underdogProb * 100).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Selected Match Details */}
          {selectedMatch && (
            <Card className="animate-fade-in">
              <CardHeader>
                <CardTitle className="text-sm">Match Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{selectedMatch.round}</span>
                    <span>Match {selectedMatch.matchIndex}</span>
                  </div>
                  <div className="rounded-md border border-border/60 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p
                          className={cn(
                            'font-medium',
                            selectedMatch.winner === selectedMatch.player1Name && 'text-primary'
                          )}
                        >
                          {selectedMatch.player1Name || 'TBD'}
                        </p>
                        <p className="text-xs text-muted-foreground">Player 1</p>
                      </div>
                      <p className="text-sm font-mono text-muted-foreground">
                        {typeof selectedMatch.player1Prob === 'number'
                          ? `${(selectedMatch.player1Prob * 100).toFixed(1)}%`
                          : '—'}
                      </p>
                    </div>
                    <div className="my-2 h-px bg-border/60" />
                    <div className="flex items-center justify-between">
                      <div>
                        <p
                          className={cn(
                            'font-medium',
                            selectedMatch.winner === selectedMatch.player2Name && 'text-primary'
                          )}
                        >
                          {selectedMatch.player2Name || 'TBD'}
                        </p>
                        <p className="text-xs text-muted-foreground">Player 2</p>
                      </div>
                      <p className="text-sm font-mono text-muted-foreground">
                        {typeof selectedMatch.player2Prob === 'number'
                          ? `${(selectedMatch.player2Prob * 100).toFixed(1)}%`
                          : '—'}
                      </p>
                    </div>
                  </div>
                  {selectedMatch.winner && (
                    <div className="rounded-md bg-elevated px-3 py-2 text-xs text-muted-foreground">
                      Most likely winner: <span className="text-foreground">{selectedMatch.winner}</span>
                    </div>
                  )}
                  {!selectedMatch.winner && (
                    <div className="rounded-md bg-elevated px-3 py-2 text-xs text-muted-foreground">
                      No winner projected yet for this matchup.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

