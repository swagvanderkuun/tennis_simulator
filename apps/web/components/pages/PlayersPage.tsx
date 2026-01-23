'use client';

import { useEffect, useMemo, useState } from 'react';
import { Search, Filter, ChevronDown, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, TierBadge } from '@/components/ui';
import { EloTrendChart, RadarChart } from '@/components/charts';
import { cn, formatElo } from '@/lib/utils';
import { getPlayerEloHistory, getPlayers, Player, EloHistory } from '@/lib/api';
import { useAppStore } from '@/lib/store';

// Mock data
const mockPlayers = [
  { id: 1, name: 'Jannik Sinner', tier: 'A', elo: 2150, helo: 2180, celo: 2020, gelo: 2080, ranking: 1, form: 45, country: 'ITA' },
  { id: 2, name: 'Carlos Alcaraz', tier: 'A', elo: 2120, helo: 2090, celo: 2180, gelo: 2150, ranking: 2, form: 38, country: 'ESP' },
  { id: 3, name: 'Novak Djokovic', tier: 'A', elo: 2080, helo: 2100, celo: 2050, gelo: 2120, ranking: 3, form: -12, country: 'SRB' },
  { id: 4, name: 'Daniil Medvedev', tier: 'A', elo: 1980, helo: 2020, celo: 1890, gelo: 1920, ranking: 4, form: 15, country: 'RUS' },
  { id: 5, name: 'Alexander Zverev', tier: 'A', elo: 1950, helo: 1920, celo: 1980, gelo: 1900, ranking: 5, form: 22, country: 'GER' },
  { id: 6, name: 'Andrey Rublev', tier: 'B', elo: 1890, helo: 1920, celo: 1850, gelo: 1820, ranking: 6, form: -8, country: 'RUS' },
  { id: 7, name: 'Hubert Hurkacz', tier: 'B', elo: 1870, helo: 1890, celo: 1820, gelo: 1880, ranking: 7, form: 18, country: 'POL' },
  { id: 8, name: 'Taylor Fritz', tier: 'B', elo: 1860, helo: 1880, celo: 1790, gelo: 1850, ranking: 8, form: 25, country: 'USA' },
];

const mockEloHistory = [
  { date: '2025-07', elo: 1980, helo: 2010, celo: 1920, gelo: 1950 },
  { date: '2025-08', elo: 2020, helo: 2050, celo: 1960, gelo: 1980 },
  { date: '2025-09', elo: 2050, helo: 2080, celo: 1990, gelo: 2020 },
  { date: '2025-10', elo: 2080, helo: 2110, celo: 2000, gelo: 2040 },
  { date: '2025-11', elo: 2120, helo: 2150, celo: 2010, gelo: 2060 },
  { date: '2025-12', elo: 2150, helo: 2180, celo: 2020, gelo: 2080 },
];

export function PlayersPage() {
  const {
    tour,
    playersByTour,
    playersLoadedAt,
    setPlayersForTour,
  } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTiers, setSelectedTiers] = useState<string[]>(['A', 'B', 'C', 'D']);
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [eloHistory, setEloHistory] = useState<EloHistory[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const pageSize = 100;

  useEffect(() => {
    let mounted = true;
    const loadPlayers = async () => {
      try {
        setIsLoading(true);
        const cacheAge = playersLoadedAt[tour]
          ? Date.now() - (playersLoadedAt[tour] as number)
          : null;
        const cacheFresh = cacheAge !== null && cacheAge < 5 * 60 * 1000;

        if (cacheFresh && playersByTour[tour].length > 0) {
          setPlayers(playersByTour[tour]);
          setSelectedPlayer(playersByTour[tour][0] || null);
          setOffset(playersByTour[tour].length);
          setHasMore(playersByTour[tour].length % pageSize === 0);
          setIsLoading(false);
          return;
        }

        const data = await getPlayers({ tour, limit: pageSize, offset: 0 });
        if (!mounted) return;
        setPlayers(data);
        if (data.length > 0) {
          setSelectedPlayer(data[0]);
        }
        setOffset(data.length);
        setHasMore(data.length === pageSize);
        setPlayersForTour(tour, data);
      } catch (err) {
        if (!mounted) return;
        setPlayers([]);
        setSelectedPlayer(null);
        setOffset(0);
        setHasMore(false);
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };
    loadPlayers();
    return () => {
      mounted = false;
    };
  }, [tour]);

  const handleLoadMore = async () => {
    if (isLoadingMore || !hasMore) return;
    setIsLoadingMore(true);
    try {
      const data = await getPlayers({ tour, limit: pageSize, offset });
      const next = [...players, ...data];
      setPlayers(next);
      setPlayersForTour(tour, next);
      setOffset(next.length);
      setHasMore(data.length === pageSize);
    } catch {
      // ignore
    } finally {
      setIsLoadingMore(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    const loadHistory = async () => {
      if (!selectedPlayer) return;
      try {
        const history = await getPlayerEloHistory(selectedPlayer.id);
        if (!mounted) return;
        setEloHistory(history);
      } catch (err) {
        // fallback to mock history
        setEloHistory(mockEloHistory);
      }
    };
    loadHistory();
    return () => {
      mounted = false;
    };
  }, [selectedPlayer]);

  const filteredPlayers = useMemo(() => {
    const source = players;
    return source.filter((p) => {
      const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesTier = selectedTiers.includes(p.tier);
      return matchesSearch && matchesTier;
    });
  }, [players, searchQuery, selectedTiers]);

  const toggleTier = (tier: string) => {
    setSelectedTiers((prev) =>
      prev.includes(tier) ? prev.filter((t) => t !== tier) : [...prev, tier]
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl font-bold text-foreground">Players</h1>
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search players..."
              className="w-64 pl-9 pr-4 py-2 rounded-lg bg-elevated border border-border text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          {/* Filter toggle */}
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2"
          >
            <Filter className="h-4 w-4" />
            Filters
            <ChevronDown
              className={cn(
                'h-4 w-4 transition-transform',
                showFilters && 'rotate-180'
              )}
            />
          </Button>
        </div>
      </div>

      {/* Filters panel */}
      {showFilters && (
        <Card className="animate-slide-in">
          <CardContent className="pt-6">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-sm font-medium text-foreground mb-2">Tier</p>
                <div className="flex items-center gap-2">
                  {['A', 'B', 'C', 'D'].map((tier) => (
                    <button
                      key={tier}
                      onClick={() => toggleTier(tier)}
                      className={cn(
                        'tier-badge cursor-pointer transition-opacity',
                        `tier-${tier.toLowerCase()}`,
                        !selectedTiers.includes(tier) && 'opacity-30'
                      )}
                    >
                      {tier}
                    </button>
                  ))}
                </div>
              </div>
              <div className="h-8 w-px bg-border" />
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {filteredPlayers.length} players
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedTiers(['A', 'B', 'C', 'D']);
                  }}
                >
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Player Table */}
        <Card className="lg:col-span-2">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6">
                <div className="skeleton h-6 w-48 mb-4" />
                <div className="space-y-3">
                  {Array.from({ length: 8 }).map((_, idx) => (
                    <div key={idx} className="skeleton h-10 w-full" />
                  ))}
                </div>
              </div>
            ) : (
              <div className="w-full overflow-x-auto">
                <table className="data-table min-w-[720px]">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Player</th>
                      <th>Tier</th>
                      <th>Elo</th>
                      <th className="hidden md:table-cell">Hard</th>
                      <th className="hidden md:table-cell">Clay</th>
                      <th className="hidden md:table-cell">Grass</th>
                      <th>Form</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPlayers.map((player) => (
                      <tr
                        key={player.id}
                        onClick={() => setSelectedPlayer(player)}
                        className={cn(
                          'cursor-pointer',
                          selectedPlayer?.id === player.id && 'bg-primary/5'
                        )}
                      >
                        <td className="font-mono text-muted-foreground">
                          {player.ranking ? `#${player.ranking}` : '—'}
                        </td>
                        <td>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{player.name}</span>
                            {player.country && (
                              <span className="text-xs text-muted-foreground">
                                {player.country}
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <TierBadge tier={player.tier} />
                        </td>
                        <td className="font-mono">{formatElo(player.elo)}</td>
                        <td className="hidden md:table-cell font-mono text-secondary">
                          {formatElo(player.helo)}
                        </td>
                        <td className="hidden md:table-cell font-mono text-accent">
                          {formatElo(player.celo)}
                        </td>
                        <td className="hidden md:table-cell font-mono text-primary">
                          {formatElo(player.gelo)}
                        </td>
                        <td>
                          <span
                            className={cn(
                              'font-mono',
                              (player.form ?? 0) > 0 ? 'text-primary' : 'text-danger'
                            )}
                          >
                            {(player.form ?? 0) > 0 ? '+' : ''}
                            {(player.form ?? 0).toFixed(2)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {hasMore && (
                  <div className="p-4 flex justify-center">
                    <Button
                      variant="outline"
                      onClick={handleLoadMore}
                      disabled={isLoadingMore}
                    >
                      {isLoadingMore ? 'Loading...' : 'Load more'}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Player Profile */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{selectedPlayer?.name || 'Select Player'}</CardTitle>
                <TierBadge tier={selectedPlayer?.tier || 'D'} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center p-3 rounded-lg bg-elevated">
                  <p className="text-xs text-muted-foreground mb-1">Overall Elo</p>
                  <p className="text-xl font-mono font-bold text-foreground">
                    {formatElo(selectedPlayer?.elo)}
                  </p>
                </div>
                <div className="text-center p-3 rounded-lg bg-elevated">
                  <p className="text-xs text-muted-foreground mb-1">World Rank</p>
                  <p className="text-xl font-mono font-bold text-foreground">
                    {selectedPlayer?.ranking ? `#${selectedPlayer.ranking}` : '—'}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center p-2 rounded bg-secondary/10">
                  <p className="text-xs text-secondary">Hard</p>
                  <p className="font-mono text-sm">{formatElo(selectedPlayer?.helo)}</p>
                </div>
                <div className="text-center p-2 rounded bg-accent/10">
                  <p className="text-xs text-accent">Clay</p>
                  <p className="font-mono text-sm">{formatElo(selectedPlayer?.celo)}</p>
                </div>
                <div className="text-center p-2 rounded bg-primary/10">
                  <p className="text-xs text-primary">Grass</p>
                  <p className="font-mono text-sm">{formatElo(selectedPlayer?.gelo)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Radar Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Surface Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <RadarChart
                data={[
                  {
                    name: selectedPlayer?.name || '',
                    values: [
                      selectedPlayer?.elo || 0,
                      selectedPlayer?.helo || 0,
                      selectedPlayer?.celo || 0,
                      selectedPlayer?.gelo || 0,
                      (selectedPlayer?.form || 0) + 1500,
                    ],
                  },
                ]}
                indicators={[
                  { name: 'Overall', max: 2500 },
                  { name: 'Hard', max: 2500 },
                  { name: 'Clay', max: 2500 },
                  { name: 'Grass', max: 2500 },
                  { name: 'Form', max: 2000 },
                ]}
                height={250}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Elo Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Elo Trend — {selectedPlayer?.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <EloTrendChart
            data={eloHistory.length ? eloHistory : mockEloHistory}
            showConfidenceBands={true}
            selectedMetrics={['elo', 'helo', 'celo', 'gelo']}
            height={300}
          />
        </CardContent>
      </Card>
    </div>
  );
}

