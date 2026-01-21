'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

interface DistributionChartProps {
  data: { label: string; value: number }[];
  title?: string;
  height?: number;
  color?: string;
}

export function DistributionChart({
  data,
  title,
  height = 250,
  color = '#38E07C',
}: DistributionChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      title: title
        ? {
            text: title,
            textStyle: { color: '#E6EDF3', fontSize: 14 },
            left: 'center',
          }
        : undefined,
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(17, 25, 35, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#E6EDF3' },
        axisPointer: {
          type: 'shadow',
        },
      },
      grid: {
        top: title ? 50 : 20,
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: data.map((d) => d.label),
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0' },
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0' },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } },
      },
      series: [
        {
          type: 'bar',
          data: data.map((d) => d.value),
          barWidth: '60%',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color },
              { offset: 1, color: `${color}40` },
            ]),
            borderRadius: [4, 4, 0, 0],
          },
        },
      ],
    };

    chartInstance.current.setOption(option);

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, title, color]);

  return <div ref={chartRef} style={{ width: '100%', height }} />;
}



