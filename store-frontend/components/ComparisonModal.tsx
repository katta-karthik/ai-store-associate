'use client';

import React from 'react';
import { X, Check, Star, ShoppingBag, Zap, Award, Sparkles } from 'lucide-react';
import { useStore, Product } from '@/store/useStore';

export const ComparisonModal: React.FC = () => {
  const { isComparisonOpen, toggleComparisonModal, comparisonProducts, addToCart } = useStore();

  if (!isComparisonOpen || comparisonProducts.length < 2) return null;

  const [p1, p2] = comparisonProducts;

  const specRows = [
    { label: 'Brand', v1: p1.brand, v2: p2.brand },
    { label: 'Category', v1: p1.category, v2: p2.category },
    { label: 'Cushioning', v1: p1.specs?.cushioning || 'Standard EVA', v2: p2.specs?.cushioning || 'Standard EVA' },
    { label: 'Shoe Weight', v1: p1.specs?.weight || '285g', v2: p2.specs?.weight || '295g' },
    { label: 'Heel-to-Toe Drop', v1: p1.specs?.heel_drop || '10mm', v2: p2.specs?.heel_drop || '10mm' },
    { label: 'Primary Terrain', v1: p1.specs?.terrain || 'Road / Pavement', v2: p2.specs?.terrain || 'Road / Track' },
    { label: 'Fit Profile', v1: p1.specs?.fit || 'True to Size', v2: p2.specs?.fit || 'Athletic Snug' },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        onClick={toggleComparisonModal}
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
      />

      <div className="min-h-full flex items-center justify-center p-4 sm:p-6">
        <div className="relative w-full max-w-4xl glass-panel rounded-3xl border border-surface-border bg-surface/95 shadow-2xl p-6 sm:p-8 space-y-6 animate-slide-up">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-surface-border pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white shadow-lg shadow-primary-glow">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-xl text-white">Side-by-Side Model Comparison</h3>
                <p className="text-xs text-zinc-400">Technical specifications & consultative fit evaluation</p>
              </div>
            </div>
            <button
              onClick={toggleComparisonModal}
              className="w-9 h-9 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Sizing & Fit Advisor Banner */}
          <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-zinc-300 space-y-0.5">
              <span className="font-bold text-indigo-300 block">AI Associate Fit Advisor:</span>
              <p>
                Both models are exceptional in their class. If you prefer high-energy rebound and plush step-in comfort, pick <strong>{p2.title}</strong>. For everyday training stability and lightweight tempo, choose <strong>{p1.title}</strong>.
              </p>
            </div>
          </div>

          {/* Product Cards Side-by-Side */}
          <div className="grid grid-cols-2 gap-4 sm:gap-6">
            {[p1, p2].map((prod) => (
              <div key={prod.id} className="glass-panel rounded-2xl p-4 border border-surface-border flex flex-col justify-between space-y-3">
                <div className="relative w-full h-44 rounded-xl overflow-hidden bg-zinc-900">
                  <img
                    src={prod.primary_image}
                    alt={prod.title}
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute bottom-2 left-2 px-2.5 py-0.5 rounded-lg bg-black/70 backdrop-blur-md text-[11px] font-bold text-white">
                    {prod.brand}
                  </span>
                </div>

                <div>
                  <h4 className="font-bold text-sm text-white line-clamp-1">{prod.title}</h4>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-base font-extrabold text-indigo-300">
                      ₹{prod.base_price.toLocaleString('en-IN')}
                    </span>
                    <div className="flex items-center gap-1 text-amber-400 text-xs">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span className="font-bold">{prod.rating}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => addToCart(prod.id, prod.variants[0]?.id)}
                  className="w-full py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-bold flex items-center justify-center gap-1.5 shadow-md shadow-primary-glow transition-all"
                >
                  <ShoppingBag className="w-3.5 h-3.5" />
                  <span>Add to Bag</span>
                </button>
              </div>
            ))}
          </div>

          {/* Comparison Table */}
          <div className="border border-surface-border rounded-2xl overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="bg-surface/90 border-b border-surface-border text-zinc-400">
                  <th className="py-3 px-4 font-semibold uppercase text-[11px]">Specification</th>
                  <th className="py-3 px-4 font-semibold text-white">{p1.title}</th>
                  <th className="py-3 px-4 font-semibold text-white">{p2.title}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border text-zinc-300">
                {specRows.map((row, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-surface/40' : 'bg-transparent'}>
                    <td className="py-2.5 px-4 font-semibold text-zinc-400">{row.label}</td>
                    <td className="py-2.5 px-4">{row.v1}</td>
                    <td className="py-2.5 px-4">{row.v2}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
