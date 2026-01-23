'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Users, Swords, GitBranch, Trophy, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/players', label: 'Players', icon: Users },
  { href: '/matchups', label: 'Matchups', icon: Swords },
  { href: '/brackets', label: 'Brackets', icon: GitBranch },
  { href: '/scorito', label: 'Scorito', icon: Trophy },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t border-border bg-surface/95 backdrop-blur md:hidden pb-[env(safe-area-inset-bottom)]">
      {navItems.map((item) => {
        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex flex-col items-center gap-1 px-3 py-2 text-[11px] text-muted-foreground',
              isActive && 'text-primary'
            )}
          >
            <Icon className="h-5 w-5" />
            <span>{item.label}</span>
          </Link>
        );
      })}
      <Link
        href="/settings"
        className={cn(
          'flex flex-col items-center gap-1 px-3 py-2 text-[11px] text-muted-foreground',
          pathname.startsWith('/settings') && 'text-primary'
        )}
      >
        <Settings className="h-5 w-5" />
        <span>Settings</span>
      </Link>
    </nav>
  );
}

