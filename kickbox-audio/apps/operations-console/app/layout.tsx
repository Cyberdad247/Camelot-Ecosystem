import React from 'react';
import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ThemeToggle } from '../src/components/ThemeToggle';

export const metadata: Metadata = {
  title: 'Camelot-OS | Sovereign Executive Intelligence HUD',
  description: 'Invisioned Marketing / KBA Executive Operations Console & Bare-Metal Edge Interphase',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'KBA Sovereign Interphase',
  },
};

export const viewport: Viewport = {
  themeColor: '#D4AF37',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-[#050507] text-slate-100 antialiased selection:bg-[#9D4EDD]/40 selection:text-white">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,700;0,800;1,400;1,700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="flex h-full flex-col font-sans overflow-x-hidden border-t-4 border-[#D4AF37] bg-[#050507] relative">
        
        {/* Dynamic Radial Mesh & Noise Layer */}
        <div className="fixed inset-0 pointer-events-none z-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(212,175,55,0.12),rgba(5,5,7,1))] bg-mesh-grid" />
        <div className="fixed inset-0 pointer-events-none z-0 opacity-15 bg-[radial-gradient(#D4AF37_1px,transparent_1px)] [background-size:24px_24px]" />

        {/* Global Executive Top Navigation Bar */}
        <header className="sticky top-0 z-50 flex h-14 items-center justify-between border-b-2 border-[#D4AF37]/30 bg-[#050507]/90 px-6 backdrop-blur-xl font-mono">
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 bg-[#D4AF37] shadow-[0_0_10px_#D4AF37] animate-pulse" />
            <span className="font-bold tracking-widest text-[#D4AF37] text-xs md:text-sm uppercase">
              CAMELOT-OS // KBA SOVEREIGN INTERPHASE
            </span>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-400">
            <div className="hidden md:flex items-center gap-2">
              <span className="text-slate-500">TAILSCALE EDGE:</span>
              <span className="px-2 py-0.5 bg-slate-900 border border-[#D4AF37]/40 text-[#D4AF37] font-bold">
                100.71.218.75:4433
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">BIFROST:</span>
              <span className="text-emerald-400 font-bold">mTLS ACTIVE</span>
            </div>
            <ThemeToggle />
          </div>
        </header>

        {/* Main Content Viewport */}
        <main className="flex-1 relative z-10 flex flex-col p-4 md:p-8">
          <div className="mx-auto w-full max-w-7xl flex-1">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
