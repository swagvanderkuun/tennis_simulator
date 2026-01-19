import { HTMLAttributes, forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary/20 text-primary',
        secondary: 'bg-secondary/20 text-secondary',
        accent: 'bg-accent/20 text-accent',
        danger: 'bg-danger/20 text-danger',
        muted: 'bg-muted/20 text-muted-foreground',
        outline: 'border border-border text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(badgeVariants({ variant }), className)}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

// Tier badge component
export const TierBadge = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement> & { tier: string }
>(({ className, tier, ...props }, ref) => {
  const tierClass = {
    A: 'tier-a',
    B: 'tier-b',
    C: 'tier-c',
    D: 'tier-d',
  }[tier?.toUpperCase()] || 'tier-d';

  return (
    <div
      ref={ref}
      className={cn('tier-badge', tierClass, className)}
      {...props}
    >
      {tier?.toUpperCase()}
    </div>
  );
});

TierBadge.displayName = 'TierBadge';


