'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, Check, Heart } from 'lucide-react';

export const MinimalBundleTier: React.FC = () => {
  return (
    <section className="py-16 bg-stone-50 border-t border-b border-stone-200/70">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-xl mx-auto mb-12">
          <p className="text-xs uppercase tracking-[0.25em] font-bold text-purple-600 mb-2">
            Bundle & Save
          </p>
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-slate-900">
            Handcrafted Sets for Every Story
          </h2>
          <p className="text-slate-500 text-sm mt-3">
            Mix and match your favorite weaves and charms. Perfect for gifts, best friends, and teams.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto items-stretch">
          
          {/* Tier 1: Single Piece */}
          <div className="bg-white p-7 rounded-2xl border border-stone-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Single Piece</div>
              <h3 className="font-serif font-bold text-xl text-slate-900 mt-1">Single Custom</h3>
              <div className="text-3xl font-extrabold text-slate-900 mt-4">$5.95</div>
              <p className="text-xs text-slate-500 mt-1">1 custom hand-woven keychain</p>
              
              <ul className="mt-6 space-y-3 text-xs text-slate-600">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>Choose custom thread colors</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>1 standard charm attachment</span>
                </li>
              </ul>
            </div>
            <Link
              href="/customize"
              className="mt-8 block w-full py-3 bg-stone-100 hover:bg-stone-200 text-slate-800 text-center font-bold text-xs uppercase tracking-wider rounded-xl transition-all"
            >
              Build Single
            </Link>
          </div>

          {/* Tier 2: Best Friends / Pair (Popular) */}
          <div className="bg-white p-7 rounded-2xl border-2 border-purple-500 shadow-xl relative flex flex-col justify-between transform md:-translate-y-2">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full shadow-sm">
              Most Popular
            </div>
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-purple-600">Bestie Pack</div>
              <h3 className="font-serif font-bold text-xl text-slate-900 mt-1">Matching Pair Set</h3>
              <div className="text-3xl font-extrabold text-purple-700 mt-4">$10.95</div>
              <p className="text-xs text-slate-500 mt-1">2 matching or custom keychains</p>
              
              <ul className="mt-6 space-y-3 text-xs text-slate-600">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>2 custom weaves of your choice</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>Matching charms or letters</span>
                </li>
                <li className="flex items-center gap-2">
                  <Heart className="w-4 h-4 text-pink-500" />
                  <span className="font-semibold text-purple-900">Save $1.00 instantly</span>
                </li>
              </ul>
            </div>
            <Link
              href="/customize"
              className="mt-8 block w-full py-3.5 bg-purple-600 hover:bg-purple-700 text-white text-center font-bold text-xs uppercase tracking-wider rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Build Pair Set
            </Link>
          </div>

          {/* Tier 3: Team / Family Pack */}
          <div className="bg-white p-7 rounded-2xl border border-stone-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Team & Family</div>
              <h3 className="font-serif font-bold text-xl text-slate-900 mt-1">Squad 4-Pack</h3>
              <div className="text-3xl font-extrabold text-slate-900 mt-4">$19.95</div>
              <p className="text-xs text-slate-500 mt-1">4 keychains with school/team colors</p>
              
              <ul className="mt-6 space-y-3 text-xs text-slate-600">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>4 custom team/sports keychains</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span>Free bonus charm on every piece</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-purple-600" />
                  <span className="font-semibold text-emerald-700">Save $3.85 + Free Shipping</span>
                </li>
              </ul>
            </div>
            <Link
              href="/customize"
              className="mt-8 block w-full py-3 bg-stone-100 hover:bg-stone-200 text-slate-800 text-center font-bold text-xs uppercase tracking-wider rounded-xl transition-all"
            >
              Build Squad Pack
            </Link>
          </div>

        </div>
      </div>
    </section>
  );
};

export default MinimalBundleTier;
