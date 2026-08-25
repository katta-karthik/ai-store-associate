'use client';

import React from 'react';
import { Sliders, RotateCcw, Sparkles } from 'lucide-react';
import { useStore } from '@/store/useStore';

export const FilterSidebar: React.FC = () => {
  const { filters, setFilters } = useStore();

  const categories = [
    { id: '', name: 'All Footwear' },
    { id: 'running-shoes', name: 'Road Running' },
    { id: 'trail-outdoor', name: 'Trail & Outdoor' },
    { id: 'lifestyle-sneakers', name: 'Sneakers / Retro' },
  ];

  const brands = ['Nike', 'Adidas', 'Puma', 'Salomon'];
  const sizes = ['8', '9', '10', '11'];

  const resetFilters = () => {
    setFilters({
      query: '',
      category: '',
      maxPrice: 15000,
      brand: '',
      size: '',
    });
  };

  return (
    <aside className="w-full lg:w-64 glass-panel rounded-2xl p-5 border border-surface-border space-y-6 h-fit sticky top-20">
      <div className="flex items-center justify-between border-b border-surface-border pb-4">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" />
          <h2 className="font-bold text-sm tracking-wide uppercase text-zinc-300">Live Filters</h2>
        </div>
        <button
          onClick={resetFilters}
          className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          Reset
        </button>
      </div>

      {/* Category Section */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Category</label>
        <div className="flex flex-col gap-1.5">
          {categories.map((cat) => (
            <button
              key={cat.id || 'all'}
              onClick={() => setFilters({ category: cat.id })}
              className={`text-left px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                filters.category === cat.id
                  ? 'bg-primary/20 text-indigo-300 border border-primary/40 shadow-sm shadow-primary-glow font-semibold'
                  : 'text-zinc-400 hover:bg-surface hover:text-zinc-200'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range Slider */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Max Price</label>
          <span className="text-xs font-bold text-indigo-300 px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20">
            ₹{filters.maxPrice.toLocaleString('en-IN')}
          </span>
        </div>
        <input
          type="range"
          min="4000"
          max="15000"
          step="500"
          value={filters.maxPrice}
          onChange={(e) => setFilters({ maxPrice: Number(e.target.value) })}
          className="w-full accent-primary bg-zinc-700 h-1.5 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-zinc-500">
          <span>₹4,000</span>
          <span>₹15,000</span>
        </div>
      </div>

      {/* Brand Filter */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Brand</label>
        <div className="grid grid-cols-2 gap-2">
          {brands.map((b) => (
            <button
              key={b}
              onClick={() => setFilters({ brand: filters.brand === b ? '' : b })}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                filters.brand.toLowerCase() === b.toLowerCase()
                  ? 'bg-primary text-white shadow-md shadow-primary-glow font-bold'
                  : 'bg-surface/80 border border-surface-border text-zinc-400 hover:text-white hover:border-zinc-500'
              }`}
            >
              {b}
            </button>
          ))}
        </div>
      </div>

      {/* Size Pills */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Shoe Size (UK/India)</label>
        <div className="grid grid-cols-4 gap-2">
          {sizes.map((s) => (
            <button
              key={s}
              onClick={() => setFilters({ size: filters.size === s ? '' : s })}
              className={`py-2 rounded-xl text-xs font-semibold transition-all ${
                filters.size === s
                  ? 'bg-accent text-white shadow-md shadow-accent-glow'
                  : 'bg-surface/80 border border-surface-border text-zinc-400 hover:text-white hover:border-zinc-500'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Real-Time Sync Badge */}
      <div className="pt-4 border-t border-surface-border flex items-center gap-2 text-[11px] text-zinc-400">
        <Sparkles className="w-3.5 h-3.5 text-primary animate-pulse" />
        <span>Controlled live by AI Associate</span>
      </div>
    </aside>
  );
};
