'use client';

import React from 'react';
import { ShoppingBag, Sparkles, Search, SlidersHorizontal, MessageSquare } from 'lucide-react';
import { useStore } from '@/store/useStore';

export const Navbar: React.FC = () => {
  const { cart, filters, setFilters, toggleChat, isChatOpen } = useStore();

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center shadow-lg shadow-primary-glow">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300">
              ShopAgent
            </span>
            <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              AI Store
            </span>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-md mx-4 hidden md:block">
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search running shoes, trail gear, streetwear..."
              value={filters.query}
              onChange={(e) => setFilters({ query: e.target.value })}
              className="w-full pl-10 pr-4 py-2 bg-surface/80 border border-surface-border rounded-xl text-sm text-foreground placeholder-zinc-500 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
            />
          </div>
        </div>

        {/* Cart & AI Chat Drawer Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleChat}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-all ${
              isChatOpen
                ? 'bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary-glow'
                : 'bg-surface hover:bg-surface-card text-zinc-300 border border-surface-border'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">AI Associate</span>
          </button>

          <button className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-surface hover:bg-surface-card border border-surface-border transition-all">
            <ShoppingBag className="w-5 h-5 text-zinc-200" />
            {cart.item_count > 0 && (
              <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-accent text-white text-xs font-bold flex items-center justify-center shadow-lg shadow-accent-glow animate-bounce">
                {cart.item_count}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
