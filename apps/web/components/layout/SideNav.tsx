'use client';

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

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-surface border-r border-border">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-border">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/20">
          <span className="text-xl">🎾</span>
        </div>
        <div>
          <h1 className="font-display text-lg font-bold text-foreground">
            Tournament
          </h1>
          <p className="text-xs text-primary font-medium">Studio</p>
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
            Data as of <span className="font-mono text-foreground">Jan 16, 2026</span>
          </p>
        </div>
      </div>
    </aside>
  );
}



