'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Sparkles, ArrowRight, Heart, ShieldCheck } from 'lucide-react';

interface CleanMinimalHeroProps {
  featuredProduct?: {
    id: string;
    title: string;
    price: string;
    imageUrl: string;
    description: string;
  };
}

export const CleanMinimalHero: React.FC<CleanMinimalHeroProps> = ({
  featuredProduct = {
    id: 'soul-featured-01',
    title: 'The Signature Soul Weave',
    price: '$5.95',
    imageUrl: 'https://i.postimg.cc/cvyv100W/Untitled_design_(2).png',
    description: 'Lovingly hand-woven with premium threads and curated accent charms. Crafted one knot at a time.',
  },
}) => {
  return (
    <section className="relative overflow-hidden bg-white py-12 md:py-20 border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-12 lg:gap-16 items-center">
          
          {/* Left Column: Authentic Craft Storytelling & Action */}
          <div className="text-center md:text-left space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-purple-50 border border-purple-100/80 rounded-full text-purple-900 text-xs font-semibold tracking-wide">
              <Sparkles className="w-3.5 h-3.5 text-purple-600" />
              <span>Handmade · One at a Time</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-serif font-bold text-slate-900 leading-[1.15] tracking-tight">
              Custom Keychains <br />
              <span className="italic font-normal text-purple-700 font-serif">
                Lovingly Woven by Hand.
              </span>
            </h1>

            <p className="text-slate-600 text-base md:text-lg leading-relaxed max-w-xl mx-auto md:mx-0">
              Personalized threads, charms, and colors. Choose your favorite style or design your own piece from scratch.
            </p>

            {/* Clean Action Buttons */}
            <div className="flex flex-wrap gap-4 pt-2 justify-center md:justify-start">
              <Link
                href="/customize"
                className="px-7 py-3.5 bg-purple-600 hover:bg-purple-700 text-white text-sm font-bold rounded-full shadow-md shadow-purple-200 transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Build Your Own
              </Link>
              <a
                href="#products"
                className="px-7 py-3.5 bg-white text-slate-800 border border-slate-200 hover:border-purple-300 hover:text-purple-700 text-sm font-bold rounded-full transition-all"
              >
                Shop Collection
              </a>
            </div>

            {/* Minimalist Trust Badges */}
            <div className="flex items-center gap-6 pt-4 justify-center md:justify-start text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-1.5">
                <Heart className="w-4 h-4 text-pink-500" />
                <span>100% Handmade</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Made to Last</span>
              </div>
            </div>
          </div>

          {/* Right Column: Clean Polaroid Style Product Card */}
          <div className="relative mx-auto md:mr-0 max-w-md w-full">
            <div className="bg-stone-50 p-4 pb-6 rounded-2xl border border-stone-200 shadow-xl shadow-slate-100 transition-all hover:shadow-2xl">
              <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-white mb-4 border border-stone-100">
                <Image
                  src={featuredProduct.imageUrl}
                  alt={featuredProduct.title}
                  fill
                  priority
                  className="object-cover transition-transform duration-700 hover:scale-105"
                  sizes="(max-width: 768px) 100vw, 500px"
                />
                <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-bold text-slate-900 shadow-sm">
                  Featured This Week
                </div>
              </div>

              <div className="flex items-center justify-between px-1">
                <div>
                  <h3 className="font-serif font-bold text-slate-900 text-lg">
                    {featuredProduct.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">Custom woven pattern</p>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900 text-base">{featuredProduct.price}</div>
                  <Link
                    href="/customize"
                    className="text-xs font-bold text-purple-700 hover:text-purple-900 flex items-center gap-1 mt-0.5"
                  >
                    <span>Personalize</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default CleanMinimalHero;
