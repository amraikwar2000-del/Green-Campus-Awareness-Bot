/**
 * Chatbot logic for EcoBot.
 * Handles user messaging, conversation history, quick suggestions,
 * typing indicators, Markdown formatting, and clear chat.
 */

const EcoChat = {
  history: [],
  isSending: false,
};

document.addEventListener('DOMContentLoaded', () => {
  initChat();
});

function initChat() {
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');

  if (chatSendBtn && chatInput) {
    chatSendBtn.addEventListener('click', () => sendUserMessage());
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendUserMessage();
      }
    });
  }

  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => clearChat());
  }

  // Setup quick suggestion buttons
  document.querySelectorAll('.suggestion-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const query = btn.getAttribute('data-query') || btn.innerText.trim();
      if (query) {
        if (EcoApp.activeTab !== 'chatbot') {
          switchTab('chatbot');
        }
        sendUserMessage(query);
      }
    });
  });
}

/**
 * Send message from user to EcoBot backend
 */
async function sendUserMessage(overrideText = null) {
  if (EcoChat.isSending) return;

  const inputEl = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  const messageText = overrideText || (inputEl ? inputEl.value.trim() : '');

  if (!messageText) return;

  // Clear input field
  if (inputEl) inputEl.value = '';

  // Append user message bubble
  appendMessage('user', messageText);

  // Add to local history
  EcoChat.history.push({ role: 'user', content: messageText });

  // Show typing indicator
  setTypingIndicator(true);
  EcoChat.isSending = true;
  if (sendBtn) sendBtn.disabled = true;

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: messageText,
        session_id: EcoApp.sessionId,
        history: EcoChat.history.slice(-8)
      })
    });

    const data = await response.json();
    setTypingIndicator(false);
    EcoChat.isSending = false;
    if (sendBtn) sendBtn.disabled = false;

    if (data.success && data.response) {
      appendMessage('bot', data.response, data.source);
      EcoChat.history.push({ role: 'assistant', content: data.response });
    } else {
      appendMessage('bot', `⚠️ ${data.error || 'Oops, I had trouble processing that. Please try again!'}`, 'error');
    }
  } catch (err) {
    console.error("Chat error:", err);
    setTypingIndicator(false);
    EcoChat.isSending = false;
    if (sendBtn) sendBtn.disabled = false;
    appendMessage('bot', "⚠️ Connection error. Please ensure the backend server is running and try again.", 'error');
  }
}

/**
 * Append a message bubble to the chat container
 */
function appendMessage(sender, rawText, source = null) {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  const row = document.createElement('div');
  row.className = `chat-row ${sender === 'user' ? 'user-row' : 'bot-row'}`;

  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (sender === 'user') {
    row.innerHTML = `
      <div class="chat-bubble">
        <div>${escapeHtml(rawText)}</div>
        <div class="chat-time text-end">${currentTime}</div>
      </div>
    `;
  } else {
    const formattedHtml = formatMarkdown(rawText);
    const sourceBadge = source === 'openai'
      ? '<span class="badge bg-success-subtle text-success small ms-2"><i class="bi bi-stars"></i> OpenAI Live</span>'
      : '<span class="badge bg-secondary-subtle text-secondary small ms-2"><i class="bi bi-mortarboard"></i> Eco Campus Engine</span>';

    row.innerHTML = `
      <img src="/static/images/ecobot-avatar.jpg" alt="EcoBot" class="chat-bubble-avatar">
      <div class="chat-bubble">
        <div class="d-flex align-items-center justify-content-between mb-1">
          <strong class="text-success" style="font-size:0.85rem;">🌿 EcoBot ${sourceBadge}</strong>
          <button class="btn btn-sm btn-link text-muted p-0 ms-2 copy-btn" title="Copy response" onclick="copyMessageText(this)">
            <i class="bi bi-clipboard"></i>
          </button>
        </div>
        <div class="chat-text-content">${formattedHtml}</div>
        <div class="chat-time">${currentTime}</div>
      </div>
    `;
  }

  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

/**
 * Toggle the animated typing indicator
 */
function setTypingIndicator(show) {
  const container = document.getElementById('chatMessages');
  let indicator = document.getElementById('typingIndicatorRow');

  if (show) {
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'typingIndicatorRow';
      indicator.className = 'chat-row bot-row';
      indicator.innerHTML = `
        <img src="/static/images/ecobot-avatar.jpg" alt="EcoBot" class="chat-bubble-avatar">
        <div class="chat-bubble" style="background:#ffffff; border:1px solid #e2ece9;">
          <div class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      `;
      container.appendChild(indicator);
    }
    container.scrollTop = container.scrollHeight;
  } else {
    if (indicator) {
      indicator.remove();
    }
  }
}

/**
 * Clear the current conversation
 */
function clearChat() {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  EcoChat.history = [];
  container.innerHTML = `
    <div class="chat-row bot-row">
      <img src="/static/images/ecobot-avatar.jpg" alt="EcoBot" class="chat-bubble-avatar">
      <div class="chat-bubble">
        <h4 class="fw-bold mb-2">Hello there! 🌿 I'm EcoBot.</h4>
        <p>I am your campus environmental awareness assistant! You can ask me anything about recycling, saving water, cutting electricity consumption, composting, or participating in green campus challenges.</p>
        <p class="mb-0"><strong>Try asking:</strong> Click any of the quick suggestions above to start!</p>
        <div class="chat-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
      </div>
    </div>
  `;
  showEcoToast("Chat history cleared.", "info");
}

/**
 * Copy message content to clipboard
 */
function copyMessageText(btn) {
  const card = btn.closest('.chat-bubble');
  const textEl = card ? card.querySelector('.chat-text-content') : null;
  if (!textEl) return;

  navigator.clipboard.writeText(textEl.innerText).then(() => {
    btn.innerHTML = '<i class="bi bi-check text-success"></i>';
    setTimeout(() => {
      btn.innerHTML = '<i class="bi bi-clipboard"></i>';
    }, 2000);
  });
}

/**
 * Helper to escape HTML characters
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

/**
 * Lightweight client-side Markdown formatter for clean chat responses
 */
function formatMarkdown(text) {
  if (!text) return '';

  let html = escapeHtml(text);

  // Headers (### Header)
  html = html.replace(/^### (.*$)/gim, '<h4 class="fw-bold text-success mt-2 mb-2">$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3 class="fw-bold text-success mt-2 mb-2">$1</h3>');

  // Bold (**bold**)
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

  // Italics (*italic*)
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

  // Unordered list items (• or -)
  html = html.replace(/^[•\-\*]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gms, '<ul class="mb-2 ps-3">$1</ul>');

  // Line breaks
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br>');

  return `<p class="mb-0">${html}</p>`;
}
