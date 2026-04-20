---
to: src/components/<%= name %>/<%= name %>.tsx
---
import { cva, type VariantProps } from 'class-variance-authority';
// import { cn } from '@/lib/utils'; // Start with standard clsx/tailwind-merge if utils not present

// [LAW I: SOVEREIGNTY] - Styles are decoupled via CVA
const <%= h.changeCase.camel(name) %>Variants = cva(
  "flex items-center justify-center rounded-md transition-all",
  {
    variants: {
      intent: {
        primary: "bg-yellow-500 text-black hover:bg-yellow-400", // 'camelot-gold' approx
        ghost: "bg-transparent hover:bg-zinc-800",
      },
    },
    defaultVariants: { intent: "primary" },
  }
);

interface <%= name %>Props extends VariantProps<typeof <%= h.changeCase.camel(name) %>Variants> {
  children: React.ReactNode;
  className?: string;
}

export const <%= name %> = ({ children, intent, className }: <%= name %>Props) => {
  return (
    <div className={<%= h.changeCase.camel(name) %>Variants({ intent, className })}>
      {children}
    </div>
  );
};
