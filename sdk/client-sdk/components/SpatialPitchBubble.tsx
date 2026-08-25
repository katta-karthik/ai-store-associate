'use client';

import React, { useState } from 'react';
import { Sparkles, ShoppingBag, Zap, Award, CheckCircle2, X } from 'lucide-react';
import { EmotionType } from '../types';

interface SpatialPitchBubbleProps {
  productId: string;
  productTitle: string;
  price?: number;
  emotion: EmotionType;
  pitchText: string;
  onAddToCart?: (productId: string, variantId: string) => void;
  onCompare?: (productId: string) => void;
  onClose?: () => void;
  rememberedSize?: string;
}

export const SpatialPitchBubble: React.FC<SpatialPitchBubbleProps> = ({
  productId,
  productTitle,
  price,
  emotion,
  pitchText,
  onAddToCart,
  onCompare,
  onClose,
  rememberedSize = '10',
}) => {
  const [selectedSize, setSelectedSize] = useState<string>(rememberedSize);
  const [isAdded, setIsAdded] = useState(false);

  const availableSizes = ['8', '9', '10', '11'];

  const getEmotionDetails = () => {
    switch (emotion) {
      case 'HYPED':
      case 'CHARMING_COMPLIMENT':
        return { icon: '🤩', badge: 'HERO LOOK', color: 'from-pink-500 to-indigo-600', border: 'border-pink-500/40' };
      case 'FIT_ADVISOR':
      case 'ANALYTICAL':
        return { icon: '🧐', badge: 'FIT DOCTOR', color: 'from-amber-500 to-indigo-600', border: 'border-amber-500/40' };
      case 'CELEBRATING':
        return { icon: '🎉', badge: 'DEAL CLOSED', color: 'from-emerald-500 to-indigo-600', border: 'border-emerald-500/40' };
      default:
        return { icon: '✨', badge: 'WALKALONG SPECIALIST', color: 'from-indigo-600 to-purple-600', border: 'border-indigo-500/40' };
    }
  };

  const emo = getEmotionDetails();

  const handlePackInBag = () => {
    setIsAdded(true);
    onAddToCart?.(productId, `var_${productId}_${selectedSize}`);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <div className={`relative w-80 sm:w-88 rounded-2xl p-4 bg-zinc-950/95 backdrop-blur-2xl border ${emo.border} shadow-2xl text-white font-sans animate-in fade-in zoom-in-95 duration-200 pointer-events-auto select-none`}>
      {/* Header Tag */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-base">{emo.icon}</span>
          <span className={`text-[10px] font-black tracking-widest px-2 py-0.5 rounded-full bg-gradient-to-r ${emo.color} text-white shadow-sm`}>
            {emo.badge}
          </span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Flattering Sweet Pitch Quote */}
      <div className="relative mb-3 pl-2 border-l-2 border-indigo-500/60">
        <p className="text-xs text-zinc-100 font-medium leading-relaxed">
          {pitchText || `Sir! Look at the **${productTitle}**! You will look 100% like a movie hero in this!`}
        </p>
      </div>

      {/* 1-Tap Interactive Sizing Pills */}
      <div className="space-y-1.5 mb-3 bg-zinc-900/60 rounded-xl p-2 border border-zinc-800/80">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-zinc-400 font-medium">Select UK Size:</span>
          {rememberedSize && (
            <span className="text-indigo-400 font-bold">Size UK {rememberedSize} (Your fit)</span>
          )}
        </div>
        <div className="flex gap-1.5">
          {availableSizes.map((sz) => {
            const isSelected = selectedSize === sz;
            const isMySize = sz === rememberedSize;
            return (
              <button
                key={sz}
                onClick={() => setSelectedSize(sz)}
                className={`flex-1 py-1 px-1.5 rounded-lg text-[11px] font-bold transition-all ${
                  isSelected
                    ? 'bg-indigo-600 text-white shadow-md ring-2 ring-indigo-400'
                    : 'bg-zinc-800/90 text-zinc-300 hover:bg-zinc-700'
                }`}
              >
                {isMySize ? `⭐ ${sz}` : sz}
              </button>
            );
          })}
        </div>
      </div>

      {/* 1-Tap Instant Purchase & Compare CTA Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={handlePackInBag}
          className={`flex-1 py-2 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-lg ${
            isAdded
              ? 'bg-emerald-600 text-white animate-bounce'
              : 'bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white shadow-indigo-500/25'
          }`}
        >
          {isAdded ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Packed in Your Bag! 🎉</span>
            </>
          ) : (
            <>
              <ShoppingBag className="w-3.5 h-3.5" />
              <span>Pack in my Bag (Size {selectedSize})</span>
            </>
          )}
        </button>

        {onCompare && (
          <button
            onClick={() => onCompare(productId)}
            className="p-2 rounded-xl bg-zinc-800/90 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 hover:text-white transition"
            title="Side-by-side comparison"
          >
            <Zap className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
