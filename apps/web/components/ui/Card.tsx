import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('rounded-xl bg-surface border border-border', className)}
      {...props}
    />
  )
);
Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 p-6', className)}
      {...props}
    />
  )
);
CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('font-display text-lg font-semibold leading-none tracking-tight', className)}
      {...props}
    />
  )
);
CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn('text-sm text-muted-foreground', className)}
      {...props}
    />
  )
);
CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
);
CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex items-center p-6 pt-0', className)}
      {...props}
    />
  )
);
CardFooter.displayName = 'CardFooter';

// Glass card variant
export const GlassCard = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('glass-card p-6', className)}
      {...props}
    />
  )
);
GlassCard.displayName = 'GlassCard';

// Metric card variant
export const MetricCard = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement> & {
    label: string;
    value: string | number;
    delta?: string;
    deltaType?: 'positive' | 'negative' | 'neutral';
  }
>(({ className, label, value, delta, deltaType = 'neutral', ...props }, ref) => (
  <div
    ref={ref}
    className={cn('metric-card', className)}
    {...props}
  >
    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
      {label}
    </p>
    <p className="text-2xl font-mono font-bold text-foreground">{value}</p>
    {delta && (
      <p
        className={cn(
          'text-sm font-mono mt-1',
          deltaType === 'positive' && 'text-primary',
          deltaType === 'negative' && 'text-danger',
          deltaType === 'neutral' && 'text-muted-foreground'
        )}
      >
        {delta}
      </p>
    )}
  </div>
));
MetricCard.displayName = 'MetricCard';


