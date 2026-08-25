'use client';

import React, { useState } from 'react';
import { Star, ShoppingBag, Check, Sparkles, AlertCircle, MessageCircle } from 'lucide-react';
import { useStore, Product } from '@/store/useStore';

export const ProductGrid: React.FC = () => {
  const { products, isLoading, highlightedProductIds, addToCart } = useStore();
  const [selectedVariants, setSelectedVariants] = useState<Record<string, string>>({});
  const [addedIds, setAddedIds] = useState<Record<string, boolean>>({});

  const handleSelectSize = (productId: string, variantId: string) => {
    setSelectedVariants((prev) => ({ ...prev, [productId]: variantId }));
  };

  const handleAddToCart = async (product: Product) => {
    const variantId = selectedVariants[product.id] || product.variants[0]?.id;
    if (!variantId) return;

    await addToCart(product.id, variantId);
    setAddedIds((prev) => ({ ...prev, [product.id]: true }));
    setTimeout(() => {
      setAddedIds((prev) => ({ ...prev, [product.id]: false }));
    }, 2000);
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((n) => (
          <div key={n} className="glass-panel rounded-2xl p-4 animate-pulse space-y-4">
            <div className="w-full h-52 bg-zinc-800 rounded-xl" />
            <div className="h-4 bg-zinc-800 rounded w-3/4" />
            <div className="h-4 bg-zinc-800 rounded w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="glass-panel rounded-3xl p-12 text-center max-w-lg mx-auto space-y-4">
        <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center mx-auto text-zinc-400">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-white">No products found</h3>
        <p className="text-sm text-zinc-400">
          Try loosening your price filters or ask our AI Associate to show alternative recommendations!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {products.map((product) => {
        const isHighlighted = highlightedProductIds.includes(product.id);
        const selectedVariantId = selectedVariants[product.id] || product.variants[0]?.id;
        const isAdded = addedIds[product.id];

        return (
          <div
            key={product.id}
            id={product.id}
            data-product-id={product.id}
            data-product-title={product.title}
            className={`glass-panel rounded-2xl p-4 flex flex-col justify-between transition-all duration-300 relative group hover:border-indigo-500/50 hover:shadow-xl hover:shadow-indigo-500/10 ${
              isHighlighted ? 'agent-highlight' : 'border-surface-border'
            }`}
          >
            {/* AI Recommendation Highlight Badge */}
            {isHighlighted && (
              <div className="absolute -top-3 right-4 px-3 py-1 rounded-full bg-gradient-to-r from-pink-500 to-indigo-500 text-white text-[11px] font-bold flex items-center gap-1 shadow-lg shadow-pink-500/30 animate-pulse">
                <Sparkles className="w-3 h-3" />
                <span>Sales Boy's Pick</span>
              </div>
            )}

            <div>
              {/* Product Image */}
              <div className="relative w-full h-56 rounded-xl overflow-hidden bg-zinc-900 mb-4">
                <img
                  src={product.primary_image}
                  alt={product.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded-md bg-black/60 backdrop-blur-md text-[10px] font-semibold text-zinc-300">
                  {product.brand}
                </span>
              </div>

              {/* Title & Ratings */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-indigo-400 font-semibold">{product.category}</span>
                  <div className="flex items-center gap-1 text-amber-400 text-xs">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    <span className="font-bold">{product.rating}</span>
                    <span className="text-zinc-500">({product.review_count})</span>
                  </div>
                </div>

                <h3 className="font-bold text-base text-white tracking-tight leading-snug line-clamp-1">
                  {product.title}
                </h3>
                <p className="text-xs text-zinc-400 line-clamp-2 leading-relaxed">
                  {product.description}
                </p>
              </div>

              {/* Sizes Selection */}
              <div className="mt-3 space-y-1.5">
                <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">Select UK Size:</span>
                <div className="flex flex-wrap gap-1.5">
                  {product.variants.map((v) => (
                    <button
                      key={v.id}
                      disabled={v.stock === 0}
                      onClick={() => handleSelectSize(product.id, v.id)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                        v.stock === 0
                          ? 'bg-zinc-900/50 text-zinc-600 line-through cursor-not-allowed border border-zinc-800'
                          : selectedVariantId === v.id
                          ? 'bg-primary text-white shadow-sm shadow-primary-glow font-bold'
                          : 'bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700 border border-zinc-700/50'
                      }`}
                    >
                      UK {v.size}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Price and Add to Cart Action */}
            <div className="pt-4 mt-4 border-t border-surface-border flex items-center justify-between">
              <div>
                <span className="text-[10px] text-zinc-500 block uppercase">Price</span>
                <span className="text-lg font-extrabold text-white">
                  ₹{product.base_price.toLocaleString('en-IN')}
                </span>
              </div>

              <button
                onClick={() => handleAddToCart(product)}
                className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md ${
                  isAdded
                    ? 'bg-emerald-600 text-white shadow-emerald-500/20'
                    : 'bg-primary hover:bg-primary-hover text-white shadow-primary-glow active:scale-95'
                }`}
              >
                {isAdded ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>In Your Bag!</span>
                  </>
                ) : (
                  <>
                    <ShoppingBag className="w-4 h-4" />
                    <span>Add to Bag</span>
                  </>
                )}
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};
