'use client';

import React from 'react';
import { ShoppingBag, X, Trash2, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { useStore } from '@/store/useStore';

export const CartDrawer: React.FC = () => {
  const { isCartOpen, toggleCart, cart, removeFromCart } = useStore();

  if (!isCartOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={toggleCart}
        className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md glass-panel border-l border-surface-border bg-surface/95 flex flex-col shadow-2xl animate-slide-up">
          {/* Header */}
          <div className="p-5 border-b border-surface-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-primary/20 text-primary border border-primary/30 flex items-center justify-center">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-white">Your Shopping Bag</h3>
                <p className="text-xs text-zinc-400">{cart.item_count} items selected</p>
              </div>
            </div>
            <button
              onClick={toggleCart}
              className="w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {cart.items.length === 0 ? (
              <div className="text-center py-16 space-y-4">
                <div className="w-16 h-16 rounded-full bg-zinc-800 flex items-center justify-center mx-auto text-zinc-500">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <h4 className="font-bold text-white text-base">Your bag is empty</h4>
                <p className="text-xs text-zinc-400 max-w-xs mx-auto">
                  Ask our AI Associate to recommend the best shoe for your needs or add directly from the store!
                </p>
              </div>
            ) : (
              cart.items.map((item) => (
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
                    <div className="flex items-center gap-2 mt-1">
                      {item.size && (
                        <span className="px-2 py-0.5 rounded-md bg-zinc-800 border border-zinc-700 text-[10px] text-zinc-300 font-semibold">
                          Size {item.size}
                        </span>
                      )}
                      <span className="text-[11px] text-zinc-400">Qty: {item.quantity}</span>
                    </div>
                    <span className="block mt-1 text-xs font-extrabold text-indigo-300">
                      ₹{item.total_price.toLocaleString('en-IN')}
                    </span>
                  </div>

                  <button
                    onClick={() => removeFromCart(item.item_id)}
                    className="p-2 rounded-xl text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Footer Subtotal & Checkout */}
          {cart.items.length > 0 && (
            <div className="p-5 border-t border-surface-border bg-surface/90 space-y-4">
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-zinc-400">
                  <span>Subtotal</span>
                  <span>₹{cart.subtotal.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-xs text-zinc-400">
                  <span>Shipping</span>
                  <span className="text-emerald-400 font-semibold">FREE</span>
                </div>
                <div className="flex justify-between text-base font-extrabold text-white pt-2 border-t border-zinc-800">
                  <span>Total</span>
                  <span className="text-indigo-400">₹{cart.subtotal.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <button className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-primary to-accent hover:opacity-95 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-primary-glow active:scale-98 transition-all">
                <span>Proceed to Express Checkout</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="flex items-center justify-center gap-2 text-[10px] text-zinc-500">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Encrypted 256-bit Universal Checkout</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
