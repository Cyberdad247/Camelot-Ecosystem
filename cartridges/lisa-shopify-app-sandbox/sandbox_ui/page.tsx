'use client';

import React, { useState } from 'react';
import { CleanMinimalHero } from '../sections/clean-minimal-hero';
import { InteractiveKeychainCustomizer } from './InteractiveKeychainCustomizer';
import { LiveSchemaProductGrid } from './LiveSchemaProductGrid';
import { MinimalBundleTier } from '../sections/minimal-bundle-tier';
import { DynamicBundleCheckout, CartItem } from '../cart/DynamicBundleCheckout';

export default function LisaStudioSandboxPage() {
  const [cartItems, setCartItems] = useState<CartItem[]>([
    {
      id: 'initial-soul-item',
      title: 'The Signature Soul Weave',
      price: 5.95,
      threadColor: 'Lavender & Plum',
      charms: ['⚾ Softball', '💖 Gilded Heart'],
      customName: 'LISA',
      quantity: 1,
    },
  ]);

  const handleAddToCart = (newItem: CartItem) => {
    setCartItems((prev) => [...prev, newItem]);
    // Smooth scroll to checkout cart area
    const cartEl = document.getElementById('checkout-cart');
    if (cartEl) {
      cartEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleRemoveItem = (id: string) => {
    setCartItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleAddUpsell = (title: string, thread: string) => {
    const upsellItem: CartItem = {
      id: `upsell-${Date.now()}`,
      title,
      price: 5.95,
      threadColor: thread,
      charms: ['✨ Shimmer Star'],
      quantity: 1,
    };
    setCartItems((prev) => [...prev, upsellItem]);
  };

  return (
    <main className="min-h-screen bg-white text-slate-800 selection:bg-purple-100 selection:text-purple-900">
      {/* 1. Clean Minimalist Brand Hero */}
      <CleanMinimalHero />

      {/* 2. Interactive Studio Customizer (Live Design Stage -> Adds directly to Flow Bag) */}
      <section id="customizer-studio" className="py-8 bg-white">
        <InteractiveKeychainCustomizer onAddToCart={handleAddToCart} />
      </section>

      {/* 3. AOV Growth: Minimalist Bundle & Save Tiers */}
      <MinimalBundleTier />

      {/* 4. Level 2 Apprentice Live Sanitized Schema Grid */}
      <LiveSchemaProductGrid />

      {/* 5. Frictionless Unified Flow Checkout Cart */}
      <DynamicBundleCheckout
        items={cartItems}
        onRemoveItem={handleRemoveItem}
        onAddUpsell={handleAddUpsell}
      />
    </main>
  );
}
