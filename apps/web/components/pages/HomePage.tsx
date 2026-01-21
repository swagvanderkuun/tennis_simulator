'use client';

import {
  ArrowUpRight,
  BookOpen,
  Brackets,
  CalendarCheck,
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
    description: 'Compare two players and inspect the match breakdown.',
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
  {
    title: 'Settings',
    description: 'Tune scoring rules and global preferences.',
    href: '/settings',
    icon: Settings,
  },
];

const featureHighlights = [
  {
    title: 'Player Explorer',
    detail: 'Find form movers, Elo leaders, and head-to-head context.',
    icon: Users,
  },
  {
    title: 'Bracket Intelligence',
    detail: 'Read the most likely draw path at a glance.',
    icon: Brackets,
  },
  {
    title: 'Matchup Explainability',
    detail: 'See Elo, surface, and form factors driving outcomes.',
    icon: LineChart,
  },
  {
    title: 'Scorito Optimizer',
    detail: 'Balance upside, risk, and tier constraints.',
    icon: ListChecks,
  },
  {
    title: 'Scenario Sandbox',
    detail: 'Test presets and run custom weights.',
    icon: Layers,
  },
  {
    title: 'Scoring Control',
    detail: 'Manage scoring rules without leaving the app.',
    icon: Settings,
  },
];

const onboardingSteps = [
  {
    title: 'Start with players',
    description: 'Explore tiers, form trends, and Elo history.',
    href: '/players',
    icon: Compass,
  },
  {
    title: 'Validate matchups',
    description: 'Simulate the head-to-head you care about.',
    href: '/matchups',
    icon: LineChart,
  },
  {
    title: 'Build a lineup',
    description: 'Optimize your Scorito roster in minutes.',
    href: '/scorito',
    icon: ListChecks,
  },
];

export function HomePage() {
  return (
    <div className="space-y-10">
      <GlassCard className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/15 via-transparent to-secondary/10" />
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <span className="chip chip-primary">Tournament Studio</span>
            <span className="text-sm text-muted-foreground">Site overview</span>
          </div>
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <h1 className="font-display text-4xl font-bold text-foreground mb-2">
                Choose your workflow
              </h1>
              <p className="text-muted-foreground text-sm max-w-xl">
                Navigate the dashboard by function. Explore player intelligence, evaluate matchups,
                inspect brackets, or optimize Scorito lineups with clear, fast workflows.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <a
                href="/players"
                className="flex items-center justify-between rounded-lg border border-border/60 bg-elevated px-4 py-3 text-sm hover:bg-elevated/80 transition-colors group"
              >
                <span className="text-foreground">Open Players</span>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </a>
              <a
                href="/scorito"
                className="flex items-center justify-between rounded-lg border border-border/60 bg-elevated px-4 py-3 text-sm hover:bg-elevated/80 transition-colors group"
              >
                <span className="text-foreground">Launch Scorito</span>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </a>
              <a
                href="/brackets"
                className="flex items-center justify-between rounded-lg border border-border/60 bg-elevated px-4 py-3 text-sm hover:bg-elevated/80 transition-colors group"
              >
                <span className="text-foreground">View Brackets</span>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </a>
              <a
                href="/matchups"
                className="flex items-center justify-between rounded-lg border border-border/60 bg-elevated px-4 py-3 text-sm hover:bg-elevated/80 transition-colors group"
              >
                <span className="text-foreground">Compare Matchups</span>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </a>
            </div>
          </div>
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {quickLinks.map((link) => {
          const Icon = link.icon;
          return (
            <Card key={link.title} className="group">
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

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-accent" />
              What you can do here
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {featureHighlights.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="rounded-lg border border-border/60 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="h-4 w-4 text-secondary" />
                      <p className="text-sm font-medium text-foreground">{feature.title}</p>
                    </div>
                    <p className="text-sm text-muted-foreground">{feature.detail}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarCheck className="h-5 w-5 text-primary" />
              Quick start flow
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {onboardingSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={step.title} className="rounded-lg bg-elevated p-3">
                  <div className="flex items-start gap-3">
                    <span className="chip chip-muted">Step {idx + 1}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <Icon className="h-4 w-4 text-primary" />
                        <p className="text-sm font-medium text-foreground">{step.title}</p>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
                      <a
                        href={step.href}
                        className="mt-2 inline-flex items-center gap-2 text-xs text-foreground hover:text-primary transition-colors"
                      >
                        Go to {step.title}
                        <ArrowUpRight className="h-3 w-3" />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

