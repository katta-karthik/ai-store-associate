'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, X, Bot, User, Loader2 } from 'lucide-react';
import { useStore } from '@/store/useStore';

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001/api/v1';

export const ChatWidget: React.FC = () => {
  const {
    isChatOpen,
    toggleChat,
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const quickPrompts = [
    '🔬 Flat feet marathon training shoe',
    '⚖️ Compare Pegasus vs Ultraboost',
    '🛒 Add Nike Pegasus size 10 to cart',
    '💖 Save Salomon to wishlist',
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || input.trim();
    if (!query || isStreaming) return;

    setInput('');
    // 1. Add User Message
    addChatMessage({ role: 'user', content: query });

    // 2. Prepare Assistant Placeholder
    addChatMessage({ role: 'assistant', content: '' });
    setIsStreaming(true);

    try {
      // Connect to SSE stream
      const response = await fetch(`${AGENT_API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: 'shopper_session_001',
          message: query,
        }),
      });

      if (!response.body) throw new Error('No stream body received');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

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

          if (eventType === 'ui_action' && dataContent) {
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
              } else if (actionObj.action === 'SYNC_CART') {
                fetchCart();
              } else if (actionObj.action === 'OPEN_CART_DRAWER') {
                fetchCart();
                useStore.setState({ isCartOpen: true });
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
              updateLastAssistantMessage(tokenData.token || '');
            } catch {
              updateLastAssistantMessage(dataContent);
            }
          }
        }
      }
    } catch (e) {
      console.error('Error streaming chat:', e);
      updateLastAssistantMessage("Sorry, I encountered an issue connecting to the store. Please try again!");
    } finally {
      setIsStreaming(false);
    }
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 w-[92vw] sm:w-[420px] h-[600px] glass-panel rounded-3xl border border-surface-border shadow-2xl flex flex-col overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="px-5 py-4 border-b border-surface-border bg-surface/90 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center shadow-md shadow-primary-glow">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-sm text-white">AI Store Associate</h3>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <p className="text-[11px] text-zinc-400">Deep research, live filter sync & cart manager</p>
          </div>
        </div>
        <button
          onClick={toggleChat}
          className="w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {chatMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 text-xs leading-relaxed ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center flex-shrink-0 text-indigo-300">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[82%] rounded-2xl px-4 py-3 shadow-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-primary to-indigo-600 text-white rounded-br-none shadow-primary-glow'
                  : 'bg-surface/90 border border-surface-border text-zinc-200 rounded-bl-none'
              }`}
            >
              {msg.content ? (
                <div
                  className="prose prose-invert prose-xs max-w-none space-y-1.5"
                  dangerouslySetInnerHTML={{
                    __html: msg.content
                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*(.*?)\*/g, '<em>$1</em>')
                      .replace(/\n/g, '<br/>'),
                  }}
                />
              ) : (
                <div className="flex items-center gap-1.5 py-1 text-zinc-400">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" />
                  <span>Synthesizing multi-constraint research...</span>
                </div>
              )}
              <span className="block text-[9px] text-zinc-500 text-right mt-1.5">{msg.timestamp}</span>
            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center flex-shrink-0 text-zinc-300">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="px-4 py-2 border-t border-surface-border bg-surface/50 overflow-x-auto flex gap-2 no-scrollbar">
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(prompt.substring(2).trim())}
            disabled={isStreaming}
            className="whitespace-nowrap px-2.5 py-1 rounded-lg bg-zinc-800/80 hover:bg-indigo-600/20 text-zinc-400 hover:text-indigo-300 border border-zinc-700/50 hover:border-indigo-500/40 text-[11px] font-medium transition-all"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-surface-border bg-surface/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2 bg-zinc-900/90 border border-surface-border focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 rounded-2xl px-3 py-2 transition-all"
        >
          <input
            type="text"
            placeholder="Ask complex questions: 'Flat feet marathon shoe under ₹10k'..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isStreaming}
            className="flex-1 bg-transparent text-xs text-white placeholder-zinc-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="w-8 h-8 rounded-xl bg-gradient-to-r from-primary to-accent hover:opacity-90 disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-md shadow-primary-glow"
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
