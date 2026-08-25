/**
 * ShopAgent Universal Standalone Web Component & Embed Script.
 * 
 * 100% Zero-Crash Spatial Sales Associate with Shadow DOM Encapsulation.
 * Works on ANY E-Commerce Platform (Shopify, MERN, Spring Boot, PHP, WooCommerce, Next.js, HTML).
 */

(function () {
  'use strict';

  // Prevent multiple injections
  if (window.__SHOPAGENT_INITIALIZED__) return;
  window.__SHOPAGENT_INITIALIZED__ = true;

  // Read configuration from current script tag
  const currentScript = document.currentScript || (function() {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const API_BASE = currentScript?.getAttribute('data-api-url') || 'http://localhost:8001/api/v1';
  const STORE_ID = currentScript?.getAttribute('data-store-id') || 'merchant_store_default';

  // Session & Shopper Identification
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
      this.emotion = 'CHARMING_COMPLIMENT';
      this.spatialTarget = null;
      this.selectedSize = '10';
      this.messages = [
        {
          role: 'assistant',
          content: "👋 Namaste Sir! I'm your **ShopAgent Sales Associate** walking beside you today! As you browse, I'll glide alongside each shoe and give you my honest hero review. Tell me what style you love or click 🎙️ to speak!",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ];
      this.speechText = "👋 **Namaste Sir!** I'm your dedicated sales associate walking with you. Hover or tap any pair and I'll show you its hero features!";
      this.recognition = null;
    }

    connectedCallback() {
      this.initVoiceRecognition();
      this.render();
      this.bindEvents();
      this.listenToProductInteractions();
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

    listenToProductInteractions() {
      try {
        window.addEventListener('mouseover', (e) => {
          const card = e.target.closest('[data-product-id]');
          if (card && !this.isExpanded) {
            const prodId = card.getAttribute('data-product-id');
            const title = card.getAttribute('data-product-title') || 'this shoe';
            const price = card.getAttribute('data-product-price') || '';

            const rect = card.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            let dockLeft = rect.right + 16;
            if (rect.right + 340 > viewportWidth) {
              dockLeft = Math.max(16, rect.left - 340);
            }

            const dockTop = Math.max(80, Math.min(rect.top + 10, viewportHeight - 260));

            this.spatialTarget = {
              id: prodId,
              title: title,
              price: price,
              top: dockTop,
              left: dockLeft
            };
            this.emotion = 'HYPED';
            this.speechText = `✨ Sir! Look at the **${title}**! In this pair, you will look 100% like a movie hero, haha! Shall I pack your size?`;
            this.render();
            this.bindEvents();
          }
        });
      } catch (e) {}
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
      this.speechText = "Analyzing our best pairs for you, Sir...";
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
                window.dispatchEvent(new CustomEvent('shopagent:action', { detail: actionObj }));
                if (actionObj.action === 'SET_FILTERS') {
                  window.dispatchEvent(new CustomEvent('shopagent:filter-change', { detail: actionObj.payload }));
                } else if (actionObj.action === 'SYNC_CART' || actionObj.action === 'OPEN_CART_DRAWER') {
                  window.dispatchEvent(new CustomEvent('shopagent:cart-sync', { detail: actionObj.payload }));
                } else if (actionObj.action === 'AVATAR_GLIDE') {
                  const targetCard = document.querySelector(`[data-product-id="${actionObj.payload.target_id}"]`);
                  if (targetCard) {
                    const rect = targetCard.getBoundingClientRect();
                    this.spatialTarget = {
                      id: actionObj.payload.target_id,
                      title: targetCard.getAttribute('data-product-title') || 'Featured Hero',
                      top: Math.max(80, rect.top + 10),
                      left: Math.max(16, rect.right + 16)
                    };
                    this.render();
                    this.bindEvents();
                  }
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
            }
          }
        }
      } catch (err) {
        console.warn('[ShopAgent] Stream error:', err);
      } finally {
        this.isStreaming = false;
        this.renderMessages();
      }
    }

    toggleVoice() {
      if (!this.recognition) {
        alert('Voice shopping recognition is not supported in this browser.');
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
          this.spatialTarget = null;
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

      const closeSpatialBtn = this.shadowRoot.querySelector('#close-spatial-btn');
      if (closeSpatialBtn) {
        closeSpatialBtn.onclick = () => {
          this.spatialTarget = null;
          this.render();
          this.bindEvents();
        };
      }

      const sizeBtns = this.shadowRoot.querySelectorAll('.size-pill');
      sizeBtns.forEach(btn => {
        btn.onclick = () => {
          this.selectedSize = btn.getAttribute('data-size') || '10';
          this.render();
          this.bindEvents();
        };
      });

      const packBagBtn = this.shadowRoot.querySelector('#pack-bag-btn');
      if (packBagBtn && this.spatialTarget) {
        packBagBtn.onclick = () => {
          window.dispatchEvent(new CustomEvent('shopagent:add-to-cart', {
            detail: {
              productId: this.spatialTarget.id,
              variantId: `var_${this.spatialTarget.id}_${this.selectedSize}`,
              quantity: 1
            }
          }));
          packBagBtn.innerText = 'Packed in Your Bag! 🎉';
          packBagBtn.style.background = '#10b981';
          setTimeout(() => {
            this.spatialTarget = null;
            this.render();
            this.bindEvents();
          }, 1500);
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
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }

          :host {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            user-select: none;
            -webkit-user-select: none;
          }

          /* Spatial Floating Pitch Callout Attached to Product */
          .spatial-box {
            position: fixed;
            z-index: 2147483646;
            width: 320px;
            background: rgba(9, 9, 11, 0.96);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(236, 72, 153, 0.45);
            border-radius: 20px;
            padding: 14px;
            color: #ffffff;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
            animation: popIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          }

          .spatial-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
          }

          .spatial-badge {
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.5px;
            padding: 2px 8px;
            border-radius: 20px;
            background: linear-gradient(135deg, #ec4899, #6366f1);
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 4px;
          }

          .close-mini-btn {
            background: transparent;
            border: none;
            color: #a1a1aa;
            font-size: 14px;
            cursor: pointer;
          }

          .spatial-quote {
            font-size: 12px;
            line-height: 1.45;
            color: #f4f4f5;
            border-left: 2px solid #6366f1;
            padding-left: 8px;
            margin-bottom: 10px;
          }

          .size-row {
            background: rgba(24, 24, 27, 0.8);
            border-radius: 12px;
            padding: 8px;
            margin-bottom: 10px;
          }

          .size-label {
            font-size: 10px;
            color: #a1a1aa;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
          }

          .size-pills {
            display: flex;
            gap: 6px;
          }

          .size-pill {
            flex: 1;
            padding: 4px;
            font-size: 11px;
            font-weight: 700;
            background: #27272a;
            border: 1px solid #3f3f46;
            color: #ffffff;
            border-radius: 6px;
            cursor: pointer;
            text-align: center;
          }

          .size-pill.active {
            background: #4f46e5;
            border-color: #818cf8;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
          }

          .pack-btn {
            width: 100%;
            padding: 9px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            background: linear-gradient(135deg, #4f46e5, #ec4899);
            border: none;
            color: #ffffff;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: transform 0.2s;
          }

          .pack-btn:hover {
            transform: scale(1.02);
          }

          /* Bottom Right Dock */
          .dock-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 2147483647;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
          }

          .idle-bubble {
            max-width: 300px;
            background: rgba(9, 9, 11, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 18px;
            padding: 12px 14px;
            color: #ffffff;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            margin-bottom: 12px;
            position: relative;
            animation: fadeIn 0.3s ease;
          }

          .idle-bubble-header {
            font-size: 11px;
            font-weight: 700;
            color: #818cf8;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
          }

          .idle-bubble-text {
            font-size: 12px;
            color: #e4e4e7;
            line-height: 1.4;
          }

          .idle-bubble::after {
            content: '';
            position: absolute;
            bottom: -6px;
            right: 28px;
            width: 12px;
            height: 12px;
            background: rgba(9, 9, 11, 0.95);
            border-right: 1px solid rgba(99, 102, 241, 0.35);
            border-bottom: 1px solid rgba(99, 102, 241, 0.35);
            transform: rotate(45deg);
          }

          .launcher-btn {
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            padding: 2px;
            cursor: pointer;
            border: none;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.45);
            transition: transform 0.2s;
          }

          .launcher-btn:hover {
            transform: scale(1.06);
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

          /* Full Chat Drawer */
          .chat-drawer {
            width: 360px;
            height: 480px;
            background: rgba(9, 9, 11, 0.98);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin-bottom: 12px;
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
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
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
          }

          .message.assistant .bubble {
            background: #18181b;
            border: 1px solid #27272a;
            color: #e4e4e7;
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
            border-top: 1px solid #27272a;
            background: #121215;
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
          }

          .voice-btn.listening {
            background: rgba(239, 68, 68, 0.3);
            border-color: #ef4444;
            color: #ef4444;
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

          @keyframes popIn {
            from { opacity: 0; transform: scale(0.92) translateY(10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
          }
        </style>

        ${this.spatialTarget && !this.isExpanded ? `
          <div class="spatial-box" style="top: ${this.spatialTarget.top}px; left: ${this.spatialTarget.left}px;">
            <div class="spatial-header">
              <div class="spatial-badge">
                <span>🤩</span>
                <span>HERO PITCH</span>
              </div>
              <button class="close-mini-btn" id="close-spatial-btn">✕</button>
            </div>
            <div class="spatial-quote">
              ${this.speechText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
            </div>
            <div class="size-row">
              <div class="size-label">
                <span>Select UK Size:</span>
                <span style="color:#818cf8; font-weight:700;">Size UK ${this.selectedSize}</span>
              </div>
              <div class="size-pills">
                ${['8', '9', '10', '11'].map(sz => `
                  <button class="size-pill ${this.selectedSize === sz ? 'active' : ''}" data-size="${sz}">
                    ${sz === '10' ? `⭐ ${sz}` : sz}
                  </button>
                `).join('')}
              </div>
            </div>
            <button class="pack-btn" id="pack-bag-btn">
              🛍️ Pack in my Bag (Size UK ${this.selectedSize})
            </button>
          </div>
        ` : ''}

        <div class="dock-container">
          ${!this.spatialTarget && !this.isExpanded ? `
            <div class="idle-bubble">
              <div class="idle-bubble-header">
                <span>✨ ShopAgent Walkalong Associate</span>
              </div>
              <div class="idle-bubble-text">
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
              <span>${this.emotion === 'HYPED' ? '🤩' : this.emotion === 'CELEBRATING' ? '🎉' : '✨'}</span>
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

  // Register Custom Element
  if (!customElements.get('shopagent-widget')) {
    customElements.define('shopagent-widget', ShopAgentWidgetElement);
  }

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
