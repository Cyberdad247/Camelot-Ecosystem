'use client';

import React, { useState } from 'react';
import { Sparkles, Check, ShoppingBag, Eye, Heart } from 'lucide-react';
import type { CartItem } from '../cart/DynamicBundleCheckout';

interface ThreadOption {
  id: string;
  name: string;
  colorClass: string;
  hex: string;
}

interface CharmOption {
  id: string;
  name: string;
  category: 'Sports' | 'Hearts' | 'Nature';
  icon: string;
}

const THREAD_OPTIONS: ThreadOption[] = [
  { id: 'purple_lavender', name: 'Lavender & Plum', colorClass: 'from-purple-500 to-indigo-600', hex: '#8B5CF6' },
  { id: 'gold_amber', name: 'Luxora Gold & Sand', colorClass: 'from-amber-400 to-yellow-600', hex: '#D4AF37' },
  { id: 'rose_petal', name: 'Rose & Blossom', colorClass: 'from-pink-400 to-rose-500', hex: '#FB7185' },
  { id: 'navy_sky', name: 'Navy & Game Day', colorClass: 'from-blue-600 to-sky-400', hex: '#2563EB' },
  { id: 'forest_mint', name: 'Sage & Emerald', colorClass: 'from-emerald-500 to-teal-600', hex: '#10B981' },
];

const CHARM_OPTIONS: CharmOption[] = [
  { id: 'softball', name: 'Softball / Baseball', category: 'Sports', icon: '⚾' },
  { id: 'basketball', name: 'Basketball', category: 'Sports', icon: '🏀' },
  { id: 'football', name: 'Football', category: 'Sports', icon: '🏈' },
  { id: 'gold_heart', name: 'Gilded Heart', category: 'Hearts', icon: '💖' },
  { id: 'sparkle_star', name: 'Shimmer Star', category: 'Nature', icon: '✨' },
  { id: 'butterfly', name: 'Pastel Butterfly', category: 'Nature', icon: '🦋' },
];

interface InteractiveKeychainCustomizerProps {
  onAddToCart?: (item: CartItem) => void;
}

export const InteractiveKeychainCustomizer: React.FC<InteractiveKeychainCustomizerProps> = ({ onAddToCart }) => {
  const [selectedThread, setSelectedThread] = useState<ThreadOption>(THREAD_OPTIONS[0]);
  const [selectedCharms, setSelectedCharms] = useState<CharmOption[]>([CHARM_OPTIONS[0], CHARM_OPTIONS[3]]);
  const [customText, setCustomText] = useState<string>('LISA');
  const [activeTab, setActiveTab] = useState<'threads' | 'charms' | 'letters'>('threads');
  const [addedAnimation, setAddedAnimation] = useState<boolean>(false);

  const toggleCharm = (charm: CharmOption) => {
    if (selectedCharms.some((c) => c.id === charm.id)) {
      setSelectedCharms(selectedCharms.filter((c) => c.id !== charm.id));
    } else {
      if (selectedCharms.length < 3) {
        setSelectedCharms([...selectedCharms, charm]);
      }
    }
  };

  const calculateTotal = () => {
    let base = 5.95;
    if (selectedCharms.length > 1) {
      base += (selectedCharms.length - 1) * 1.5;
    }
    return base;
  };

  const handleAdd = () => {
    const newItem: CartItem = {
      id: `custom-${Date.now()}`,
      title: `${selectedThread.name} Custom Weave`,
      price: calculateTotal(),
      threadColor: selectedThread.name,
      charms: selectedCharms.map((c) => `${c.icon} ${c.name}`),
      customName: customText.trim() || undefined,
      quantity: 1,
    };

    if (onAddToCart) {
      onAddToCart(newItem);
      setAddedAnimation(true);
      setTimeout(() => setAddedAnimation(false), 2000);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-3xl border border-stone-200 shadow-xl my-8">
      {/* Header */}
      <div className="text-center max-w-xl mx-auto mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Interactive Studio Sandbox</span>
        </div>
        <h2 className="text-3xl md:text-4xl font-serif font-bold text-slate-900">
          Build Your Custom Keychain
        </h2>
        <p className="text-slate-500 text-sm mt-2">
          Watch your custom weave and charms assemble in real-time.
        </p>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Visual Live Preview Canvas (Left 6 Cols) */}
        <div className="lg:col-span-6 bg-stone-50 rounded-2xl p-8 border border-stone-200/80 flex flex-col items-center justify-center relative min-h-[420px] shadow-inner">
          <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-md px-3 py-1 rounded-full text-[11px] font-bold text-slate-600 border border-stone-100 flex items-center gap-1.5 shadow-sm">
            <Eye className="w-3.5 h-3.5 text-purple-600" />
            <span>Real-Time SVG Canvas</span>
          </div>

          {/* SVG Animated Woven Keychain Representation */}
          <div className="relative w-48 h-80 flex flex-col items-center justify-start pt-4 transition-all duration-500">
            {/* Metal Ring */}
            <div className="w-14 h-14 rounded-full border-4 border-amber-400 bg-stone-200 shadow-md flex items-center justify-center relative z-20">
              <div className="w-8 h-8 rounded-full border-2 border-stone-400 bg-transparent"></div>
            </div>

            {/* Custom Woven Cord Body */}
            <div className={`w-10 h-44 rounded-b-2xl bg-gradient-to-b ${selectedThread.colorClass} shadow-lg relative -mt-2 flex flex-col items-center justify-around py-3 transition-colors duration-500 border border-black/10`}>
              {/* Pattern Texture Overlay */}
              <div className="w-full h-full absolute inset-0 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:6px_6px] opacity-25 rounded-b-2xl pointer-events-none"></div>

              {/* Letter Beads */}
              {customText.split('').slice(0, 6).map((letter, idx) => (
                <div key={idx} className="w-6 h-6 rounded-md bg-white text-slate-900 font-black text-xs flex items-center justify-center shadow-sm z-10 border border-stone-200 uppercase">
                  {letter}
                </div>
              ))}
            </div>

            {/* Dangling Charms */}
            <div className="flex gap-2 -mt-2 z-30">
              {selectedCharms.map((charm) => (
                <div key={charm.id} className="w-9 h-9 rounded-full bg-white shadow-md border border-stone-200 flex items-center justify-center text-lg animate-bounce transition-transform">
                  {charm.icon}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 text-center">
            <span className="text-xs text-slate-400 font-medium">Selected Thread: </span>
            <span className="text-xs font-bold text-slate-800">{selectedThread.name}</span>
          </div>
        </div>

        {/* Customization Control Panel (Right 6 Cols) */}
        <div className="lg:col-span-6 space-y-6">
          
          {/* Navigation Tabs */}
          <div className="flex border-b border-stone-200 gap-6 text-sm font-bold">
            <button
              onClick={() => setActiveTab('threads')}
              className={`pb-3 border-b-2 transition-all cursor-pointer ${activeTab === 'threads' ? 'border-purple-600 text-purple-700' : 'border-transparent text-slate-400 hover:text-slate-700'}`}
            >
              1. Thread Colors
            </button>
            <button
              onClick={() => setActiveTab('charms')}
              className={`pb-3 border-b-2 transition-all cursor-pointer ${activeTab === 'charms' ? 'border-purple-600 text-purple-700' : 'border-transparent text-slate-400 hover:text-slate-700'}`}
            >
              2. Accent Charms ({selectedCharms.length}/3)
            </button>
            <button
              onClick={() => setActiveTab('letters')}
              className={`pb-3 border-b-2 transition-all cursor-pointer ${activeTab === 'letters' ? 'border-purple-600 text-purple-700' : 'border-transparent text-slate-400 hover:text-slate-700'}`}
            >
              3. Personalized Name
            </button>
          </div>

          {/* Tab 1: Threads */}
          {activeTab === 'threads' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {THREAD_OPTIONS.map((thread) => (
                  <button
                    key={thread.id}
                    onClick={() => setSelectedThread(thread)}
                    className={`p-3.5 rounded-xl border text-left flex items-center gap-3 transition-all cursor-pointer ${selectedThread.id === thread.id ? 'border-purple-600 bg-purple-50/50 shadow-sm' : 'border-stone-200 hover:border-stone-300'}`}
                  >
                    <div className={`w-6 h-6 rounded-full bg-gradient-to-br ${thread.colorClass} shadow-sm border border-black/10`}></div>
                    <span className="text-xs font-bold text-slate-800">{thread.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Tab 2: Charms */}
          {activeTab === 'charms' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {CHARM_OPTIONS.map((charm) => {
                  const isSelected = selectedCharms.some((c) => c.id === charm.id);
                  return (
                    <button
                      key={charm.id}
                      onClick={() => toggleCharm(charm)}
                      className={`p-3 rounded-xl border text-center transition-all cursor-pointer relative ${isSelected ? 'border-purple-600 bg-purple-50/60 shadow-sm' : 'border-stone-200 hover:border-stone-300'}`}
                    >
                      {isSelected && (
                        <div className="absolute top-1.5 right-1.5 w-4 h-4 bg-purple-600 text-white rounded-full flex items-center justify-center text-[10px]">
                          <Check className="w-2.5 h-2.5" />
                        </div>
                      )}
                      <div className="text-2xl mb-1">{charm.icon}</div>
                      <div className="text-[11px] font-bold text-slate-800 leading-tight">{charm.name}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 3: Personalized Name */}
          {activeTab === 'letters' && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Name / Initials (Max 6 Characters)
                </label>
                <input
                  type="text"
                  maxLength={6}
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value.toUpperCase())}
                  placeholder="e.g. LISA"
                  className="w-full px-4 py-3 bg-stone-50 border border-stone-200 rounded-xl font-bold text-lg text-slate-900 tracking-widest focus:outline-none focus:ring-2 focus:ring-purple-500 uppercase"
                />
              </div>
            </div>
          )}

          {/* Pricing & Add to Flow Action Box */}
          <div className="p-5 bg-stone-50 rounded-2xl border border-stone-200 flex items-center justify-between mt-6">
            <div>
              <div className="text-xs text-slate-400 font-semibold uppercase">Estimated Total</div>
              <div className="text-2xl font-black text-slate-900">${calculateTotal().toFixed(2)}</div>
            </div>
            <button
              onClick={handleAdd}
              className={`px-6 py-3.5 text-xs font-bold uppercase tracking-wider rounded-xl shadow-md transition-all flex items-center gap-2 cursor-pointer ${
                addedAnimation ? 'bg-emerald-600 text-white' : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
            >
              {addedAnimation ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Added to Bag!</span>
                </>
              ) : (
                <>
                  <ShoppingBag className="w-4 h-4" />
                  <span>Add to Custom Bag</span>
                </>
              )}
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};

export default InteractiveKeychainCustomizer;
