'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
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
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="fixed top-0 left-64 right-0 z-30 h-16 bg-surface/80 backdrop-blur-xl border-b border-border">
      <div className="flex h-full items-center justify-between px-6">
        {/* Left: Context selectors */}
        <div className="flex items-center gap-4">
          {/* Tour toggle */}
          <div className="flex rounded-lg bg-elevated p-1">
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
              <SelectTrigger className="w-64">
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
            <div className="flex items-center gap-2">
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

        {/* Right: Search and user */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            {searchOpen ? (
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onBlur={() => !searchQuery && setSearchOpen(false)}
                placeholder="Search players..."
                className="w-64 px-4 py-2 rounded-lg bg-elevated border border-border text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                autoFocus
              />
            ) : (
              <button
                onClick={() => setSearchOpen(true)}
                className="p-2 rounded-lg hover:bg-elevated transition-colors"
              >
                <Search className="h-5 w-5 text-muted-foreground" />
              </button>
            )}
          </div>

          {/* User menu placeholder */}
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-primary text-sm font-medium">
            U
          </div>
        </div>
      </div>
    </header>
  );
}

