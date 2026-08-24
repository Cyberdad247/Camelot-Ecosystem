"use client";

import { GlassOverlay } from '@/components/ui/GlassOverlay';
import { KnightSprites } from '@/components/ui/KnightSprites';
import { TashaVoiceWidget } from '@/components/ui/TashaVoiceWidget';

export default function Home() {
  return (
    <main className="relative w-full h-screen bg-black overflow-hidden selection:bg-yellow-500/30">
      {/* 2D Throne Room Background */}
      <div
        className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url('/assets/throne_bg.webp')" }}
      >
        <div className="absolute inset-0 bg-black/40" /> {/* Darken for UI legibility */}
        <KnightSprites />
      </div>

      {/* Glass UI (Overlay) */}
      <div className="absolute inset-0 z-10 pointer-events-none">
        <GlassOverlay />
      </div>

      {/* Tasha Voice Receptionist */}
      <TashaVoiceWidget />
    </main>
  );
}
