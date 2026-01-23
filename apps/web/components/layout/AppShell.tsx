'use client';

import { useEffect, ReactNode } from 'react';
import { SideNav } from './SideNav';
import { TopBar } from './TopBar';
import { MobileNav } from './MobileNav';
import { getActiveTournament, getPlayers, getScoritoScoringRules, getTournaments } from '@/lib/api';
import { useAppStore } from '@/lib/store';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const {
    tour,
    surface,
    tournaments,
    selectedTournamentId,
    setTour,
    setSurface,
    setTournaments,
    setSelectedTournamentId,
  } = useAppStore();

  useEffect(() => {
    let mounted = true;

    const loadTournaments = async () => {
      try {
        const list = await getTournaments(tour);
        if (!mounted) return;
        setTournaments(list);

        // Always reset tournament selection when tour changes to pick best for new tour
        const active = await getActiveTournament(tour);
        if (!mounted) return;
        if (active) {
          setSelectedTournamentId(active.id);
        } else if (list.length > 0) {
          setSelectedTournamentId(list[0].id);
        } else {
          setSelectedTournamentId(null);
        }

        // Warm API cache for common endpoints
        getPlayers({ tour, limit: 1 }).catch(() => undefined);
        getScoritoScoringRules().catch(() => undefined);
      } catch (err) {
        // Keep UI functional even if API is unavailable
        if (mounted) {
          setTournaments([]);
          setSelectedTournamentId(null);
        }
      }
    };

    loadTournaments();
    return () => {
      mounted = false;
    };
  }, [tour, setSelectedTournamentId, setTournaments]);

  return (
    <div className="min-h-screen bg-background">
      <SideNav />
      <MobileNav />
      <TopBar
        tour={tour}
        onTourChange={setTour}
        surface={surface}
        onSurfaceChange={setSurface}
        tournaments={tournaments}
        selectedTournament={selectedTournamentId ?? undefined}
        onTournamentChange={(id) => setSelectedTournamentId(id)}
      />
      <main className="ml-0 md:ml-64 pt-0 md:pt-16 pb-28 md:pb-0 min-h-screen">
        <div className="p-4 md:p-6">{children}</div>
      </main>
    </div>
  );
}

