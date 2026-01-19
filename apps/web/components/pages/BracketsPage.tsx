'use client';

import { useEffect, useMemo, useState } from 'react';
import { Play, AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '@/components/ui';
import { BracketTree } from '@/components/charts';
import { cn } from '@/lib/utils';
import {
  DrawMatch,
  getDrawProbabilities,
  getDrawSnapshot,
  getDrawTree,
  getTournaments,
  TournamentProbabilities,
} from '@/lib/api';
import { useAppStore } from '@/lib/store';

export function BracketsPage() {
  const { tour, selectedTournamentId, setSelectedTournamentId } = useAppStore();
  const [selectedTournament, setSelectedTournament] = useState('Australian Open 2026');
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<any>(null);
  const [drawMatches, setDrawMatches] = useState<DrawMatch[]>([]);
  const [probabilities, setProbabilities] = useState<TournamentProbabilities[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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

        const [tree, probs] = await Promise.all([
          getDrawTree(snap.id),
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
        }
      }
    };

    loadTournament();
    return () => {
      mounted = false;
    };
  }, [tour, selectedTournamentId, setSelectedTournamentId]);

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

  const displayProbabilities = probabilities.length
    ? probabilities.slice(0, 10).map((p) => ({
        name: p.player_name,
        winProb: p.win_prob,
        finalProb: p.final_prob,
        semiProb: p.semi_prob,
        qfProb: p.qf_prob,
      }))
    : [];

  const handleSimulate = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
    }, 1500);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Bracket View</h1>
          <p className="text-muted-foreground">{selectedTournament}</p>
        </div>
        <Button onClick={handleSimulate} disabled={isSimulating} className="gap-2">
          <Play className="h-4 w-4" />
          {isSimulating ? 'Simulating...' : 'Run Simulation'}
        </Button>
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
                width={900}
                height={600}
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
              <div className="text-sm text-muted-foreground">
                Upset watch will populate once match probabilities are available.
              </div>
            </CardContent>
          </Card>

          {/* Selected Match Details */}
          {selectedMatch && (
            <Card className="animate-fade-in">
              <CardHeader>
                <CardTitle className="text-sm">Match Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-2">
                  <p className="text-xs text-muted-foreground">{selectedMatch.round}</p>
                  <div className="flex items-center justify-center gap-4">
                    <div className="text-right">
                      <p className={cn(
                        'font-medium',
                        selectedMatch.winner === selectedMatch.player1Name && 'text-primary'
                      )}>
                        {selectedMatch.player1Name}
                      </p>
                      <p className="text-sm font-mono text-muted-foreground">
                        {(selectedMatch.player1Prob * 100).toFixed(1)}%
                      </p>
                    </div>
                    <span className="text-muted-foreground">vs</span>
                    <div className="text-left">
                      <p className={cn(
                        'font-medium',
                        selectedMatch.winner === selectedMatch.player2Name && 'text-primary'
                      )}>
                        {selectedMatch.player2Name}
                      </p>
                      <p className="text-sm font-mono text-muted-foreground">
                        {(selectedMatch.player2Prob * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

