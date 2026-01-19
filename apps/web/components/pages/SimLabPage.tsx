'use client';

import { useState, useCallback } from 'react';
import { Play, RotateCcw, Save, Layers } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Button, Slider } from '@/components/ui';
import { ScenarioHeatmap, DistributionChart } from '@/components/charts';
import { cn } from '@/lib/utils';

// Preset configurations
const PRESETS = {
  'Overall (default)': { elo: 0.45, helo: 0.25, celo: 0.20, gelo: 0.10, formScale: 100, formCap: 50 },
  'Hard Court Focus': { elo: 0.25, helo: 0.50, celo: 0.15, gelo: 0.10, formScale: 100, formCap: 50 },
  'Clay Court Focus': { elo: 0.25, helo: 0.15, celo: 0.50, gelo: 0.10, formScale: 100, formCap: 50 },
  'Grass Court Focus': { elo: 0.25, helo: 0.15, celo: 0.10, gelo: 0.50, formScale: 100, formCap: 50 },
  'Elo Only': { elo: 1.0, helo: 0.0, celo: 0.0, gelo: 0.0, formScale: 0, formCap: 0 },
  'Form Heavy': { elo: 0.30, helo: 0.20, celo: 0.15, gelo: 0.10, formScale: 200, formCap: 100 },
};

// Mock heatmap data
const generateHeatmapData = (weights: typeof PRESETS['Overall (default)']) => {
  const surfaces = ['Hard', 'Clay', 'Grass'];
  const forms = ['-50', '-25', '0', '+25', '+50'];
  const data: number[][] = [];
  
  surfaces.forEach((surface, sIdx) => {
    const row: number[] = [];
    forms.forEach((form, fIdx) => {
      const formValue = parseInt(form);
      const surfaceWeight = surface === 'Hard' ? weights.helo : surface === 'Clay' ? weights.celo : weights.gelo;
      const baseProb = 0.5 + surfaceWeight * 0.2 + (formValue / 100) * (weights.formScale / 200);
      row.push(Math.max(0.1, Math.min(0.9, baseProb)));
    });
    data.push(row);
  });
  
  return {
    xLabels: forms,
    yLabels: surfaces,
    data,
  };
};

// Mock sensitivity data
const generateSensitivityData = (weights: typeof PRESETS['Overall (default)']) => {
  return [
    { label: 'Elo ±50', value: Math.abs(weights.elo * 8) },
    { label: 'Hard ±50', value: Math.abs(weights.helo * 6) },
    { label: 'Clay ±50', value: Math.abs(weights.celo * 6) },
    { label: 'Grass ±50', value: Math.abs(weights.gelo * 6) },
    { label: 'Form ±25', value: Math.abs(weights.formScale / 25) },
  ];
};

export function SimLabPage() {
  const [weights, setWeights] = useState(PRESETS['Overall (default)']);
  const [selectedPreset, setSelectedPreset] = useState('Overall (default)');
  const [savedScenarios, setSavedScenarios] = useState<{ name: string; weights: typeof weights }[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);

  const totalWeight = weights.elo + weights.helo + weights.celo + weights.gelo;
  const isValidWeights = Math.abs(totalWeight - 1.0) < 0.01;

  const handlePresetChange = (presetName: string) => {
    setSelectedPreset(presetName);
    setWeights(PRESETS[presetName as keyof typeof PRESETS]);
  };

  const handleWeightChange = useCallback((key: keyof typeof weights, value: number) => {
    setWeights((prev) => ({ ...prev, [key]: value }));
    setSelectedPreset('Custom');
  }, []);

  const handleReset = () => {
    handlePresetChange('Overall (default)');
  };

  const handleSaveScenario = () => {
    const name = `Scenario ${savedScenarios.length + 1}`;
    setSavedScenarios((prev) => [...prev, { name, weights: { ...weights } }]);
  };

  const handleRunSimulation = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
    }, 1500);
  };

  const heatmapData = generateHeatmapData(weights);
  const sensitivityData = generateSensitivityData(weights);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Simulation Lab</h1>
          <p className="text-muted-foreground">Configure weights and explore scenarios</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
          <Button variant="outline" onClick={handleSaveScenario} className="gap-2">
            <Save className="h-4 w-4" />
            Save Scenario
          </Button>
          <Button
            onClick={handleRunSimulation}
            disabled={!isValidWeights || isSimulating}
            className="gap-2"
          >
            <Play className="h-4 w-4" />
            {isSimulating ? 'Running...' : 'Run Simulation'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Weights Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary" />
              Weight Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Preset selector */}
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">Preset</label>
              <select
                value={selectedPreset}
                onChange={(e) => handlePresetChange(e.target.value)}
                className="w-full p-2 rounded-lg bg-elevated border border-border text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {Object.keys(PRESETS).map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
                <option value="Custom">Custom</option>
              </select>
            </div>

            {/* Weight sliders */}
            <Slider
              label="Overall Elo"
              value={[weights.elo]}
              onValueChange={(v) => handleWeightChange('elo', v[0])}
              min={0}
              max={1}
              step={0.05}
              formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <Slider
              label="Hard Court Elo"
              value={[weights.helo]}
              onValueChange={(v) => handleWeightChange('helo', v[0])}
              min={0}
              max={1}
              step={0.05}
              formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <Slider
              label="Clay Court Elo"
              value={[weights.celo]}
              onValueChange={(v) => handleWeightChange('celo', v[0])}
              min={0}
              max={1}
              step={0.05}
              formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <Slider
              label="Grass Court Elo"
              value={[weights.gelo]}
              onValueChange={(v) => handleWeightChange('gelo', v[0])}
              min={0}
              max={1}
              step={0.05}
              formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            />

            {/* Total weight indicator */}
            <div className={cn(
              'p-3 rounded-lg text-center',
              isValidWeights ? 'bg-primary/10 text-primary' : 'bg-danger/10 text-danger'
            )}>
              <p className="text-sm font-medium">
                Total: {(totalWeight * 100).toFixed(0)}%
              </p>
              {!isValidWeights && (
                <p className="text-xs mt-1">Must equal 100%</p>
              )}
            </div>

            {/* Form configuration */}
            <div className="pt-4 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-4">Form Adjustment</p>
              <Slider
                label="Form Scale"
                value={[weights.formScale]}
                onValueChange={(v) => handleWeightChange('formScale', v[0])}
                min={0}
                max={400}
                step={10}
                formatValue={(v) => `${v}`}
              />
              <Slider
                label="Form Cap"
                value={[weights.formCap]}
                onValueChange={(v) => handleWeightChange('formCap', v[0])}
                min={0}
                max={200}
                step={5}
                formatValue={(v) => `${v}`}
              />
            </div>
          </CardContent>
        </Card>

        {/* Scenario Heatmap */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Scenario Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Win probability by surface and form differential
            </p>
            <ScenarioHeatmap
              data={heatmapData}
              title="Surface × Form Impact"
              height={350}
            />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Sensitivity Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Sensitivity Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Win probability delta when each factor changes by ±50 Elo points
            </p>
            <DistributionChart
              data={sensitivityData}
              height={250}
              color="#F9C74F"
            />
          </CardContent>
        </Card>

        {/* Saved Scenarios */}
        <Card>
          <CardHeader>
            <CardTitle>Saved Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            {savedScenarios.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No scenarios saved yet. Click "Save Scenario" to create one.
              </p>
            ) : (
              <div className="space-y-2">
                {savedScenarios.map((scenario, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-elevated hover:bg-elevated/80 cursor-pointer transition-colors"
                    onClick={() => {
                      setWeights(scenario.weights);
                      setSelectedPreset('Custom');
                    }}
                  >
                    <span className="font-medium">{scenario.name}</span>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>E:{(scenario.weights.elo * 100).toFixed(0)}%</span>
                      <span>H:{(scenario.weights.helo * 100).toFixed(0)}%</span>
                      <span>C:{(scenario.weights.celo * 100).toFixed(0)}%</span>
                      <span>G:{(scenario.weights.gelo * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Impact Sliders Demo */}
      <Card>
        <CardHeader>
          <CardTitle>Real-Time Impact Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            See how win probability changes as you adjust weights above
          </p>
          <div className="grid grid-cols-4 gap-4">
            {['Sinner vs Alcaraz', 'Djokovic vs Medvedev', 'Zverev vs Rublev', 'Fritz vs Hurkacz'].map((matchup, idx) => {
              const baseProb = [0.52, 0.58, 0.55, 0.48][idx];
              const adjustedProb = baseProb + (weights.elo - 0.45) * 0.1 + (weights.formScale - 100) / 1000;
              return (
                <div key={matchup} className="p-4 rounded-lg bg-elevated text-center">
                  <p className="text-sm font-medium text-foreground mb-2">{matchup}</p>
                  <p className="text-2xl font-mono font-bold text-primary">
                    {(Math.max(0.1, Math.min(0.9, adjustedProb)) * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Δ {((adjustedProb - baseProb) * 100).toFixed(1)}%
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


