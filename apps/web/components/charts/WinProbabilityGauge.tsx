'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

interface WinProbabilityGaugeProps {
  player1Name: string;
  player2Name: string;
  player1Prob: number;
  height?: number;
}

export function WinProbabilityGauge({
  player1Name,
  player2Name,
  player1Prob,
  height = 200,
}: WinProbabilityGaugeProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, 'dark');
    }

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      series: [
        {
          type: 'gauge',
          startAngle: 180,
          endAngle: 0,
          center: ['50%', '75%'],
          radius: '90%',
          min: 0,
          max: 100,
          splitNumber: 10,
          axisLine: {
            lineStyle: {
              width: 20,
              color: [
                [player1Prob, '#38E07C'],
                [1, '#4CC9F0'],
              ],
            },
          },
          pointer: {
            icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
            length: '60%',
            width: 8,
            offsetCenter: [0, '-10%'],
            itemStyle: {
              color: '#E6EDF3',
            },
          },
          axisTick: {
            length: 8,
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)',
              width: 1,
            },
          },
          splitLine: {
            length: 15,
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.3)',
              width: 2,
            },
          },
          axisLabel: {
            show: false,
          },
          title: {
            show: false,
          },
          detail: {
            fontSize: 24,
            offsetCenter: [0, '-20%'],
            valueAnimation: true,
            formatter: function (value: number) {
              return Math.round(value) + '%';
            },
            color: '#E6EDF3',
          },
          data: [{ value: Math.round(player1Prob * 100) }],
        },
      ],
    };

    chartInstance.current.setOption(option);

    const handleResize = () => chartInstance.current?.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [player1Prob]);

  return (
    <div className="relative">
      <div ref={chartRef} style={{ width: '100%', height }} />
      <div className="absolute bottom-4 left-0 right-0 flex justify-between px-8">
        <div className="text-center">
          <p className="text-sm font-medium text-primary">{player1Name}</p>
          <p className="text-xs text-muted-foreground">
            {(player1Prob * 100).toFixed(1)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-secondary">{player2Name}</p>
          <p className="text-xs text-muted-foreground">
            {((1 - player1Prob) * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}



