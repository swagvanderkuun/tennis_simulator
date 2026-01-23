'use client';

import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Surface } from '@/lib/store';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';

interface TopBarProps {
  tournaments?: { id: number; name: string }[];
  selectedTournament?: number;
  onTournamentChange?: (id: number) => void;
  tour: 'atp' | 'wta';
  onTourChange: (tour: 'atp' | 'wta') => void;
  surface?: Surface;
  onSurfaceChange?: (surface: Surface) => void;
}

export function TopBar({
  tournaments = [],
  selectedTournament,
  onTournamentChange,
  tour,
  onTourChange,
  surface,
  onSurfaceChange,
}: TopBarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [showHeader, setShowHeader] = useState(true);

  useEffect(() => {
    let lastY = window.scrollY;
    let ticking = false;

    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(() => {
        const currentY = window.scrollY;
        const delta = currentY - lastY;
        if (!menuOpen) {
          if (currentY < 8) {
            setShowHeader(true);
          } else if (delta > 10) {
            setShowHeader(false);
          } else if (delta < -10) {
            setShowHeader(true);
          }
        }
        lastY = currentY;
        ticking = false;
      });
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [menuOpen]);

  return (
    <header
      className={cn(
        'sticky top-0 left-0 right-0 z-30 bg-surface/80 backdrop-blur-xl border-b border-border pt-[env(safe-area-inset-top)] transition-transform duration-200 md:fixed md:pt-0 md:left-64 md:right-0',
        showHeader || menuOpen ? 'translate-y-0' : '-translate-y-full'
      )}
    >
      <div className="flex items-center justify-between px-4 py-3 md:hidden">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <img
              src="/racketroute-logo.png"
              alt="RacketRoute logo"
              className="h-5 w-5 object-contain"
            />
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">RacketRoute</p>
            <p className="text-[11px] text-muted-foreground">Quick controls</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="p-2 rounded-lg bg-elevated text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Toggle menu"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {menuOpen && (
        <div className="px-4 pb-4 md:hidden">
          <div className="flex flex-col gap-3">
            <div className="flex rounded-lg bg-elevated p-1 w-fit">
              <button
                onClick={() => onTourChange('atp')}
                className={cn(
                  'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
                  tour === 'atp'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                ATP
              </button>
              <button
                onClick={() => onTourChange('wta')}
                className={cn(
                  'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
                  tour === 'wta'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                WTA
              </button>
            </div>

            {tournaments.length > 0 && onTournamentChange && (
              <Select
                value={selectedTournament ? String(selectedTournament) : undefined}
                onValueChange={(value) => onTournamentChange(Number(value))}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Tournament" />
                </SelectTrigger>
                <SelectContent>
                  {tournaments.map((t) => (
                    <SelectItem key={t.id} value={String(t.id)}>
                      {t.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {onSurfaceChange && (
              <div className="flex flex-wrap items-center gap-2">
                {(['overall', 'hard', 'clay', 'grass'] as Surface[]).map((s) => (
                  <button
                    key={s}
                    onClick={() => onSurfaceChange(s)}
                    className={cn(
                      'px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-colors',
                      surface === s
                        ? 'bg-secondary/20 text-secondary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-elevated'
                    )}
                  >
                    {s === 'overall' ? 'overall' : s}
                  </button>
                ))}
              </div>
            )}

          </div>
        </div>
      )}

      <div className="hidden md:flex h-full items-center justify-between px-6 md:py-0 md:h-16">
        {/* Left: Context selectors */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-4">
          {/* Tour toggle */}
          <div className="flex rounded-lg bg-elevated p-1 w-fit">
            <button
              onClick={() => onTourChange('atp')}
              className={cn(
                'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
                tour === 'atp'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              ATP
            </button>
            <button
              onClick={() => onTourChange('wta')}
              className={cn(
                'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
                tour === 'wta'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              WTA
            </button>
          </div>

          {/* Tournament selector */}
          {tournaments.length > 0 && onTournamentChange && (
            <Select
              value={selectedTournament ? String(selectedTournament) : undefined}
              onValueChange={(value) => onTournamentChange(Number(value))}
            >
              <SelectTrigger className="w-full md:w-64">
                <SelectValue placeholder="Select Tournament" />
              </SelectTrigger>
              <SelectContent>
                {tournaments.map((t) => (
                  <SelectItem key={t.id} value={String(t.id)}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          {/* Surface selector */}
          {onSurfaceChange && (
            <div className="flex flex-wrap items-center gap-2">
              {(['overall', 'hard', 'clay', 'grass'] as Surface[]).map((s) => (
                <button
                  key={s}
                  onClick={() => onSurfaceChange(s)}
                  className={cn(
                    'px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-colors',
                    surface === s
                      ? 'bg-secondary/20 text-secondary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-elevated'
                  )}
                >
                  {s === 'overall' ? 'overall' : s}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: User */}
        <div className="flex items-center justify-between gap-4 md:justify-end">
          {/* User menu placeholder */}
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-primary text-sm font-medium">
            U
          </div>
        </div>
      </div>
    </header>
  );
}

