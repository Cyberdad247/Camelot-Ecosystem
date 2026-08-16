import React from 'react';
import { cn } from '@/lib/utils'; // Assuming standard Shadcn utility exists

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, description, footer, actions, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-xl border bg-card text-card-foreground shadow-sm transition-all hover:shadow-md',
          'w-full',
          className,
        )}
        {...props}
      >
        {(title || description || actions) && (
          <div className="flex flex-col space-y-1.5 p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                {title && <h3 className="font-semibold leading-none tracking-tight">{title}</h3>}
                {description && <p className="text-sm text-muted-foreground">{description}</p>}
              </div>
              {actions && <div className="flex shrink-0">{actions}</div>}
            </div>
          </div>
        )}

        <div className="p-6 pt-0">{children}</div>

        {footer && <div className="flex items-center p-6 pt-0">{footer}</div>}
      </div>
    );
  },
);

Card.displayName = 'Card';
