// SPDX-License-Identifier: MIT

'use client';

import React, { useEffect, useState } from 'react';

export function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const savedTheme = localStorage.getItem('kba_theme') as 'dark' | 'light' | null;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
      if (savedTheme === 'light') {
        document.documentElement.classList.add('light-mode');
      } else {
        document.documentElement.classList.remove('light-mode');
      }
    }
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('kba_theme', nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);

    if (nextTheme === 'light') {
      document.documentElement.classList.add('light-mode');
    } else {
      document.documentElement.classList.remove('light-mode');
    }
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`px-3 py-1.5 font-mono font-black text-xs uppercase tracking-wider border-2 cursor-pointer transition-all hover:scale-[1.05] active:scale-[0.95] ${
        theme === 'dark'
          ? 'bg-[#FFF8D6] text-slate-950 border-[#D4AF37] shadow-[3px_3px_0px_0px_#9D4EDD]'
          : 'bg-[#0B0B0E] text-[#FFF8D6] border-[#0B0B0E] shadow-[3px_3px_0px_0px_#D4AF37]'
      }`}
    >
      {theme === 'dark' ? '☀️ WHITE SCREEN MODE' : '🌙 DARK OBSIDIAN MODE'}
    </button>
  );
}
