'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';
import { EloHistory } from '@/lib/api';

interface EloTrendChartProps {
  data: EloHistory[];
  showConfidenceBands?: boolean;
  height?: number;
  selectedMetrics?: ('elo' | 'helo' | 'celo' | 'gelo')[];
}

const COLORS = {
  elo: '#38E07C',     // primary green
  helo: '#4CC9F0',    // secondary cyan
  celo: '#F9C74F',    // accent gold
  gelo: '#90BE6D',    // grass green
  confidence: 'rgba(56, 224, 124, 0.1)',
};

export function EloTrendChart({
  data,
  showConfidenceBands = true,
  height = 300,
  selectedMetrics = ['elo'],
}: EloTrendChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    const dates = data.map((d) => d.date);
    
    const series: EChartsOption['series'] = [];

    // Add confidence band if enabled
    if (showConfidenceBands && data.length > 0) {
      const eloValues = data.map((d) => d.elo);
      const mean = eloValues.reduce((a, b) => a + b, 0) / eloValues.length;
      const stdDev = Math.sqrt(
        eloValues.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / eloValues.length
      );

      series.push({
        name: 'Confidence Band',
        type: 'line',
        data: data.map((d) => d.elo + stdDev * 1.5),
        lineStyle: { opacity: 0 },
        areaStyle: { color: COLORS.confidence },
        symbol: 'none',
        stack: 'confidence',
      });
      series.push({
        name: 'Confidence Band Lower',
        type: 'line',
        data: data.map((d) => d.elo - stdDev * 1.5),
        lineStyle: { opacity: 0 },
        areaStyle: { color: COLORS.confidence },
        symbol: 'none',
        stack: 'confidence',
      });
    }

    // Add main metric lines
    if (selectedMetrics.includes('elo')) {
      series.push({
        name: 'Overall Elo',
        type: 'line',
        data: data.map((d) => d.elo),
        smooth: true,
        lineStyle: { color: COLORS.elo, width: 2 },
        itemStyle: { color: COLORS.elo },
        symbol: 'circle',
        symbolSize: 4,
      });
    }

    if (selectedMetrics.includes('helo')) {
      series.push({
        name: 'Hard Court Elo',
        type: 'line',
        data: data.map((d) => d.helo),
        smooth: true,
        lineStyle: { color: COLORS.helo, width: 2 },
        itemStyle: { color: COLORS.helo },
        symbol: 'circle',
        symbolSize: 4,
      });
    }

    if (selectedMetrics.includes('celo')) {
      series.push({
        name: 'Clay Court Elo',
        type: 'line',
        data: data.map((d) => d.celo),
        smooth: true,
        lineStyle: { color: COLORS.celo, width: 2 },
        itemStyle: { color: COLORS.celo },
        symbol: 'circle',
        symbolSize: 4,
      });
    }

    if (selectedMetrics.includes('gelo')) {
      series.push({
        name: 'Grass Court Elo',
        type: 'line',
        data: data.map((d) => d.gelo),
        smooth: true,
        lineStyle: { color: COLORS.gelo, width: 2 },
        itemStyle: { color: COLORS.gelo },
        symbol: 'circle',
        symbolSize: 4,
      });
    }

    // Calculate dynamic y-axis bounds from all visible data
    const allValues: number[] = [];
    selectedMetrics.forEach((m) => {
      data.forEach((d) => {
        const val = d[m];
        if (val !== undefined && val !== null) {
          allValues.push(val);
        }
      });
    });
    
    let yMin = 0;
    let yMax = 5000;
    if (allValues.length > 0) {
      const dataMin = Math.min(...allValues);
      const dataMax = Math.max(...allValues);
      const range = dataMax - dataMin;
      const padding = Math.max(range * 0.15, 25); // At least 25 points padding
      yMin = Math.floor((dataMin - padding) / 50) * 50; // Round to nearest 50
      yMax = Math.ceil((dataMax + padding) / 50) * 50;
    }

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(17, 25, 35, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#E6EDF3' },
        axisPointer: {
          type: 'cross',
          crossStyle: { color: '#999' },
        },
      },
      legend: {
        data: selectedMetrics.map((m) => ({
          elo: 'Overall Elo',
          helo: 'Hard Court Elo',
          celo: 'Clay Court Elo',
          gelo: 'Grass Court Elo',
        }[m])),
        textStyle: { color: '#9FB0C0' },
        top: 10,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 50,
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0' },
      },
      yAxis: {
        type: 'value',
        min: yMin,
        max: yMax,
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0' },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } },
      },
      series,
    };

    chartInstance.current.setOption(option);

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, showConfidenceBands, selectedMetrics]);

  return <div ref={chartRef} style={{ width: '100%', height }} />;
}

