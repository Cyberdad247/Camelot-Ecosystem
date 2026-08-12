'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface HighContrastButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'gold' | 'purple' | 'danger';
  children: React.ReactNode;
}

export function HighContrastButton({
  variant = 'gold',
  children,
  className = '',
  disabled,
  ...props
}: HighContrastButtonProps) {
  const variantStyles = {
    gold: 'bg-[#D4AF37] text-[#050507] border-2 border-[#FFF8D6] hover:bg-[#FFF8D6] shadow-[4px_4px_0px_0px_#9D4EDD]',
    purple: 'bg-[#9D4EDD] text-[#050507] border-2 border-[#9D4EDD] hover:bg-[#050507] hover:text-[#9D4EDD] shadow-[4px_4px_0px_0px_#D4AF37]',
    danger: 'bg-red-600 text-white border-2 border-red-400 hover:bg-red-700 shadow-[4px_4px_0px_0px_#050507]',
  };

  return (
    <motion.button
      whileHover={disabled ? undefined : { scale: 1.04 }}
      whileTap={disabled ? undefined : { scale: 0.96 }}
      disabled={disabled}
      className={`py-3 px-6 font-mono font-black uppercase text-xs tracking-wider transition-all cursor-pointer focus-visible:outline-none ${
        variantStyles[variant]
      } ${disabled ? 'opacity-40 cursor-not-allowed pointer-events-none' : ''} ${className}`}
      {...(props as any)}
    >
      {children}
    </motion.button>
  );
}
