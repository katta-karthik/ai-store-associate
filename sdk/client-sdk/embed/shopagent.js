/**
 * ShopAgent Universal Standalone Web Component & Embed Script.
 * 
 * 100% Zero-Crash Shadow DOM Architecture.
 * Works on ANY E-Commerce Platform (Shopify, MERN, Spring Boot, PHP, WooCommerce, Next.js, HTML).
 */

(function () {
  'use strict';

  // Prevent multiple injections
  if (window.__SHOPAGENT_INITIALIZED__) return;
  window.__SHOPAGENT_INITIALIZED__ = true;

  // Read configuration from the script tag
  const currentScript = document.currentScript || (function() {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const API_BASE = currentScript?.getAttribute('data-api-url') || 'http://localhost:8001/api/v1';
  const STORE_ID = currentScript?.getAttribute('data-store-id') || 'merchant_store_default';

  // Session & Shopper Identification (Stored in browser localStorage)
  function getOrCreateSession() {
    let sid = localStorage.getItem('shopagent_session_id');
    let uid = localStorage.getItem('shopagent_shopper_id');
    if (!sid) {
      sid = 'sess_' + Math.random().toString(36).substring(2, 11);
      localStorage.setItem('shopagent_session_id', sid);
    }
    if (!uid) {
      uid = 'shopper_' + Math.random().toString(36).substring(2, 11);
      localStorage.setItem('shopagent_shopper_id', uid);
    }
    return { sessionId: sid, shopperId: uid };
  }

  const { sessionId, shopperId } = getOrCreateSession();

  // Create Custom Web Component with Shadow DOM
  class ShopAgentWidgetElement extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.isExpanded = false;
      this.isStreaming = false;
      this.isListening = false;
      this.messages = [
        {
          role: 'assistant',
          content: "👋 Hi! I'm your **ShopAgent AI Associate**. Ask me anything like *'I have flat feet and need a marathon shoe'* or *'Compare Pegasus vs Ultraboost'*, or click the 🎙️ mic to speak!",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ];
      this.speechText = "👋 **Namaste Sir!** I'm your personal sales associate walking with you today. What hero look or running shoes can I find for you?";
      this.recognition = null;
    }

    connectedCallback() {
      this.initVoiceRecognition();
      this.render();
      this.bindEvents();
      this.listenToProductHovers();
    }

    initVoiceRecognition() {
      try {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
          this.recognition = new SpeechRecognition();
          this.recognition.continuous = false;
          this.recognition.interimResults = false;
          this.recognition.lang = 'en-US';

          this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (transcript) {
              this.sendMessage(transcript);
            }
            this.isListening = false;
            this.updateVoiceButton();
          };

          this.recognition.onerror = () => {
            this.isListening = false;
            this.updateVoiceButton();
          };
          this.recognition.onend = () => {
            this.isListening = false;
            this.updateVoiceButton();
          };
        }
      } catch (e) {
        console.warn('[ShopAgent] Voice recognition initialization skipped.');
      }
    }

    listenToProductHovers() {
      try {
        window.addEventListener('mouseover', (e) => {
          const card = e.target.closest('[data-product-id]');
          if (card) {
            const title = card.getAttribute('data-product-title') || 'this shoe';
            this.setBubbleText(`✨ Sir, looking at the **${title}**? Absolute superstar quality! Shall I check your size?`);
          }
        });
      } catch (e) {}
    }

    setBubbleText(text) {
      this.speechText = text;
      const bubble = this.shadowRoot.querySelector('.speech-bubble-text');
      if (bubble) bubble.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    async sendMessage(query) {
      if (!query || this.isStreaming) return;

      this.messages.push({
        role: 'user',
        content: query,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
      this.messages.push({
        role: 'assistant',
        content: '',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });

      this.isStreaming = true;
      this.setBubbleText("Analyzing our best pairs for you, Sir...");
      this.renderMessages();

      try {
        const res = await fetch(`${API_BASE}/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            shopper_id: shopperId,
            message: query
          })
        });

        if (!res.body) throw new Error('No stream body');

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';

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
                // Dispatch standard decoupled custom event to host window
                window.dispatchEvent(new CustomEvent('shopagent:action', { detail: actionObj }));
                if (actionObj.action === 'SET_FILTERS') {
                  window.dispatchEvent(new CustomEvent('shopagent:filter-change', { detail: actionObj.payload }));
                } else if (actionObj.action === 'OPEN_CART_DRAWER' || actionObj.action === 'SYNC_CART') {
                  window.dispatchEvent(new CustomEvent('shopagent:cart-sync', { detail: actionObj.payload }));
                }
              } catch (err) {}
            } else if (eventType === 'token' && dataContent) {
              let tokenStr = '';
              try {
                const parsed = JSON.parse(dataContent);
                tokenStr = parsed.token || '';
              } catch {
                tokenStr = dataContent;
              }
              fullText += tokenStr;
              const lastMsg = this.messages[this.messages.length - 1];
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.content = fullText;
              }
              this.updateLastMessage(fullText);
              this.setBubbleText(fullText);
            }
          }
        }
      } catch (err) {
        console.warn('[ShopAgent] Stream error:', err);
        this.setBubbleText("Sir, I'm right here with you! Tell me what you'd like to check next!");
      } finally {
        this.isStreaming = false;
        this.renderMessages();
      }
    }

    toggleVoice() {
      if (!this.recognition) {
        alert('Voice recognition is not supported in this browser.');
        return;
      }
      if (this.isListening) {
        this.recognition.stop();
        this.isListening = false;
      } else {
        this.isListening = true;
        this.recognition.start();
      }
      this.updateVoiceButton();
    }

    updateVoiceButton() {
      const btn = this.shadowRoot.querySelector('#voice-btn');
      if (btn) {
        if (this.isListening) {
          btn.classList.add('listening');
        } else {
          btn.classList.remove('listening');
        }
      }
    }

    updateLastMessage(text) {
      const msgList = this.shadowRoot.querySelector('.chat-messages');
      if (msgList && msgList.lastElementChild) {
        const textElem = msgList.lastElementChild.querySelector('.msg-text');
        if (textElem) {
          textElem.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');
        }
      }
      const chatBody = this.shadowRoot.querySelector('.chat-messages');
      if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
    }

    renderMessages() {
      const msgContainer = this.shadowRoot.querySelector('.chat-messages');
      if (!msgContainer) return;

      msgContainer.innerHTML = this.messages.map(m => `
        <div class="message ${m.role}">
          ${m.role === 'assistant' ? '<div class="avatar-badge">✨</div>' : ''}
          <div class="bubble">
            <div class="msg-text">${m.content ? m.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') : (this.isStreaming ? 'Thinking...' : '')}</div>
            <div class="msg-time">${m.time}</div>
          </div>
        </div>
      `).join('');

      msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    bindEvents() {
      const toggleBtn = this.shadowRoot.querySelector('#toggle-btn');
      if (toggleBtn) {
        toggleBtn.onclick = () => {
          this.isExpanded = !this.isExpanded;
          this.render();
          this.bindEvents();
        };
      }

      const closeBtn = this.shadowRoot.querySelector('#close-btn');
      if (closeBtn) {
        closeBtn.onclick = () => {
          this.isExpanded = false;
          this.render();
          this.bindEvents();
        };
      }

      const voiceBtn = this.shadowRoot.querySelector('#voice-btn');
      if (voiceBtn) {
        voiceBtn.onclick = () => this.toggleVoice();
      }

      const form = this.shadowRoot.querySelector('#chat-form');
      if (form) {
        form.onsubmit = (e) => {
          e.preventDefault();
          const input = this.shadowRoot.querySelector('#chat-input');
          if (input && input.value.trim()) {
            this.sendMessage(input.value.trim());
            input.value = '';
          }
        };
      }

      const promptBtns = this.shadowRoot.querySelectorAll('.chip-btn');
      promptBtns.forEach(btn => {
        btn.onclick = () => {
          const q = btn.getAttribute('data-query');
          if (q) this.sendMessage(q);
        };
      });
    }

    render() {
      this.shadowRoot.innerHTML = `
        <style>
          :host {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 2147483647;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            pointer-events: none;
            user-select: none;
            -webkit-user-select: none;
          }

          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }

          .widget-container {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
          }

          /* Floating Speech Bubble */
          .speech-bubble {
            pointer-events: auto;
            max-width: 320px;
            margin-bottom: 12px;
            background: rgba(9, 9, 11, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 18px;
            padding: 14px;
            color: #ffffff;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            position: relative;
            animation: fadeIn 0.3s ease;
          }

          .speech-bubble-header {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            color: #818cf8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
          }

          .live-badge {
            margin-left: auto;
            font-size: 9px;
            padding: 2px 6px;
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border-radius: 4px;
          }

          .speech-bubble-text {
            font-size: 12px;
            color: #e4e4e7;
            line-height: 1.45;
          }

          .speech-bubble::after {
            content: '';
            position: absolute;
            bottom: -6px;
            right: 32px;
            width: 12px;
            height: 12px;
            background: rgba(9, 9, 11, 0.95);
            border-right: 1px solid rgba(99, 102, 241, 0.35);
            border-bottom: 1px solid rgba(99, 102, 241, 0.35);
            transform: rotate(45deg);
          }

          /* Floating Launcher Button */
          .launcher-btn {
            pointer-events: auto;
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            padding: 2px;
            cursor: pointer;
            border: none;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.45);
            transition: transform 0.2s, box-shadow 0.2s;
          }

          .launcher-btn:hover {
            transform: scale(1.06);
            box-shadow: 0 14px 30px rgba(99, 102, 241, 0.6);
          }

          .launcher-inner {
            width: 100%;
            height: 100%;
            background: #09090b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
          }

          .launcher-icon {
            font-size: 24px;
          }

          .live-dot {
            position: absolute;
            top: 4px;
            right: 4px;
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            border: 2px solid #09090b;
          }

          /* Chat Drawer */
          .chat-drawer {
            pointer-events: auto;
            width: 360px;
            height: 480px;
            background: rgba(9, 9, 11, 0.97);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin-bottom: 12px;
            animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
          }

          .chat-header {
            padding: 12px 16px;
            background: rgba(24, 24, 27, 0.7);
            border-bottom: 1px solid #27272a;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }

          .chat-title {
            font-size: 13px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 6px;
          }

          .chat-subtitle {
            font-size: 10px;
            color: #a1a1aa;
          }

          .close-btn {
            background: transparent;
            border: none;
            color: #a1a1aa;
            cursor: pointer;
            font-size: 16px;
            padding: 4px 8px;
            border-radius: 6px;
          }

          .close-btn:hover {
            color: #ffffff;
            background: #27272a;
          }

          .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
          }

          .message {
            display: flex;
            gap: 8px;
            max-width: 85%;
          }

          .message.user {
            align-self: flex-end;
          }

          .message.assistant {
            align-self: flex-start;
          }

          .avatar-badge {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.25);
            border: 1px solid rgba(99, 102, 241, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            flex-shrink: 0;
          }

          .bubble {
            padding: 9px 13px;
            border-radius: 14px;
            font-size: 12px;
            line-height: 1.4;
          }

          .message.user .bubble {
            background: #4f46e5;
            color: #ffffff;
            border-bottom-right-radius: 2px;
          }

          .message.assistant .bubble {
            background: #18181b;
            border: 1px solid #27272a;
            color: #e4e4e7;
            border-bottom-left-radius: 2px;
          }

          .msg-time {
            font-size: 9px;
            color: #71717a;
            margin-top: 4px;
            text-align: right;
          }

          .chips-row {
            padding: 6px 12px;
            display: flex;
            gap: 6px;
            overflow-x: auto;
            border-top: 1px solid rgba(39, 39, 42, 0.6);
            background: rgba(18, 18, 20, 0.4);
          }

          .chip-btn {
            white-space: nowrap;
            padding: 4px 10px;
            border-radius: 20px;
            background: #18181b;
            border: 1px solid #3f3f46;
            color: #d4d4d8;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
          }

          .chip-btn:hover {
            background: rgba(99, 102, 241, 0.3);
            border-color: #6366f1;
            color: #ffffff;
          }

          .chat-input-bar {
            padding: 10px 12px;
            border-top: 1px solid #27272a;
            display: flex;
            gap: 8px;
            background: #121215;
          }

          .voice-btn {
            background: #18181b;
            border: 1px solid #3f3f46;
            color: #e4e4e7;
            padding: 8px 10px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
          }

          .voice-btn.listening {
            background: rgba(239, 68, 68, 0.25);
            border-color: #ef4444;
            color: #ef4444;
            animation: pulse 1s infinite;
          }

          .input-field {
            flex: 1;
            background: #09090b;
            border: 1px solid #3f3f46;
            border-radius: 10px;
            padding: 8px 12px;
            color: #ffffff;
            font-size: 12px;
            outline: none;
          }

          .input-field:focus {
            border-color: #6366f1;
          }

          .send-btn {
            background: #4f46e5;
            border: none;
            color: #ffffff;
            padding: 8px 12px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
          }

          .send-btn:hover {
            background: #4338ca;
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes slideUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
          }
        </style>

        <div class="widget-container">
          ${!this.isExpanded ? `
            <div class="speech-bubble">
              <div class="speech-bubble-header">
                <span>✨ ShopAgent Associate</span>
                <span class="live-badge">LIVE</span>
              </div>
              <div class="speech-bubble-text">
                ${this.speechText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
              </div>
            </div>
          ` : ''}

          ${this.isExpanded ? `
            <div class="chat-drawer">
              <div class="chat-header">
                <div>
                  <div class="chat-title">✨ ShopAgent Associate</div>
                  <div class="chat-subtitle">Walkalong Retail Specialist</div>
                </div>
                <button class="close-btn" id="close-btn">✕</button>
              </div>

              <div class="chat-messages"></div>

              <div class="chips-row">
                <button class="chip-btn" data-query="Show marathon road shoes under 10000">🏃 Marathon Shoes</button>
                <button class="chip-btn" data-query="Compare Pegasus vs Ultraboost">⚖️ Compare Pairs</button>
              </div>

              <form class="chat-input-bar" id="chat-form">
                <button type="button" class="voice-btn" id="voice-btn" title="Voice Input">🎙️</button>
                <input type="text" class="input-field" id="chat-input" placeholder="Ask or speak..." autocomplete="off" />
                <button type="submit" class="send-btn">Send</button>
              </form>
            </div>
          ` : ''}

          <button class="launcher-btn" id="toggle-btn" aria-label="Open ShopAgent">
            <div class="launcher-inner">
              <span class="launcher-icon">✨</span>
              <div class="live-dot"></div>
            </div>
          </button>
        </div>
      `;

      if (this.isExpanded) {
        this.renderMessages();
      }
    }
  }

  // Register Custom Web Component
  if (!customElements.get('shopagent-widget')) {
    customElements.define('shopagent-widget', ShopAgentWidgetElement);
  }

  // Auto-inject the component into host webpage body
  function autoMountWidget() {
    if (!document.querySelector('shopagent-widget')) {
      const widget = document.createElement('shopagent-widget');
      document.body.appendChild(widget);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoMountWidget);
  } else {
    autoMountWidget();
  }
})();
