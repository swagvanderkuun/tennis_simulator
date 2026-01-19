'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle, Button, TierBadge } from '@/components/ui';
import { Settings, Database, Palette, Bell, User } from 'lucide-react';
import { getScoritoScoringRules } from '@/lib/api';

const DEFAULT_SCORING = {
  A: [10, 20, 30, 40, 60, 80, 100],
  B: [20, 40, 60, 80, 100, 120, 140],
  C: [30, 60, 90, 120, 140, 160, 180],
  D: [60, 90, 120, 160, 180, 200, 200],
};
const ROUND_LABELS = ['R1', 'R2', 'R3', 'R4', 'QF', 'SF', 'F'];
const SCORING_STORAGE_KEY = 'scorito_scoring_rules_v1';

export default function SettingsPage() {
  const [scoring, setScoring] = useState(DEFAULT_SCORING);
  const [roundLabels, setRoundLabels] = useState(ROUND_LABELS);

  useEffect(() => {
    let mounted = true;
    const loadScoring = async () => {
      try {
        if (typeof window !== 'undefined') {
          const stored = window.localStorage.getItem(SCORING_STORAGE_KEY);
          if (stored) {
            const parsed = JSON.parse(stored) as {
              scoring: typeof DEFAULT_SCORING;
              rounds: typeof ROUND_LABELS;
            };
            if (parsed?.scoring && parsed?.rounds) {
              if (!mounted) return;
              setScoring(parsed.scoring);
              setRoundLabels(parsed.rounds);
              return;
            }
          }
        }

        const rules = await getScoritoScoringRules();
        if (!mounted) return;
        setScoring(rules.scoring as typeof DEFAULT_SCORING);
        setRoundLabels(rules.rounds as typeof ROUND_LABELS);
      } catch (err) {
        // Keep defaults
      }
    };
    loadScoring();
    return () => {
      mounted = false;
    };
  }, []);

  const handleScoringChange = (tier: string, roundIdx: number, value: number) => {
    setScoring((prev) => {
      const next = {
        ...prev,
        [tier]: prev[tier as keyof typeof prev].map((v, i) => (i === roundIdx ? value : v)),
      } as typeof prev;
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(
          SCORING_STORAGE_KEY,
          JSON.stringify({ scoring: next, rounds: roundLabels })
        );
      }
      return next;
    });
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Configure your Tournament Studio experience</p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Data Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                Data Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Default Tour</p>
                  <p className="text-sm text-muted-foreground">Set your preferred tour</p>
                </div>
                <select className="px-3 py-2 rounded-lg bg-elevated border border-border text-sm">
                  <option value="atp">ATP (Men)</option>
                  <option value="wta">WTA (Women)</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Default Surface</p>
                  <p className="text-sm text-muted-foreground">Set your preferred surface</p>
                </div>
                <select className="px-3 py-2 rounded-lg bg-elevated border border-border text-sm">
                  <option value="overall">Overall</option>
                  <option value="hard">Hard Court</option>
                  <option value="clay">Clay Court</option>
                  <option value="grass">Grass Court</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Data Refresh</p>
                  <p className="text-sm text-muted-foreground">Auto-refresh interval</p>
                </div>
                <select className="px-3 py-2 rounded-lg bg-elevated border border-border text-sm">
                  <option value="5">5 minutes</option>
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="0">Manual only</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Appearance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-secondary" />
                Appearance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Theme</p>
                  <p className="text-sm text-muted-foreground">Color scheme</p>
                </div>
                <select className="px-3 py-2 rounded-lg bg-elevated border border-border text-sm">
                  <option value="dark">Dark (Default)</option>
                  <option value="light" disabled>Light (Coming soon)</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Compact Mode</p>
                  <p className="text-sm text-muted-foreground">Reduce spacing</p>
                </div>
                <input type="checkbox" className="h-5 w-5 rounded bg-elevated border-border" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Animations</p>
                  <p className="text-sm text-muted-foreground">Enable motion effects</p>
                </div>
                <input type="checkbox" defaultChecked className="h-5 w-5 rounded bg-elevated border-border" />
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-accent" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Match Alerts</p>
                  <p className="text-sm text-muted-foreground">Notify on match completions</p>
                </div>
                <input type="checkbox" className="h-5 w-5 rounded bg-elevated border-border" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Upset Alerts</p>
                  <p className="text-sm text-muted-foreground">Notify on major upsets</p>
                </div>
                <input type="checkbox" defaultChecked className="h-5 w-5 rounded bg-elevated border-border" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Data Updates</p>
                  <p className="text-sm text-muted-foreground">Notify when Elo data updates</p>
                </div>
                <input type="checkbox" className="h-5 w-5 rounded bg-elevated border-border" />
              </div>
            </CardContent>
          </Card>

          {/* Account */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-danger" />
                Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-elevated">
                <p className="font-medium">Guest User</p>
                <p className="text-sm text-muted-foreground">You are not signed in</p>
              </div>
              <Button variant="outline" className="w-full" disabled>
                Sign In (Coming soon)
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* API Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-primary/10 text-center">
                <div className="h-3 w-3 rounded-full bg-primary mx-auto mb-2" />
                <p className="text-sm font-medium">API</p>
                <p className="text-xs text-muted-foreground">Connected</p>
              </div>
              <div className="p-4 rounded-lg bg-primary/10 text-center">
                <div className="h-3 w-3 rounded-full bg-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Database</p>
                <p className="text-xs text-muted-foreground">Healthy</p>
              </div>
              <div className="p-4 rounded-lg bg-primary/10 text-center">
                <div className="h-3 w-3 rounded-full bg-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Cache</p>
                <p className="text-xs text-muted-foreground">Active</p>
              </div>
              <div className="p-4 rounded-lg bg-primary/10 text-center">
                <div className="h-3 w-3 rounded-full bg-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Data</p>
                <p className="text-xs text-muted-foreground">Up to date</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Scorito Scoring Rules */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Scorito Scoring Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground mb-3">
              Changes are saved locally in this browser.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left p-2 text-muted-foreground">Tier</th>
                    {roundLabels.map((r) => (
                      <th key={r} className="text-center p-2 text-muted-foreground">{r}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(['A', 'B', 'C', 'D'] as const).map((tier) => (
                    <tr key={tier}>
                      <td className="p-2">
                        <TierBadge tier={tier} />
                      </td>
                      {scoring[tier].map((points, idx) => (
                        <td key={idx} className="p-1">
                          <input
                            type="number"
                            value={points}
                            onChange={(e) =>
                              handleScoringChange(tier, idx, Number(e.target.value))
                            }
                            className="w-12 p-1 text-center rounded bg-elevated border border-border text-xs font-mono focus:outline-none focus:ring-1 focus:ring-ring"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}


