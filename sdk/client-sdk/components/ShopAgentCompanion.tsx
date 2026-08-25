'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Sparkles, Send, X, Mic, ShoppingBag, Zap, Heart, MessageSquare, ChevronRight, User, Award, CheckCircle2 } from 'lucide-react';
import { useShopAgent } from '../hooks/useShopAgent';
import { ShopAgentConfig } from '../types';
import { SpatialPitchBubble } from './SpatialPitchBubble';

interface ShopAgentCompanionProps {
  config?: ShopAgentConfig;
  onAddToCart?: (productId: string, variantId: string) => void;
  onOpenCart?: () => void;
  onOpenWishlist?: () => void;
  onCompare?: (productId: string) => void;
}

interface SpatialTarget {
  id: string;
  title: string;
  price?: number;
  top: number;
  left: number;
  side: 'left' | 'right' | 'top';
}

export const ShopAgentCompanion: React.FC<ShopAgentCompanionProps> = ({
  config,
  onAddToCart,
  onOpenCart,
  onOpenWishlist,
  onCompare,
}) => {
  const {
    chatMessages,
    isStreaming,
    isListening,
    emotion,
    setEmotion,
    speechBubbleText,
    setSpeechBubbleText,
    sendMessage,
    toggleVoiceInput,
  } = useShopAgent(config);

  const [input, setInput] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [spatialTarget, setSpatialTarget] = useState<SpatialTarget | null>(null);
  const [isGliding, setIsGliding] = useState(false);

  const chatBottomRef = useRef<HTMLDivElement>(null);
  const glideTimeoutRef = useRef<any>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Spatial Product Hover & Click Glide Tracker
  useEffect(() => {
    const handleProductInteraction = (e: any) => {
      const card = e.target.closest('[data-product-id]');
      if (card) {
        const prodId = card.getAttribute('data-product-id') || 'prod_default';
        const prodTitle = card.getAttribute('data-product-title') || 'this shoe';
        const prodPrice = parseFloat(card.getAttribute('data-product-price') || '0');

        const rect = card.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // Determine best dock side to avoid covering store UI
        let dockLeft = 0;
        let dockTop = rect.top + window.scrollY;
        let side: 'left' | 'right' | 'top' = 'right';

        if (rect.right + 360 < viewportWidth) {
          dockLeft = rect.right + 16;
          side = 'right';
        } else if (rect.left - 360 > 0) {
          dockLeft = rect.left - 360;
          side = 'left';
        } else {
          dockLeft = Math.max(16, rect.left);
          dockTop = Math.max(80, rect.top - 180);
          side = 'top';
        }

        // Clamp inside viewport
        dockTop = Math.max(80, Math.min(rect.top + 20, viewportHeight - 280));
        dockLeft = Math.max(16, Math.min(dockLeft, viewportWidth - 380));

        setIsGliding(true);
        setEmotion('HYPED');
        setSpatialTarget({
          id: prodId,
          title: prodTitle,
          price: prodPrice || undefined,
          top: dockTop,
          left: dockLeft,
          side,
        });

        setSpeechBubbleText(`✨ Sir! You have an amazing eye! In the **${prodTitle}**, you will look 100% like a movie hero! Shall I pack your size?`);

        if (glideTimeoutRef.current) clearTimeout(glideTimeoutRef.current);
        glideTimeoutRef.current = setTimeout(() => setIsGliding(false), 600);
      }
    };

    window.addEventListener('mouseover', handleProductInteraction);
    return () => window.removeEventListener('mouseover', handleProductInteraction);
  }, [setEmotion, setSpeechBubbleText]);

  useEffect(() => {
    if (isExpanded) {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isExpanded]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput('');
  };

  const handleDismissSpatialTarget = () => {
    setSpatialTarget(null);
    setEmotion('CHARMING_COMPLIMENT');
    setSpeechBubbleText("Sir, I'm right here walking beside you! Check out any pair you like!");
  };

  if (!mounted) return null;

  return (
    <>
      {/* 1. Spatial Floating Sales Associate Gliding to Target Product */}
      {spatialTarget && !isExpanded && (
        <div
          style={{
            position: 'fixed',
            top: `${spatialTarget.top}px`,
            left: `${spatialTarget.left}px`,
            zIndex: 9999,
            transition: 'all 0.45s cubic-bezier(0.16, 1, 0.3, 1)',
            transform: isGliding ? 'scale(1.05) translateZ(0)' : 'scale(1) translateZ(0)',
          }}
          className="pointer-events-auto select-none font-sans flex flex-col items-start gap-2"
        >
          {/* Sales Associate Avatar Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-950/95 border border-indigo-500/50 shadow-xl backdrop-blur-xl">
            <span className="text-sm animate-pulse">🤩</span>
            <span className="text-[11px] font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-indigo-300">
              Personal Associate At Your Side
            </span>
          </div>

          {/* Interactive Spatial Deal-Closing Callout */}
          <SpatialPitchBubble
            productId={spatialTarget.id}
            productTitle={spatialTarget.title}
            price={spatialTarget.price}
            emotion={emotion}
            pitchText={speechBubbleText}
            onAddToCart={(pid, vid) => {
              onAddToCart?.(pid, vid);
              setEmotion('CELEBRATING');
              setSpeechBubbleText("🎉 Wah Sir! Outstanding taste! I've packed this right into your shopping bag!");
            }}
            onCompare={onCompare}
            onClose={handleDismissSpatialTarget}
          />
        </div>
      )}

      {/* 2. Standard Walkalong Dock at Bottom Right */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none select-none font-sans">
        {/* Floating Idle Speech Bubble when not attached to a specific product */}
        {!spatialTarget && !isExpanded && (
          <div className="mb-3 max-w-xs sm:max-w-sm pointer-events-auto transition-all duration-300 transform translate-y-0 opacity-100">
            <div className="relative rounded-2xl p-3.5 border border-indigo-500/30 shadow-2xl bg-zinc-950/95 backdrop-blur-xl text-white">
              <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-indigo-400 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                <span>ShopAgent Walkalong Associate</span>
                <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">LIVE</span>
              </div>
              <p className="text-xs text-zinc-200 leading-relaxed line-clamp-3">
                {speechBubbleText}
              </p>
              <div className="absolute -bottom-1.5 right-8 w-3 h-3 bg-zinc-950/95 border-r border-b border-indigo-500/30 transform rotate-45" />
            </div>
          </div>
        )}

        {/* 3. Expanded Full Chat Conversation Drawer */}
        {isExpanded && (
          <div className="mb-3 w-80 sm:w-96 h-[480px] pointer-events-auto rounded-2xl border border-indigo-500/30 shadow-2xl bg-zinc-950/95 backdrop-blur-xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5">
            {/* Header */}
            <div className="p-3.5 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-pink-500 flex items-center justify-center text-white shadow-lg">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                    ShopAgent Associate
                    <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-ping" />
                  </h3>
                  <p className="text-[10px] text-zinc-400">Walkalong Retail Specialist</p>
                </div>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-zinc-800 transition"
                aria-label="Minimize"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-6 h-6 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-300 text-[10px] shrink-0 mt-0.5">
                      ✨
                    </div>
                  )}
                  <div
                    className={`max-w-[82%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none shadow-md'
                        : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-bl-none shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content || (isStreaming ? 'Thinking...' : '')}</p>
                    <span className="block text-[9px] mt-1 text-zinc-400 text-right">{msg.timestamp}</span>
                  </div>
                </div>
              ))}
              <div ref={chatBottomRef} />
            </div>

            {/* Quick Prompts */}
            <div className="px-3 py-1.5 border-t border-zinc-800/80 flex items-center gap-1.5 overflow-x-auto text-[11px] bg-zinc-900/30 scrollbar-none">
              <button
                onClick={() => sendMessage('Show marathon road shoes under 10000')}
                className="whitespace-nowrap px-2.5 py-1 rounded-full bg-zinc-800/80 hover:bg-indigo-600/30 hover:border-indigo-500/50 border border-zinc-700 text-zinc-300 hover:text-white transition"
              >
                🏃 Marathon Shoes
              </button>
              <button
                onClick={() => sendMessage('Compare Pegasus vs Ultraboost')}
                className="whitespace-nowrap px-2.5 py-1 rounded-full bg-zinc-800/80 hover:bg-indigo-600/30 hover:border-indigo-500/50 border border-zinc-700 text-zinc-300 hover:text-white transition"
              >
                ⚖️ Compare Top Pairs
              </button>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="p-3 border-t border-zinc-800 flex items-center gap-2 bg-zinc-900/80">
              <button
                type="button"
                onClick={toggleVoiceInput}
                className={`p-2 rounded-xl border transition ${
                  isListening
                    ? 'bg-red-500/20 border-red-500 text-red-400 animate-pulse'
                    : 'bg-zinc-800/80 border-zinc-700 text-zinc-300 hover:text-white'
                }`}
                title="Voice Shopping"
              >
                <Mic className="w-4 h-4" />
              </button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask anything or speak..."
                className="flex-1 bg-zinc-950 border border-zinc-700 rounded-xl px-3 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="p-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 rounded-xl text-white transition shadow-md"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        {/* 4. Floating Avatar Launcher Button */}
        <div className="flex items-center gap-3 pointer-events-auto">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="group relative flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-600 via-indigo-500 to-pink-500 p-0.5 shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
            aria-label="Toggle ShopAgent Associate"
          >
            <div className="w-full h-full rounded-full bg-zinc-950 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-indigo-500/10 group-hover:bg-indigo-500/20 transition" />
              <span className="text-xl transform group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300">
                {emotion === 'HYPED' ? '🤩' : emotion === 'CELEBRATING' ? '🎉' : emotion === 'FIT_ADVISOR' ? '🧐' : '✨'}
              </span>
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-emerald-400 rounded-full ring-2 ring-zinc-950" />
            </div>
          </button>
        </div>
      </div>
    </>
  );
};
