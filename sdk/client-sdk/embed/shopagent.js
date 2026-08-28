/**
 * ShopAgent Universal Standalone Web Component & Embed Script.
 *
 * Zero-Footprint Intercom-Style AI Sales Associate.
 * Shadow DOM Encapsulated — works on ANY E-Commerce Platform.
 *
 * DESIGN PRINCIPLE: The merchant's page is NEVER modified.
 * Our entire footprint = one 56px FAB circle + expandable 360×480px chat panel.
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
      this.isOpen = false;
      this.isStreaming = false;
      this.isListening = false;
      this.emotion = 'CHARMING_COMPLIMENT';
      this.hasUnread = true;
      this.showToast = true;
      this.messages = [
        {
          role: 'assistant',
          content: "👋 Namaste Sir! I'm your **ShopAgent Sales Associate**. Tell me what style you love, your shoe size, or budget and I'll find the perfect pair!",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ];
      this.recognition = null;
    }

    connectedCallback() {
      this.initVoiceRecognition();
      this.render();
      this.bindEvents();
      // Auto-dismiss toast after 4 seconds
      setTimeout(() => {
        this.showToast = false;
        this.updateToast();
      }, 4000);
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

    async sendMessage(query) {
      if (!query || this.isStreaming) return;

      // Auto-open panel
      if (!this.isOpen) {
        this.isOpen = true;
        this.render();
        this.bindEvents();
      }

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
                // Dispatch events for host page to optionally listen to
                window.dispatchEvent(new CustomEvent('shopagent:action', { detail: actionObj }));
                if (actionObj.action === 'SET_FILTERS') {
                  window.dispatchEvent(new CustomEvent('shopagent:filter-change', { detail: actionObj.payload }));
                } else if (actionObj.action === 'SYNC_CART' || actionObj.action === 'OPEN_CART_DRAWER') {
                  window.dispatchEvent(new CustomEvent('shopagent:cart-sync', { detail: actionObj.payload }));
                }
              } catch (err) {}
            } else if (eventType === 'emotion' && dataContent) {
              try {
                const emoObj = JSON.parse(dataContent);
                if (emoObj.emotion) {
                  this.emotion = emoObj.emotion;
                  this.updateFabEmoji();
                }
              } catch {}
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
        btn.className = this.isListening ? 'voice-btn listening' : 'voice-btn';
      }
    }

    updateFabEmoji() {
      const emoji = this.shadowRoot.querySelector('#fab-emoji');
      if (emoji) {
        emoji.textContent = this.getEmoji();
      }
    }

    updateToast() {
      const toast = this.shadowRoot.querySelector('.toast');
      if (toast) {
        toast.style.display = this.showToast && !this.isOpen ? 'block' : 'none';
      }
    }

    updateLastMessage(text) {
      const msgList = this.shadowRoot.querySelector('.chat-messages');
      if (msgList && msgList.lastElementChild) {
        const textElem = msgList.lastElementChild.querySelector('.msg-text');
        if (textElem) {
          textElem.innerHTML = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br/>');
        }
      }
      if (msgList) msgList.scrollTop = msgList.scrollHeight;
    }

    renderMessages() {
      const msgContainer = this.shadowRoot.querySelector('.chat-messages');
      if (!msgContainer) return;

      msgContainer.innerHTML = this.messages.map(m => `
        <div class="message ${m.role}">
          ${m.role === 'assistant' ? '<div class="avatar-badge">✨</div>' : ''}
          <div class="bubble">
            <div class="msg-text">${m.content
              ? m.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br/>')
              : (this.isStreaming ? '<span class="typing">Thinking...</span>' : '')
            }</div>
            <div class="msg-time">${m.time}</div>
          </div>
        </div>
      `).join('');

      msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    getEmoji() {
      if (this.emotion === 'HYPED') return '🤩';
      if (this.emotion === 'CELEBRATING') return '🎉';
      if (this.emotion === 'ANALYTICAL') return '🔬';
      return '👑';
    }

    bindEvents() {
      // FAB toggle
      const fab = this.shadowRoot.querySelector('#fab-btn');
      if (fab) {
        fab.onclick = () => {
          this.isOpen = !this.isOpen;
          this.hasUnread = false;
          this.showToast = false;
          this.render();
          this.bindEvents();
          if (this.isOpen) this.renderMessages();
        };
      }

      // Close button inside panel
      const closeBtn = this.shadowRoot.querySelector('#close-btn');
      if (closeBtn) {
        closeBtn.onclick = () => {
          this.isOpen = false;
          this.render();
          this.bindEvents();
        };
      }

      // Voice
      const voiceBtn = this.shadowRoot.querySelector('#voice-btn');
      if (voiceBtn) {
        voiceBtn.onclick = () => this.toggleVoice();
      }

      // Chat form
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

      // Quick chips
      const chips = this.shadowRoot.querySelectorAll('.chip-btn');
      chips.forEach(btn => {
        btn.onclick = () => {
          const q = btn.getAttribute('data-query');
          if (q) this.sendMessage(q);
        };
      });
    }

    render() {
      this.shadowRoot.innerHTML = `
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }

          :host {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            user-select: none;
            -webkit-user-select: none;
          }

          /* ── Container: fixed bottom-right, out of document flow ── */
          .widget-root {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 2147483647;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 12px;
          }

          /* ── Expandable Chat Panel ── */
          .chat-panel {
            width: 360px;
            height: 480px;
            background: rgba(9, 9, 11, 0.98);
            backdrop-filter: blur(24px);
            border: 1px solid #27272a;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
          }

          .panel-header {
            padding: 12px 16px;
            background: rgba(24, 24, 27, 0.7);
            border-bottom: 1px solid #27272a;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }

          .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .header-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #ec4899);
            padding: 2px;
            flex-shrink: 0;
          }

          .header-avatar-inner {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: #09090b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
          }

          .header-title { font-size: 13px; font-weight: 700; color: #fff; }
          .header-subtitle { font-size: 10px; color: #a1a1aa; display: flex; align-items: center; gap: 4px; }
          .online-dot { width: 5px; height: 5px; border-radius: 50%; background: #10b981; display: inline-block; }

          .close-btn {
            background: #18181b;
            border: 1px solid #27272a;
            color: #a1a1aa;
            cursor: pointer;
            font-size: 14px;
            width: 28px;
            height: 28px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .close-btn:hover { color: #fff; background: #27272a; }

          /* Personalization strip inside panel */
          .prefs-strip {
            padding: 6px 12px;
            border-bottom: 1px solid rgba(39, 39, 42, 0.5);
            background: rgba(24, 24, 27, 0.4);
            display: flex;
            gap: 6px;
            overflow-x: auto;
          }
          .prefs-strip::-webkit-scrollbar { display: none; }

          .pref-badge {
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 600;
            white-space: nowrap;
            flex-shrink: 0;
          }

          .pref-size { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); color: #a5b4fc; }
          .pref-budget { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #6ee7b7; }
          .pref-brand { background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.2); color: #f9a8d4; }

          /* Chat messages */
          .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            scrollbar-width: thin;
            scrollbar-color: #27272a transparent;
          }

          .message { display: flex; gap: 8px; max-width: 88%; }
          .message.user { align-self: flex-end; }
          .message.assistant { align-self: flex-start; }

          .avatar-badge {
            width: 20px; height: 20px; border-radius: 50%;
            background: rgba(99, 102, 241, 0.2);
            display: flex; align-items: center; justify-content: center;
            font-size: 10px; flex-shrink: 0; margin-top: 2px;
          }

          .bubble {
            padding: 8px 12px;
            border-radius: 14px;
            font-size: 12px;
            line-height: 1.45;
          }

          .message.user .bubble {
            background: #4f46e5;
            color: #fff;
            border-bottom-right-radius: 4px;
          }

          .message.assistant .bubble {
            background: #18181b;
            border: 1px solid #27272a;
            color: #e4e4e7;
            border-bottom-left-radius: 4px;
          }

          .msg-time { font-size: 9px; color: #71717a; margin-top: 3px; text-align: right; }
          .typing { color: #71717a; font-style: italic; }

          /* Quick suggestion chips */
          .chips-row {
            padding: 6px 10px;
            display: flex;
            gap: 6px;
            overflow-x: auto;
            border-top: 1px solid #27272a;
            background: #121215;
          }
          .chips-row::-webkit-scrollbar { display: none; }

          .chip-btn {
            white-space: nowrap;
            padding: 4px 10px;
            border-radius: 20px;
            background: #18181b;
            border: 1px solid #3f3f46;
            color: #a1a1aa;
            font-size: 10px;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.15s;
          }
          .chip-btn:hover { color: #fff; border-color: #6366f1; }

          /* Input bar */
          .input-bar {
            padding: 10px 12px;
            border-top: 1px solid #27272a;
            display: flex;
            gap: 8px;
            background: #121215;
          }

          .voice-btn {
            background: #18181b;
            border: 1px solid #3f3f46;
            color: #a1a1aa;
            padding: 8px 10px;
            border-radius: 10px;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.15s;
          }
          .voice-btn:hover { color: #fff; }
          .voice-btn.listening {
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            color: #ef4444;
            animation: pulse 1.5s infinite;
          }

          .input-field {
            flex: 1;
            background: #09090b;
            border: 1px solid #3f3f46;
            border-radius: 10px;
            padding: 8px 12px;
            color: #fff;
            font-size: 12px;
            outline: none;
            transition: border-color 0.15s;
          }
          .input-field:focus { border-color: #6366f1; }

          .send-btn {
            background: #4f46e5;
            border: none;
            color: #fff;
            padding: 8px 12px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
            flex-shrink: 0;
            transition: background 0.15s;
          }
          .send-btn:hover { background: #4338ca; }

          /* ── Auto-Dismiss Toast ── */
          .toast {
            max-width: 220px;
            padding: 8px 12px;
            border-radius: 12px;
            background: rgba(9, 9, 11, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid #27272a;
            color: #e4e4e7;
            font-size: 11px;
            line-height: 1.4;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
            cursor: pointer;
            animation: fadeIn 0.3s ease;
          }
          .toast-label {
            font-size: 10px;
            font-weight: 700;
            color: #818cf8;
            margin-bottom: 2px;
          }

          /* ── FAB Launcher ── */
          .fab-btn {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            padding: 2px;
            cursor: pointer;
            border: none;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            transition: transform 0.2s;
            position: relative;
          }
          .fab-btn:hover { transform: scale(1.06); }
          .fab-btn:active { transform: scale(0.95); }

          .fab-inner {
            width: 100%;
            height: 100%;
            background: #09090b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
          }

          .live-dot {
            position: absolute;
            top: 0;
            right: 0;
            width: 12px;
            height: 12px;
            background: #10b981;
            border-radius: 50%;
            border: 2.5px solid #09090b;
            animation: pulse 2s infinite;
          }

          .unread-badge {
            position: absolute;
            top: -4px;
            left: -4px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #ef4444;
            color: #fff;
            font-size: 10px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2.5px solid #09090b;
          }

          @keyframes slideUp {
            from { opacity: 0; transform: translateY(16px) scale(0.96); }
            to { opacity: 1; transform: translateY(0) scale(1); }
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        </style>

        <div class="widget-root">
          ${this.isOpen ? `
            <div class="chat-panel">
              <!-- Header -->
              <div class="panel-header">
                <div class="header-left">
                  <div class="header-avatar">
                    <div class="header-avatar-inner">${this.getEmoji()}</div>
                  </div>
                  <div>
                    <div class="header-title">AI Sales Associate</div>
                    <div class="header-subtitle">
                      <span class="online-dot"></span>
                      Online · Remembers your preferences
                    </div>
                  </div>
                </div>
                <button class="close-btn" id="close-btn">✕</button>
              </div>

              <!-- Personalization inside panel -->
              <div class="prefs-strip">
                <span class="pref-badge pref-size">👟 UK 10</span>
                <span class="pref-badge pref-budget">💰 &lt;₹8K</span>
                <span class="pref-badge pref-brand">🏷️ Nike</span>
              </div>

              <!-- Messages -->
              <div class="chat-messages"></div>

              <!-- Quick chips -->
              <div class="chips-row">
                <button class="chip-btn" data-query="Show running shoes under 8000 in size 10">🏃 Running &lt;₹8K</button>
                <button class="chip-btn" data-query="Compare Pegasus vs Ultraboost">⚖️ Compare</button>
                <button class="chip-btn" data-query="What's best for wide feet?">👣 Wide Feet</button>
              </div>

              <!-- Input -->
              <form class="input-bar" id="chat-form">
                <button type="button" class="voice-btn" id="voice-btn">🎙️</button>
                <input type="text" class="input-field" id="chat-input" placeholder="Ask about shoes, sizing, deals..." autocomplete="off" />
                <button type="submit" class="send-btn">Send</button>
              </form>
            </div>
          ` : ''}

          ${this.showToast && !this.isOpen ? `
            <div class="toast" id="toast-msg">
              <div class="toast-label">✨ ShopAgent</div>
              👋 Hi! I'm your AI sales associate. Ask me anything!
            </div>
          ` : ''}

          <button class="fab-btn" id="fab-btn" aria-label="${this.isOpen ? 'Close' : 'Open'} ShopAgent">
            <div class="fab-inner">
              <span id="fab-emoji">${this.isOpen ? '✕' : this.getEmoji()}</span>
            </div>
            <div class="live-dot"></div>
            ${this.hasUnread && !this.isOpen ? '<div class="unread-badge">1</div>' : ''}
          </button>
        </div>
      `;

      if (this.isOpen) {
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
