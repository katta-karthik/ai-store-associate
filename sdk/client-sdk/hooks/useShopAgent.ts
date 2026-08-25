'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage, EmotionType, ShopAgentConfig, UIAction } from '../types';

export function useShopAgent(config: ShopAgentConfig = {}) {
  const agentApiUrl = (config.agentApiUrl || process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001/api/v1').replace(/\/+$/, '');
  const [sessionId, setSessionId] = useState<string>(config.sessionId || 'shopper_session_001');
  const [shopperId, setShopperId] = useState<string>(config.shopperId || 'shopper_001');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome_msg',
      role: 'assistant',
      content: "👋 Hi! I'm your **ShopAgent AI Associate**. Ask me anything like *'I have flat feet and need a marathon shoe'* or *'Compare Pegasus vs Ultraboost'*, or click the 🎙️ mic to speak!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [emotion, setEmotion] = useState<EmotionType>('CHARMING_COMPLIMENT');
  const [speechBubbleText, setSpeechBubbleText] = useState("👋 **Namaste Sir!** I'm your personal sales associate walking with you today. What hero look or running shoes can I find for you?");
  const [comparisonProducts, setComparisonProducts] = useState<any[]>([]);
  const [isComparisonOpen, setIsComparisonOpen] = useState(false);
  const [researchReport, setResearchReport] = useState<any | null>(null);
  const [isResearchReportOpen, setIsResearchReportOpen] = useState(false);

  const recognitionRef = useRef<any>(null);

  // Initialize session from localStorage if in browser
  useEffect(() => {
    if (typeof window !== 'undefined') {
      let sid = config.sessionId || localStorage.getItem('shopagent_session_id');
      let uid = config.shopperId || localStorage.getItem('shopagent_shopper_id');
      if (!sid) {
        sid = `sess_${Math.random().toString(36).substring(2, 11)}`;
        localStorage.setItem('shopagent_session_id', sid);
      }
      if (!uid) {
        uid = `shopper_${Math.random().toString(36).substring(2, 11)}`;
        localStorage.setItem('shopagent_shopper_id', uid);
      }
      setSessionId(sid);
      setShopperId(uid);

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
            sendMessage(transcript);
          }
          setIsListening(false);
        };

        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
      }
    }
  }, [config.sessionId, config.shopperId]);

  const toggleVoiceInput = useCallback(() => {
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
  }, [isListening]);

  const sendMessage = useCallback(async (text: string) => {
    const query = text.trim();
    if (!query || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const assistantMsgId = `msg_a_${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);
    setSpeechBubbleText("Analyzing our best pairs for you, Sir...");
    setEmotion('ANALYTICAL');

    try {
      const response = await fetch(`${agentApiUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          shopper_id: shopperId,
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
              const actionObj: UIAction = JSON.parse(dataContent);
              if (actionObj.action === 'SET_FILTERS') {
                config.onFilterChange?.(actionObj.payload);
              } else if (actionObj.action === 'HIGHLIGHT_PRODUCTS') {
                config.onHighlightProducts?.(actionObj.payload?.product_ids || []);
              } else if (actionObj.action === 'OPEN_COMPARISON_MODAL') {
                if (actionObj.payload?.products) {
                  setComparisonProducts(actionObj.payload.products);
                  setIsComparisonOpen(true);
                }
              } else if (actionObj.action === 'SHOW_RESEARCH_REPORT') {
                setResearchReport(actionObj.payload);
                setIsResearchReportOpen(true);
              } else if (actionObj.action === 'AVATAR_GLIDE') {
                if (actionObj.payload?.emotion) setEmotion(actionObj.payload.emotion);
              } else if (actionObj.action === 'SYNC_CART' || actionObj.action === 'OPEN_CART_DRAWER') {
                config.onSyncCart?.();
                if (actionObj.action === 'OPEN_CART_DRAWER') setEmotion('CELEBRATING');
              } else if (actionObj.action === 'SYNC_WISHLIST' || actionObj.action === 'OPEN_WISHLIST_DRAWER') {
                config.onSyncWishlist?.();
              }
            } catch (err) {
              console.error('Error parsing UI action from ShopAgent:', err);
            }
          } else if (eventType === 'token' && dataContent) {
            let tokenStr = '';
            try {
              const tokenData = JSON.parse(dataContent);
              tokenStr = tokenData.token || '';
            } catch {
              tokenStr = dataContent;
            }
            fullAssistantText += tokenStr;
            setChatMessages((prev) => {
              const last = prev[prev.length - 1];
              if (last && last.role === 'assistant') {
                return [...prev.slice(0, -1), { ...last, content: fullAssistantText }];
              }
              return prev;
            });
            setSpeechBubbleText(fullAssistantText);
          }
        }
      }
      setEmotion('CHARMING_COMPLIMENT');
    } catch (err) {
      console.error('ShopAgent stream error:', err);
      setSpeechBubbleText("Sir, I'm right here with you! Tell me what you'd like to check next!");
    } finally {
      setIsStreaming(false);
    }
  }, [agentApiUrl, sessionId, shopperId, isStreaming, config]);

  return {
    sessionId,
    shopperId,
    chatMessages,
    isStreaming,
    isListening,
    emotion,
    setEmotion,
    speechBubbleText,
    setSpeechBubbleText,
    comparisonProducts,
    isComparisonOpen,
    setIsComparisonOpen,
    researchReport,
    isResearchReportOpen,
    setIsResearchReportOpen,
    sendMessage,
    toggleVoiceInput,
  };
}
