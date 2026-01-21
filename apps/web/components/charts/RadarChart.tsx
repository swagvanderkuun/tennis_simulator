'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

interface RadarChartProps {
  data: {
    name: string;
    values: number[];
    color?: string;
  }[];
  indicators: { name: string; max: number }[];
  height?: number;
}

export function RadarChart({ data, indicators, height = 300 }: RadarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      tooltip: {
        backgroundColor: 'rgba(17, 25, 35, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#E6EDF3' },
      },
      legend: {
        data: data.map((d) => d.name),
        textStyle: { color: '#9FB0C0' },
        bottom: 10,
      },
      radar: {
        indicator: indicators,
        shape: 'polygon',
        splitNumber: 5,
        axisName: {
          color: '#9FB0C0',
          fontSize: 11,
        },
        splitLine: {
          lineStyle: { color: 'rgba(255, 255, 255, 0.1)' },
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(56, 224, 124, 0.02)', 'rgba(56, 224, 124, 0.04)'],
          },
        },
        axisLine: {
          lineStyle: { color: 'rgba(255, 255, 255, 0.1)' },
        },
      },
      series: [
        {
          type: 'radar',
          data: data.map((d, i) => ({
            name: d.name,
            value: d.values,
            lineStyle: {
              color: d.color || ['#38E07C', '#4CC9F0', '#F9C74F'][i % 3],
              width: 2,
            },
            areaStyle: {
              color: d.color
                ? `${d.color}20`
                : ['rgba(56, 224, 124, 0.2)', 'rgba(76, 201, 240, 0.2)', 'rgba(249, 199, 79, 0.2)'][i % 3],
            },
            itemStyle: {
              color: d.color || ['#38E07C', '#4CC9F0', '#F9C74F'][i % 3],
            },
          })),
        },
      ],
    };

    chartInstance.current.setOption(option);

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, indicators]);

  return <div ref={chartRef} style={{ width: '100%', height }} />;
}



