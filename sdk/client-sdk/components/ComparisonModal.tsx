'use client';

import React, { useState } from 'react';
import { X, Check, Star, ShoppingBag, Zap, Award, Sparkles } from 'lucide-react';
import { Product } from '../types';

interface ComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  products: Product[];
  onAddToCart?: (productId: string, variantId: string) => void;
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  isOpen,
  onClose,
  products,
  onAddToCart,
}) => {
  const [selectedVariants, setSelectedVariants] = useState<Record<string, string>>({});

  if (!isOpen || products.length < 2) return null;

  const [p1, p2] = products;

  const getActiveVariant = (product: Product) => {
    return selectedVariants[product.id] || product.variants?.[0]?.id || '';
  };

  const handleSelectVariant = (productId: string, variantId: string) => {
    setSelectedVariants((prev) => ({ ...prev, [productId]: variantId }));
  };

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
    <div className="fixed inset-0 z-50 overflow-y-auto font-sans">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
      />

      <div className="min-h-full flex items-center justify-center p-4 sm:p-6">
        <div className="relative w-full max-w-4xl rounded-3xl border border-zinc-800 bg-zinc-950/95 shadow-2xl p-6 sm:p-8 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-white shadow-lg">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-xl text-white">Side-by-Side Model Comparison</h3>
                <p className="text-xs text-zinc-400">Technical specifications & consultative fit evaluation</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-9 h-9 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Product Header Cards */}
          <div className="grid grid-cols-2 gap-4 sm:gap-6">
            {[p1, p2].map((prod) => (
              <div
                key={prod.id}
                className="bg-zinc-900/60 rounded-2xl p-4 border border-zinc-800 flex flex-col items-center text-center space-y-3"
              >
                <div className="w-28 h-28 sm:w-36 sm:h-36 rounded-xl overflow-hidden bg-zinc-950">
                  <img
                    src={prod.primary_image}
                    alt={prod.title}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                    {prod.brand}
                  </span>
                  <h4 className="font-bold text-white text-sm line-clamp-1">{prod.title}</h4>
                  <div className="text-lg font-black text-white">
                    ₹{prod.base_price.toLocaleString('en-IN')}
                  </div>
                </div>

                {/* Interactive Size Pill Selector */}
                {prod.variants && prod.variants.length > 0 && (
                  <div className="w-full space-y-1.5 pt-1">
                    <span className="text-[10px] font-medium text-zinc-400 block text-left">
                      Select Size:
                    </span>
                    <div className="flex flex-wrap gap-1 justify-center">
                      {prod.variants.map((v) => {
                        const activeVarId = getActiveVariant(prod);
                        const isSelected = activeVarId === v.id;
                        return (
                          <button
                            key={v.id}
                            disabled={v.stock === 0}
                            onClick={() => handleSelectVariant(prod.id, v.id)}
                            className={`px-2 py-1 rounded-md text-[10px] font-bold transition-all ${
                              v.stock === 0
                                ? 'opacity-30 bg-zinc-800 line-through cursor-not-allowed text-zinc-500'
                                : isSelected
                                ? 'bg-indigo-600 text-white shadow-sm ring-1 ring-indigo-400'
                                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                            }`}
                          >
                            {v.size || 'Standard'}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                <button
                  onClick={() => onAddToCart?.(prod.id, getActiveVariant(prod))}
                  className="w-full py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-bold text-white text-xs flex items-center justify-center gap-1.5 transition-all shadow-md mt-2"
                >
                  <ShoppingBag className="w-3.5 h-3.5" />
                  <span>Add to Cart</span>
                </button>
              </div>
            ))}
          </div>

          {/* Specs Table */}
          <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/40">
            <table className="w-full text-left text-xs">
              <tbody className="divide-y divide-zinc-800">
                {specRows.map((row, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-transparent' : 'bg-zinc-900/20'}>
                    <td className="py-3 px-4 text-zinc-400 font-medium w-1/3">{row.label}</td>
                    <td className="py-3 px-4 text-white font-semibold text-center border-l border-zinc-800/60 w-1/3">
                      {row.v1}
                    </td>
                    <td className="py-3 px-4 text-white font-semibold text-center border-l border-zinc-800/60 w-1/3">
                      {row.v2}
                    </td>
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
