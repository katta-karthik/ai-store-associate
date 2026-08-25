'use client';

import React, { useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { FilterSidebar } from '@/components/FilterSidebar';
import { ProductGrid } from '@/components/ProductGrid';
import { ChatWidget } from '@/components/ChatWidget';
import { CartDrawer } from '@/components/CartDrawer';
import { WishlistDrawer } from '@/components/WishlistDrawer';
import { ComparisonModal } from '@/components/ComparisonModal';
import { ResearchReportDrawer } from '@/components/ResearchReportDrawer';
import { useStore } from '@/store/useStore';
import { Sparkles, ShieldCheck, Zap, RefreshCw } from 'lucide-react';

export default function StorefrontPage() {
  const { fetchProducts, fetchCart, fetchWishlist } = useStore();

  useEffect(() => {
    fetchProducts();
    fetchCart();
    fetchWishlist();
  }, [fetchProducts, fetchCart, fetchWishlist]);

  return (
    <div className="min-h-screen flex flex-col bg-[#09090b]">
      {/* Top Navbar */}
      <Navbar />

      {/* Hero Banner with Glassmorphism */}
      <section className="relative overflow-hidden border-b border-surface-border bg-gradient-to-b from-indigo-950/30 via-surface/40 to-transparent py-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8">
          <div className="space-y-4 max-w-2xl text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen E-Commerce Associate Live</span>
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
              Shopping with an{' '}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-pink-400 to-purple-400">
                AI Store Associate
              </span>
            </h1>
            <p className="text-zinc-400 text-sm sm:text-base leading-relaxed">
              Experience conversational shopping. Speak naturally and watch your store filters,
              side-by-side product comparisons, deep research fit scores, and cart adapt in real time.
            </p>
          </div>

          {/* Quick Stat Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 w-full lg:w-auto">
            <div className="glass-panel rounded-2xl p-4 border border-surface-border flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <span className="block font-bold text-white text-sm">Real-Time</span>
                <span className="text-[11px] text-zinc-400">SSE Filter & Cart Sync</span>
              </div>
            </div>

            <div className="glass-panel rounded-2xl p-4 border border-surface-border flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400">
                <RefreshCw className="w-5 h-5" />
              </div>
              <div>
                <span className="block font-bold text-white text-sm">Universal</span>
                <span className="text-[11px] text-zinc-400">Store SDK</span>
              </div>
            </div>

            <div className="glass-panel rounded-2xl p-4 border border-surface-border flex items-center gap-3 col-span-2 sm:col-span-1">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="block font-bold text-white text-sm">0-Crash</span>
                <span className="text-[11px] text-zinc-400">SRE Guardrails</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Catalog Section */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Live Filter Sidebar */}
          <FilterSidebar />

          {/* Dynamic Product Grid */}
          <div className="flex-1 space-y-6">
            <div className="flex items-center justify-between border-b border-surface-border pb-4">
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight">Curated Footwear Catalog</h2>
                <p className="text-xs text-zinc-400">Real-time stock from Universal Commerce API</p>
              </div>
            </div>

            <ProductGrid />
          </div>
        </div>
      </main>

      {/* Slide-out Drawers & Modals */}
      <CartDrawer />
      <WishlistDrawer />
      <ComparisonModal />
      <ResearchReportDrawer />

      {/* Floating AI Store Associate Chat Widget */}
      <ChatWidget />
    </div>
  );
}
