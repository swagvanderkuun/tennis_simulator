'use client';

import { forwardRef } from 'react';
import * as SliderPrimitive from '@radix-ui/react-slider';
import { cn } from '@/lib/utils';

interface SliderProps {
  value: number[];
  onValueChange: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  showValue?: boolean;
  formatValue?: (value: number) => string;
  className?: string;
}

export const Slider = forwardRef<HTMLDivElement, SliderProps>(
  (
    {
      value,
      onValueChange,
      min = 0,
      max = 100,
      step = 1,
      label,
      showValue = true,
      formatValue = (v) => v.toString(),
      className,
    },
    ref
  ) => {
    return (
      <div ref={ref} className={cn('space-y-2', className)}>
        {(label || showValue) && (
          <div className="flex items-center justify-between">
            {label && (
              <label className="text-sm font-medium text-foreground">
                {label}
              </label>
            )}
            {showValue && (
              <span className="text-sm font-mono text-muted-foreground">
                {formatValue(value[0])}
              </span>
            )}
          </div>
        )}
        <SliderPrimitive.Root
          className="relative flex w-full touch-none select-none items-center"
          value={value}
          onValueChange={onValueChange}
          min={min}
          max={max}
          step={step}
        >
          <SliderPrimitive.Track className="slider-track">
            <SliderPrimitive.Range className="slider-range" />
          </SliderPrimitive.Track>
          <SliderPrimitive.Thumb className="slider-thumb focus:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
        </SliderPrimitive.Root>
      </div>
    );
  }
);

Slider.displayName = 'Slider';

// Multi-handle slider for ranges
interface RangeSliderProps extends Omit<SliderProps, 'value' | 'onValueChange'> {
  value: [number, number];
  onValueChange: (value: [number, number]) => void;
}

export const RangeSlider = forwardRef<HTMLDivElement, RangeSliderProps>(
  (
    {
      value,
      onValueChange,
      min = 0,
      max = 100,
      step = 1,
      label,
      showValue = true,
      formatValue = (v) => v.toString(),
      className,
    },
    ref
  ) => {
    return (
      <div ref={ref} className={cn('space-y-2', className)}>
        {(label || showValue) && (
          <div className="flex items-center justify-between">
            {label && (
              <label className="text-sm font-medium text-foreground">
                {label}
              </label>
            )}
            {showValue && (
              <span className="text-sm font-mono text-muted-foreground">
                {formatValue(value[0])} - {formatValue(value[1])}
              </span>
            )}
          </div>
        )}
        <SliderPrimitive.Root
          className="relative flex w-full touch-none select-none items-center"
          value={value}
          onValueChange={(v) => onValueChange(v as [number, number])}
          min={min}
          max={max}
          step={step}
        >
          <SliderPrimitive.Track className="slider-track">
            <SliderPrimitive.Range className="slider-range" />
          </SliderPrimitive.Track>
          <SliderPrimitive.Thumb className="slider-thumb focus:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
          <SliderPrimitive.Thumb className="slider-thumb focus:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
        </SliderPrimitive.Root>
      </div>
    );
  }
);

RangeSlider.displayName = 'RangeSlider';



