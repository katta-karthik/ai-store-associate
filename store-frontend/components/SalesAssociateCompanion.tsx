'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Send, X, Mic, ShoppingBag, Zap, Heart, MessageSquare, ChevronRight, User, Award, CheckCircle2 } from 'lucide-react';
import { useStore, Product } from '@/store/useStore';

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001/api/v1';

export const SalesAssociateCompanion: React.FC = () => {
  const {
    sessionId,
    shopperId,
    setComparisonProducts,
    setResearchReport,
    chatMessages,
    addChatMessage,
    updateLastAssistantMessage,
    setFilters,
    setHighlightedProducts,
    fetchCart,
    fetchWishlist,
    isStreaming,
    setIsStreaming,
  } = useStore();

  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [emotion, setEmotion] = useState<'HYPED' | 'CHARMING_COMPLIMENT' | 'ANALYTICAL' | 'CELEBRATING' | 'FIT_ADVISOR'>('CHARMING_COMPLIMENT');
  const [speechBubbleText, setSpeechBubbleText] = useState("👋 **Namaste Sir!** I'm your personal sales associate walking with you today. What hero look or running shoes can I find for you?");
  const [mounted, setMounted] = useState(false);

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          if (transcript) {
            setInput(transcript);
            handleSendMessage(transcript);
          }
          setIsListening(false);
        };

        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
      }
    }
  }, []);

  // Listen to product card hover events to glide salesperson
  useEffect(() => {
    const handleProductHover = (e: any) => {
      const card = e.target.closest('[data-product-id]');
      if (card) {
        const prodTitle = card.getAttribute('data-product-title') || 'this shoe';
        setEmotion('HYPED');
        setSpeechBubbleText(`✨ Sir, looking at the **${prodTitle}**? Absolute superstar quality! Shall I check your size?`);
      }
    };

    window.addEventListener('mouseover', handleProductHover);
    return () => window.removeEventListener('mouseover', handleProductHover);
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || input.trim();
    if (!query || isStreaming) return;

    setInput('');
    addChatMessage({ role: 'user', content: query });
    addChatMessage({ role: 'assistant', content: '' });
    setIsStreaming(true);
    setSpeechBubbleText("Analyzing our best pairs for you, Sir...");
    setEmotion('ANALYTICAL');

    try {
      const response = await fetch(`${AGENT_API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId || 'shopper_session_001',
          shopper_id: shopperId || 'shopper_001',
          message: query,
        }),
      });

      if (!response.body) throw new Error('No stream body received');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullAssistantText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/event:\s*([^\n]+)/);
          const dataMatch = block.match(/data:\s*([^\n]+)/);

          const eventType = eventMatch ? eventMatch[1].trim() : 'token';
          const dataContent = dataMatch ? dataMatch[1].trim() : '';

          if (eventType === 'emotion' && dataContent) {
            try {
              const emoObj = JSON.parse(dataContent);
              if (emoObj.emotion) setEmotion(emoObj.emotion);
            } catch (err) {}
          } else if (eventType === 'ui_action' && dataContent) {
            try {
              const actionObj = JSON.parse(dataContent);
              if (actionObj.action === 'SET_FILTERS') {
                const payload = actionObj.payload;
                const newFilters: any = {};
                if (payload.category) newFilters.category = payload.category;
                if (payload.max_price) newFilters.maxPrice = payload.max_price;
                if (payload.brand) newFilters.brand = payload.brand;
                if (payload.size) newFilters.size = payload.size;
                setFilters(newFilters);
              } else if (actionObj.action === 'HIGHLIGHT_PRODUCTS') {
                setHighlightedProducts(actionObj.payload.product_ids || []);
              } else if (actionObj.action === 'OPEN_COMPARISON_MODAL') {
                if (actionObj.payload.products) {
                  setComparisonProducts(actionObj.payload.products);
                }
              } else if (actionObj.action === 'SHOW_RESEARCH_REPORT') {
                setResearchReport(actionObj.payload);
              } else if (actionObj.action === 'AVATAR_GLIDE') {
                if (actionObj.payload.emotion) setEmotion(actionObj.payload.emotion);
              } else if (actionObj.action === 'SYNC_CART') {
                fetchCart();
              } else if (actionObj.action === 'OPEN_CART_DRAWER') {
                fetchCart();
                useStore.setState({ isCartOpen: true });
                setEmotion('CELEBRATING');
              } else if (actionObj.action === 'SYNC_WISHLIST') {
                fetchWishlist();
              } else if (actionObj.action === 'OPEN_WISHLIST_DRAWER') {
                fetchWishlist();
                useStore.setState({ isWishlistOpen: true });
              }
            } catch (err) {
              console.error('Error parsing UI action:', err);
            }
          } else if (eventType === 'token' && dataContent) {
            try {
              const tokenData = JSON.parse(dataContent);
              const tokenStr = tokenData.token || '';
              fullAssistantText += tokenStr;
              updateLastAssistantMessage(tokenStr);
            } catch {
              fullAssistantText += dataContent;
              updateLastAssistantMessage(dataContent);
            }
            setSpeechBubbleText(fullAssistantText);
          }
        }
      }

      setEmotion('CHARMING_COMPLIMENT');
    } catch (e) {
      console.error('Error streaming chat:', e);
      setSpeechBubbleText("Sir, I'm right here with you! Tell me what you'd like to check next!");
    } finally {
      setIsStreaming(false);
    }
  };

  const getEmotionBadge = () => {
    switch (emotion) {
      case 'HYPED':
        return { label: '🔥 Hero Material!', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40', emoji: '🤩' };
      case 'CELEBRATING':
        return { label: '🎉 Deal Closed!', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40', emoji: '🥳' };
      case 'ANALYTICAL':
        return { label: '🧐 Evaluating Specs', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40', emoji: '🧐' };
      case 'FIT_ADVISOR':
        return { label: '👟 Fit Secret', color: 'bg-purple-500/20 text-purple-300 border-purple-500/40', emoji: '💡' };
      default:
        return { label: '👑 Charming Sales Associate', color: 'bg-pink-500/20 text-pink-300 border-pink-500/40', emoji: '😎' };
    }
  };

  if (!mounted) return null;

  const badge = getEmotionBadge();

  return (
    <div className="fixed bottom-6 right-6 z-40 max-w-sm pointer-events-auto select-none">
      <div className="flex flex-col items-end space-y-3">
        {/* Floating Speech Bubble with Charming Sales Pitch */}
        <div className="relative glass-panel rounded-3xl p-4 border border-indigo-500/30 bg-surface/95 shadow-2xl space-y-2 max-w-[340px] animate-slide-up">
          {/* Emotion Badge */}
          <div className="flex items-center justify-between">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border ${badge.color} flex items-center gap-1`}>
              <span>{badge.emoji}</span>
              <span>{badge.label}</span>
            </span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-[10px] text-zinc-400 hover:text-white font-semibold transition-colors"
            >
              {isExpanded ? 'Hide Chat' : 'View Consultation Log'}
            </button>
          </div>

          {/* Speech Text */}
          <div
            className="text-xs text-zinc-200 leading-relaxed max-h-40 overflow-y-auto no-scrollbar font-medium"
            dangerouslySetInnerHTML={{
              __html: speechBubbleText
                .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="text-indigo-300 font-medium">$1</em>')
                .replace(/\n/g, '<br/>'),
            }}
          />

          {/* Quick Pitch Action Chips */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            <button
              onClick={() => handleSendMessage("Sir, why is this pair hero quality? Convince me!")}
              className="px-2 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 text-[10px] font-semibold transition-all"
            >
              ✨ "Why is this hero quality?"
            </button>
            <button
              onClick={() => handleSendMessage("Compare Nike Pegasus vs Adidas Ultraboost")}
              className="px-2 py-1 rounded-lg bg-pink-500/10 hover:bg-pink-500/20 text-pink-300 border border-pink-500/20 text-[10px] font-semibold transition-all"
            >
              ⚖️ "Compare top models"
            </button>
          </div>
        </div>

        {/* The Animated Salesperson Avatar & Voice Bar */}
        <div className="flex items-center gap-2.5">
          {/* Voice Input Mic */}
          <button
            onClick={toggleVoiceInput}
            className={`w-11 h-11 rounded-2xl flex items-center justify-center transition-all shadow-lg ${
              isListening
                ? 'bg-rose-500 text-white animate-pulse shadow-rose-500/50 scale-110'
                : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white border border-zinc-700'
            }`}
            title="Click to speak with your personal associate"
          >
            {isListening ? <Mic className="w-5 h-5" /> : <Mic className="w-4 h-4" />}
          </button>

          {/* Input Trigger Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2 bg-zinc-900/90 border border-surface-border focus-within:border-primary rounded-2xl px-3 py-2 shadow-lg"
          >
            <input
              type="text"
              placeholder={isListening ? "Listening to your voice, Sir..." : "Ask your personal sales associate..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isStreaming}
              className="w-44 bg-transparent text-xs text-white placeholder-zinc-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="w-7 h-7 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 disabled:opacity-30 text-white flex items-center justify-center transition-all shadow-md shadow-primary-glow"
            >
              <Send className="w-3 h-3" />
            </button>
          </form>

          {/* 3D Animated Avatar Head */}
          <div
            onClick={() => setIsExpanded(!isExpanded)}
            className="relative w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-pink-600 to-purple-500 p-0.5 shadow-xl shadow-primary-glow cursor-pointer transform hover:scale-105 transition-transform"
          >
            <div className="w-full h-full rounded-2xl bg-zinc-950 flex flex-col items-center justify-center relative overflow-hidden">
              <span className="text-2xl select-none animate-bounce">
                {badge.emoji}
              </span>
              <span className="absolute bottom-0 text-[8px] font-black text-indigo-300 uppercase tracking-tighter">
                SALES BOY
              </span>
            </div>
            {/* Pulsing Active Beacon */}
            <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-zinc-900 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Expanded Conversation History Drawer */}
      {isExpanded && (
        <div className="fixed bottom-24 right-6 w-96 h-[480px] glass-panel rounded-3xl border border-surface-border bg-surface/95 shadow-2xl flex flex-col overflow-hidden animate-slide-up z-50">
          <div className="p-4 border-b border-surface-border flex items-center justify-between bg-surface/90">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <h4 className="font-extrabold text-sm text-white">Your Personal Sales Associate</h4>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="w-7 h-7 rounded-full bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2 text-xs ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-primary to-indigo-600 text-white rounded-br-none'
                      : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-bl-none'
                  }`}
                >
                  <div
                    dangerouslySetInnerHTML={{
                      __html: msg.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/\n/g, '<br/>'),
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
