'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

interface HeatmapData {
  xLabels: string[];
  yLabels: string[];
  data: number[][]; // [x, y, value]
}

interface ScenarioHeatmapProps {
  data: HeatmapData;
  title?: string;
  height?: number;
}

export function ScenarioHeatmap({ data, title, height = 400 }: ScenarioHeatmapProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    // Transform data for ECharts heatmap
    const heatmapData: [number, number, number][] = [];
    data.data.forEach((row, yIdx) => {
      row.forEach((value, xIdx) => {
        heatmapData.push([xIdx, yIdx, value]);
      });
    });

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
        position: 'top',
        backgroundColor: 'rgba(17, 25, 35, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: '#E6EDF3' },
        formatter: function (params: any) {
          const xLabel = data.xLabels[params.data[0]];
          const yLabel = data.yLabels[params.data[1]];
          const value = params.data[2];
          return `${xLabel} × ${yLabel}<br/>Win Prob: <strong>${(value * 100).toFixed(1)}%</strong>`;
        },
      },
      grid: {
        top: title ? 60 : 30,
        left: 80,
        right: 40,
        bottom: 60,
      },
      xAxis: {
        type: 'category',
        data: data.xLabels,
        splitArea: { show: true },
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0', rotate: 45 },
      },
      yAxis: {
        type: 'category',
        data: data.yLabels,
        splitArea: { show: true },
        axisLine: { lineStyle: { color: '#2A3544' } },
        axisLabel: { color: '#9FB0C0' },
      },
      visualMap: {
        min: 0,
        max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: ['#F72585', '#4CC9F0', '#38E07C'],
        },
        textStyle: { color: '#9FB0C0' },
      },
      series: [
        {
          name: 'Win Probability',
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            formatter: function (params: any) {
              return (params.data[2] * 100).toFixed(0) + '%';
            },
            color: '#E6EDF3',
            fontSize: 10,
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
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
  }, [data, title]);

  return <div ref={chartRef} style={{ width: '100%', height }} />;
}


