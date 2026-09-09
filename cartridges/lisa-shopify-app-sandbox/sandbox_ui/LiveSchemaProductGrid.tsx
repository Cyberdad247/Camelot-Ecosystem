'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Sparkles, ShoppingBag, Tag, ArrowRight, Check } from 'lucide-react';

export interface SyncedProduct {
  raw_id: string;
  raw_title: string;
  clean_title: string;
  category: string;
  badge: string;
  image: string;
  price: string;
  price_numeric: number;
  availability: string;
}

export const LiveSchemaProductGrid: React.FC = () => {
  const [products, setProducts] = useState<SyncedProduct[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Staged from dynamic_store_sync output (46 synced products)
    const mockSyncedCatalog: SyncedProduct[] = [
      {
        raw_id: 'soul-1000011817',
        raw_title: 'Soul- 1000011817',
        clean_title: 'The Signature Soul Weave',
        category: 'Soul',
        badge: 'Most Loved',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/rn-image_picker_lib_temp_77dff20b-1cda-4864-8bae-6abaa4d3e64f.jpg?v=1787754263',
        price: '$5.95',
        price_numeric: 5.95,
        availability: 'InStock',
      },
      {
        raw_id: 'sporty-1000012138',
        raw_title: 'Sporty  1000012138',
        clean_title: 'Game Day Sporty Weave',
        category: 'Sporty',
        badge: 'Sports Edition',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/rn-image_picker_lib_temp_8d7bb282-52bd-47f9-9aaf-05a490d5df6e.jpg?v=1776125054',
        price: '$3.45',
        price_numeric: 3.45,
        availability: 'InStock',
      },
      {
        raw_id: 'breast-cancer-1474164466462',
        raw_title: 'Breast cancer - price per keychain 1474164466462',
        clean_title: 'Hope & Strength Ribbon Keychain',
        category: 'Charity',
        badge: 'Charity Edition',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/rn-image_picker_lib_temp_f1557580-452e-4323-ba2b-609f0cfa1983.jpg?v=1787151673',
        price: '$5.95',
        price_numeric: 5.95,
        availability: 'InStock',
      },
      {
        raw_id: 'premium-1529285017581-529',
        raw_title: 'Premium - 1529285017581-529',
        clean_title: 'Deluxe Charm & Beaded Keychain',
        category: 'Premium',
        badge: 'Deluxe',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/1529285017581-529.jpg?v=1767069028',
        price: '$9.95',
        price_numeric: 9.95,
        availability: 'InStock',
      },
      {
        raw_id: 'earrings-dangle-style',
        raw_title: 'Dangle in style price per pair.',
        clean_title: 'Hand-Woven Dangle Earrings',
        category: 'Earrings',
        badge: 'Handcrafted',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/rn-image_picker_lib_temp_e74907e5-c55e-4d2e-8530-f0b36860bfc4.jpg?v=1770870122',
        price: '$5.95',
        price_numeric: 5.95,
        availability: 'InStock',
      },
      {
        raw_id: 'matching-pair-set',
        raw_title: 'Matching pair set- price per set.',
        clean_title: 'Bestie Matching Pair Set',
        category: 'Signature',
        badge: 'Pair Bundle',
        image: 'https://cdn.shopify.com/s/files/1/0952/7151/8578/files/rn-image_picker_lib_temp_b15e551f-12e0-439e-acba-e488448f437e.jpg?v=1771451778',
        price: '$8.95',
        price_numeric: 8.95,
        availability: 'InStock',
      },
    ];

    setProducts(mockSyncedCatalog);
    setLoading(false);
  }, []);

  const categories = ['All', 'Soul', 'Sporty', 'Premium', 'Earrings', 'Charity'];

  const filteredProducts =
    selectedCategory === 'All'
      ? products
      : products.filter((p) => p.category.toLowerCase() === selectedCategory.toLowerCase());

  return (
    <section id="collection-grid" className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6 border-b border-stone-100 pb-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Level 2 Apprentice Live Preview</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-serif font-bold text-slate-900">
              Sanitized Collection
            </h2>
            <p className="text-slate-500 text-sm mt-2 max-w-lg">
              Every item has been cleaned, categorized, and formatted for maximum conversion and SEO clarity.
            </p>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all cursor-pointer ${selectedCategory === cat ? 'bg-purple-600 text-white shadow-md' : 'bg-stone-100 text-slate-600 hover:bg-stone-200'}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Product Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredProducts.map((product) => (
            <article
              key={product.raw_id}
              className="group bg-white rounded-2xl border border-stone-200/80 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                {/* Image Container */}
                <div className="relative aspect-square w-full bg-stone-50 overflow-hidden border-b border-stone-100">
                  <Image
                    src={product.image}
                    alt={product.clean_title}
                    fill
                    className="object-cover transition-transform duration-700 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  />
                  <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider text-purple-900 shadow-sm border border-stone-100">
                    {product.badge}
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">
                    {product.category} Collection
                  </div>
                  <h3 className="font-serif font-bold text-slate-900 text-lg group-hover:text-purple-700 transition-colors">
                    {product.clean_title}
                  </h3>
                  <div className="text-xs text-slate-400 font-mono mt-1">
                    Raw: {product.raw_title.slice(0, 24)}...
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="p-5 pt-0 flex items-center justify-between border-t border-stone-50 mt-4">
                <div className="text-xl font-extrabold text-slate-900">{product.price}</div>
                <Link
                  href="/customize"
                  className="px-4 py-2 bg-purple-50 hover:bg-purple-600 text-purple-700 hover:text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Customize</span>
                </Link>
              </div>
            </article>
          ))}
        </div>

      </div>
    </section>
  );
};

export default LiveSchemaProductGrid;
