'use client';

import { useEffect } from 'react';
import {
  ArrowUpRight,
  Brackets,
  Compass,
  Layers,
  LineChart,
  ListChecks,
  Settings,
  Users,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, GlassCard } from '@/components/ui';

const quickLinks = [
  {
    title: 'Players',
    description: 'Browse rankings, Elo trends, and player profiles.',
    href: '/players',
    icon: Users,
  },
  {
    title: 'Matchups',
    description: 'Compare two players and inspect the matchup breakdown.',
    href: '/matchups',
    icon: LineChart,
  },
  {
    title: 'Brackets',
    description: 'Explore draw structure and most-likely outcomes.',
    href: '/brackets',
    icon: Brackets,
  },
  {
    title: 'Scorito',
    description: 'Optimize lineups and compare value across tiers.',
    href: '/scorito',
    icon: ListChecks,
  },
  {
    title: 'Sim Lab',
    description: 'Run custom scenarios and sensitivity checks.',
    href: '/sim-lab',
    icon: Layers,
  },
];

const supportingLinks = [
  {
    title: 'Scoring Rules',
    description: 'Adjust scoring and preferences before optimizing.',
    href: '/settings',
    icon: Settings,
  },
  {
    title: 'Scenario Lab',
    description: 'Run custom weight presets and stress test outcomes.',
    href: '/sim-lab',
    icon: Layers,
  },
];

const playbook = [
  {
    title: 'Signals',
    description: 'Elo, form, and surface cues in one view.',
    icon: Compass,
  },
  {
    title: 'Scenarios',
    description: 'Preset weights to stress‑test outcomes.',
    icon: Layers,
  },
  {
    title: 'Picks',
    description: 'Balance upside and risk before locking in.',
    icon: ListChecks,
  },
];

export function HomePage() {
  useEffect(() => {
    const elements = Array.from(document.querySelectorAll<HTMLElement>('.reveal'));
    if (elements.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="space-y-12">
      <GlassCard className="relative overflow-hidden reveal">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/15 via-transparent to-secondary/10" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <img
              src="/racketroute-logo.png"
              alt="RacketRoute logo"
              className="h-10 w-10 object-contain"
            />
            <span className="chip chip-primary">RacketRoute</span>
            <span className="text-sm text-muted-foreground">Welcome</span>
          </div>
          <div className="space-y-4">
            <h1 className="font-display text-4xl font-bold text-foreground">
              Route the draw. Own the picks.
            </h1>
            <p className="text-muted-foreground text-sm max-w-xl">
              Player intel, matchup reasoning, Scorito optimization — streamlined.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <a
              href="/players"
              className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:opacity-90 transition"
            >
              Get started
              <ArrowUpRight className="h-4 w-4" />
            </a>
            <a
              href="/scorito"
              className="inline-flex items-center gap-2 rounded-full bg-elevated px-4 py-2 text-sm font-medium text-foreground hover:bg-elevated/80 transition"
            >
              Go to Scorito
              <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
            </a>
          </div>
        </div>
      </GlassCard>

      <section className="space-y-4 reveal">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Core tools</h2>
          <p className="text-sm text-muted-foreground">Choose a tool to begin.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {quickLinks.map((link) => {
          const Icon = link.icon;
          return (
              <Card key={link.title} className="group reveal">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Icon className="h-4 w-4 text-primary" />
                  {link.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">{link.description}</p>
                <a
                  href={link.href}
                  className="inline-flex items-center gap-2 text-sm text-foreground group-hover:text-primary transition-colors"
                >
                  Open {link.title}
                  <ArrowUpRight className="h-4 w-4" />
                </a>
              </CardContent>
            </Card>
          );
        })}
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6 reveal">
        <Card className="xl:col-span-2 reveal">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Compass className="h-5 w-5 text-primary" />
              Playbook
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {playbook.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="rounded-xl border border-border/60 p-4 reveal">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="h-4 w-4 text-primary" />
                    <p className="text-sm font-medium text-foreground">{item.title}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card className="reveal">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-accent" />
              Supporting tools
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {supportingLinks.map((link) => {
              const Icon = link.icon;
              return (
                <div key={link.title} className="rounded-lg bg-elevated p-3 reveal">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-secondary" />
                    <p className="text-sm font-medium text-foreground">{link.title}</p>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{link.description}</p>
                  <a
                    href={link.href}
                    className="mt-2 inline-flex items-center gap-2 text-xs text-foreground hover:text-primary transition-colors"
                  >
                    Open {link.title}
                    <ArrowUpRight className="h-3 w-3" />
                  </a>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

