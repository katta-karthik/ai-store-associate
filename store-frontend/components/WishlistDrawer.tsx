'use client';

import React from 'react';
import { Heart, X, Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { useStore } from '@/store/useStore';

export const WishlistDrawer: React.FC = () => {
  const { isWishlistOpen, toggleWishlist, wishlist, removeFromWishlist, addToCart } = useStore();

  if (!isWishlistOpen) return null;

  const handleMoveToCart = async (productId: string, variantId?: string, itemId?: string) => {
    if (variantId) {
      await addToCart(productId, variantId);
    }
    if (itemId) {
      await removeFromWishlist(itemId);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={toggleWishlist}
        className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md glass-panel border-l border-surface-border bg-surface/95 flex flex-col shadow-2xl animate-slide-up">
          {/* Header */}
          <div className="p-5 border-b border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-pink-500/20 text-pink-400 border border-pink-500/30 flex items-center justify-center">
                <Heart className="w-5 h-5 fill-pink-500" />
              </div>
              <div>
                <h3 className="font-bold text-base text-white">Saved Wishlist</h3>
                <p className="text-xs text-zinc-400">{wishlist.item_count} items saved for later</p>
              </div>
            </div>
            <button
              onClick={toggleWishlist}
              className="w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Wishlist Items List */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {wishlist.items.length === 0 ? (
              <div className="text-center py-16 space-y-4">
                <div className="w-16 h-16 rounded-full bg-zinc-800 flex items-center justify-center mx-auto text-zinc-500">
                  <Heart className="w-8 h-8" />
                </div>
                <h4 className="font-bold text-white text-base">Your wishlist is empty</h4>
                <p className="text-xs text-zinc-400 max-w-xs mx-auto">
                  Tell our AI Associate to *"save this pair for later"* whenever you see a shoe you like!
                </p>
              </div>
            ) : (
              wishlist.items.map((item) => (
                <div
                  key={item.item_id}
                  className="glass-panel rounded-2xl p-3.5 border border-surface-border flex gap-3.5 items-center group"
                >
                  <div className="w-16 h-16 rounded-xl bg-zinc-900 overflow-hidden flex-shrink-0">
                    <img
                      src={item.image || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200'}
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-white truncate">{item.title}</h4>
                    <span className="block mt-0.5 text-xs font-extrabold text-indigo-300">
                      ₹{item.price.toLocaleString('en-IN')}
                    </span>
                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={() => handleMoveToCart(item.product_id, item.variant_id, item.item_id)}
                        className="px-2.5 py-1 rounded-lg bg-primary/20 hover:bg-primary text-indigo-300 hover:text-white border border-primary/30 text-[10px] font-bold flex items-center gap-1 transition-all"
                      >
                        <ShoppingBag className="w-3 h-3" />
                        <span>Move to Bag</span>
                      </button>
                    </div>
                  </div>

                  <button
                    onClick={() => removeFromWishlist(item.item_id)}
                    className="p-2 rounded-xl text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
