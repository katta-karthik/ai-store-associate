'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Send, X, Mic, ShoppingBag, Zap, Heart, MessageSquare, ChevronRight, User, Award, CheckCircle2 } from 'lucide-react';
import { useShopAgent } from '../hooks/useShopAgent';
import { ShopAgentConfig } from '../types';

interface ShopAgentCompanionProps {
  config?: ShopAgentConfig;
  onAddToCart?: (productId: string, variantId: string) => void;
  onOpenCart?: () => void;
  onOpenWishlist?: () => void;
  renderModals?: boolean;
}

export const ShopAgentCompanion: React.FC<ShopAgentCompanionProps> = ({
  config,
  onAddToCart,
  onOpenCart,
  onOpenWishlist,
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
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Listen to product card hover events to glide salesperson
  useEffect(() => {
    const handleProductHover = (e: any) => {
      const card = e.target.closest('[data-product-id]');
      if (card) {
        const prodTitle = card.getAttribute('data-product-title') || 'this item';
        setEmotion('HYPED');
        setSpeechBubbleText(`✨ Sir, looking at the **${prodTitle}**? Absolute superstar quality! Shall I check your size?`);
      }
    };

    window.addEventListener('mouseover', handleProductHover);
    return () => window.removeEventListener('mouseover', handleProductHover);
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

  if (!mounted) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none select-none font-sans">
      {/* 1. Walkalong Floating Speech Bubble */}
      {!isExpanded && (
        <div className="mb-3 max-w-xs sm:max-w-sm pointer-events-auto transition-all duration-300 transform translate-y-0 opacity-100">
          <div className="relative glass-panel rounded-2xl p-3.5 border border-indigo-500/30 shadow-2xl bg-zinc-950/90 backdrop-blur-xl text-white">
            <div className="flex items-center gap-1.5 mb-1 text-[11px] font-bold text-indigo-400 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
              <span>ShopAgent Walkalong Associate</span>
              <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">LIVE</span>
            </div>
            <p className="text-xs text-zinc-200 leading-relaxed line-clamp-3">
              {speechBubbleText}
            </p>
            {/* Pointer notch */}
            <div className="absolute -bottom-1.5 right-8 w-3 h-3 bg-zinc-950/90 border-r border-b border-indigo-500/30 transform rotate-45" />
          </div>
        </div>
      )}

      {/* 2. Expanded Chat Conversation Drawer */}
      {isExpanded && (
        <div className="mb-3 w-80 sm:w-96 h-[480px] pointer-events-auto rounded-2xl glass-panel border border-indigo-500/30 shadow-2xl bg-zinc-950/95 backdrop-blur-xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5">
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

      {/* 3. Floating Spatial Walkalong Companion Avatar Button */}
      <div className="flex items-center gap-3 pointer-events-auto">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="group relative flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-600 via-indigo-500 to-pink-500 p-0.5 shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
          aria-label="Toggle ShopAgent Associate"
        >
          <div className="w-full h-full rounded-full bg-zinc-950 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 bg-indigo-500/10 group-hover:bg-indigo-500/20 transition" />
            <Sparkles className="w-6 h-6 text-indigo-400 group-hover:text-pink-400 transition-colors transform group-hover:rotate-12 duration-300" />
            {/* Live Indicator Dot */}
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-emerald-400 rounded-full ring-2 ring-zinc-950" />
          </div>
        </button>
      </div>
    </div>
  );
};
