'use client';

import React from 'react';
import { ShoppingBag, Sparkles, ShieldCheck, Heart, Trash2 } from 'lucide-react';

export interface CartItem {
  id: string;
  title: string;
  price: number;
  threadColor: string;
  charms: string[];
  customName?: string;
  quantity: number;
}

interface DynamicBundleCheckoutProps {
  items: CartItem[];
  onRemoveItem: (id: string) => void;
  onAddUpsell: (title: string, thread: string) => void;
}

export const DynamicBundleCheckout: React.FC<DynamicBundleCheckoutProps> = ({
  items,
  onRemoveItem,
  onAddUpsell,
}) => {
  // Pricing Logic & Dynamic Tiering
  const totalCount = items.reduce((acc, item) => acc + item.quantity, 0);
  let subtotal = items.reduce((acc, item) => acc + item.price, 0);
  let discount = 0;
  let tierLabel = 'Single Piece ($5.95)';

  if (totalCount >= 4) {
    subtotal = 19.95;
    discount = totalCount * 5.95 - 19.95;
    tierLabel = 'Squad 4-Pack Tier (Save $3.85 + Free Shipping)';
  } else if (totalCount >= 2) {
    subtotal = 10.95 + (totalCount - 2) * 5.45;
    discount = totalCount * 5.95 - subtotal;
    tierLabel = 'Bestie Pair Tier (Save $1.00)';
  }

  if (items.length === 0) {
    return (
      <section id="checkout-cart" className="max-w-4xl mx-auto p-8 bg-stone-50 rounded-3xl border border-stone-200 text-center my-12">
        <div className="w-16 h-16 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingBag className="w-8 h-8" />
        </div>
        <h3 className="font-serif font-bold text-2xl text-slate-900">Your Craft Bag is Empty</h3>
        <p className="text-slate-500 text-sm mt-1 max-w-sm mx-auto">
          Use the studio customizer above to design your first custom piece.
        </p>
      </section>
    );
  }

  return (
    <section id="checkout-cart" className="max-w-4xl mx-auto p-6 md:p-8 bg-white rounded-3xl border border-stone-200 shadow-xl my-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-stone-100 pb-6 mb-6 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Unified Custom Flow Bag</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-serif font-bold text-slate-900">
            Your Custom Pieces ({totalCount} {totalCount === 1 ? 'item' : 'items'})
          </h2>
        </div>

        {/* Dynamic AOV Upsell Triggers */}
        {totalCount === 1 && (
          <button
            onClick={() => onAddUpsell('Game Day Sporty Weave', 'Navy & Game Day')}
            className="px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-800 text-xs font-bold rounded-xl transition-all flex items-center gap-1 cursor-pointer"
          >
            <span>+ Add 2nd for $5.00 (Save $1)</span>
          </button>
        )}
        {totalCount >= 2 && totalCount < 4 && (
          <button
            onClick={() => onAddUpsell('Squad Matching Weave', 'Luxora Gold & Sand')}
            className="px-4 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-xs font-bold rounded-xl transition-all flex items-center gap-1 cursor-pointer"
          >
            <span>Add 2 More for Squad 4-Pack ($19.95)</span>
          </button>
        )}
      </div>

      {/* Cart Items List */}
      <div className="space-y-4 mb-8">
        {items.map((item, idx) => (
          <div
            key={item.id}
            className="p-4 bg-stone-50 rounded-2xl border border-stone-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-600 text-white font-black text-sm flex items-center justify-center shadow-sm flex-shrink-0">
                #{idx + 1}
              </div>
              <div>
                <h4 className="font-serif font-bold text-slate-900 text-base">{item.title}</h4>
                <div className="text-xs text-slate-500 flex flex-wrap gap-2 mt-0.5">
                  <span className="font-semibold text-purple-700">Thread: {item.threadColor}</span>
                  {item.charms.length > 0 && (
                    <>
                      <span>•</span>
                      <span>Charms: {item.charms.join(', ')}</span>
                    </>
                  )}
                  {item.customName && (
                    <>
                      <span>•</span>
                      <span className="font-mono font-bold text-slate-700">Name: &quot;{item.customName}&quot;</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between sm:justify-end gap-4">
              <div className="text-right">
                <div className="font-bold text-slate-900 text-base">${item.price.toFixed(2)}</div>
                <div className="text-[10px] text-emerald-600 font-bold uppercase">Custom Woven</div>
              </div>
              <button
                onClick={() => onRemoveItem(item.id)}
                className="p-2 text-slate-400 hover:text-rose-600 rounded-lg transition-colors cursor-pointer"
                title="Remove Item"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Tier & Calculation Summary */}
      <div className="p-6 bg-purple-50/50 rounded-2xl border border-purple-100 mb-6 space-y-3">
        <div className="flex justify-between text-xs text-slate-600 font-medium">
          <span>Active Bundle Tier</span>
          <span className="font-bold text-purple-700">{tierLabel}</span>
        </div>
        {discount > 0 && (
          <div className="flex justify-between text-xs text-emerald-700 font-bold">
            <span>Bundle Savings Applied</span>
            <span>-${discount.toFixed(2)}</span>
          </div>
        )}
        <div className="flex justify-between items-baseline pt-2 border-t border-purple-200/60">
          <span className="text-base font-bold text-slate-800">Total</span>
          <span className="text-3xl font-black text-slate-900">${subtotal.toFixed(2)}</span>
        </div>
      </div>

      {/* Checkout Action Button */}
      <button className="w-full py-4 bg-purple-600 hover:bg-purple-700 text-white font-extrabold text-sm uppercase tracking-wider rounded-xl shadow-lg shadow-purple-200 transition-all flex items-center justify-center gap-2 cursor-pointer">
        <ShoppingBag className="w-4 h-4" />
        <span>Proceed to Sovereign Secure Checkout</span>
      </button>

      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-slate-400 font-medium">
        <div className="flex items-center gap-1">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Shopify Protected</span>
        </div>
        <div className="flex items-center gap-1">
          <Heart className="w-4 h-4 text-pink-500" />
          <span>Handcrafted by Lisa</span>
        </div>
      </div>
    </section>
  );
};

export default DynamicBundleCheckout;
