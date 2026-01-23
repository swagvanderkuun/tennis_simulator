'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  Users,
  Swords,
  GitBranch,
  FlaskConical,
  Trophy,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getActiveTournament, getDrawSnapshot } from '@/lib/api';
import { useAppStore } from '@/lib/store';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/players', label: 'Players', icon: Users },
  { href: '/matchups', label: 'Matchups', icon: Swords },
  { href: '/brackets', label: 'Brackets', icon: GitBranch },
  { href: '/sim-lab', label: 'Sim Lab', icon: FlaskConical },
  { href: '/scorito', label: 'Scorito', icon: Trophy },
];

export function SideNav() {
  const pathname = usePathname();
  const { tour, selectedTournamentId } = useAppStore();
  const [dataAsOf, setDataAsOf] = useState('—');

  useEffect(() => {
    let mounted = true;
    const loadUpdatedAt = async () => {
      try {
        const active = await getActiveTournament(tour);
        if (!mounted) return;
        const targetId = selectedTournamentId || active?.id;
        if (!targetId) {
          setDataAsOf('—');
          return;
        }
        const snapshot = await getDrawSnapshot(targetId);
        if (!mounted) return;
        if (snapshot?.scraped_at) {
          const date = new Date(snapshot.scraped_at);
          setDataAsOf(
            date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
          );
        } else {
          setDataAsOf('—');
        }
      } catch {
        if (mounted) setDataAsOf('—');
      }
    };

    loadUpdatedAt();
    return () => {
      mounted = false;
    };
  }, [tour, selectedTournamentId]);

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 bg-surface border-r border-border md:block">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-border">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
          <img
            src="/racketroute-logo.png"
            alt="RacketRoute logo"
            className="h-7 w-7 object-contain"
          />
        </div>
        <div>
          <h1 className="font-display text-lg font-bold text-foreground">
            RacketRoute
          </h1>
          <p className="text-xs text-primary font-medium">Tennis Analytics</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn('nav-item', isActive && 'active')}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
        <Link href="/settings" className="nav-item">
          <Settings className="h-5 w-5" />
          <span>Settings</span>
        </Link>
        <div className="mt-4 px-4">
          <p className="text-xs text-muted-foreground">
            Data as of <span className="font-mono text-foreground">{dataAsOf}</span>
          </p>
        </div>
      </div>
    </aside>
  );
}



