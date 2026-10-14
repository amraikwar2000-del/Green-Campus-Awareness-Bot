/**
 * EcoBot Chat Controller
 * Handles conversation state, API interaction, markdown parsing, and quick replies.
 */

const ChatController = (() => {
  let conversationHistory = [];
  let isGenerating = false;

  const elements = {
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatForm: document.getElementById('chatForm'),
    btnSend: document.getElementById('btnSend'),
    typingIndicator: document.getElementById('typingIndicator'),
    quickRepliesContainer: document.getElementById('quickRepliesContainer'),
    btnClearChat: document.getElementById('btnClearChat'),
    knowledgeBanner: document.getElementById('knowledgeBanner'),
    aiStatusText: document.getElementById('aiStatusText')
  };

  /**
   * Initializes chat listeners and greeting
   */
  const init = () => {
    if (!elements.chatForm) return;

    elements.chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      sendMessage();
    });

    elements.btnClearChat.addEventListener('click', clearChat);

    // Initial greeting in history
    conversationHistory.push({
      role: 'assistant',
      content: "Hello! I'm EcoBot, your Green Campus Awareness Assistant 🌿. How can I help you make our campus cleaner and greener today?"
    });

    renderSuggestedChips([
      "How can I make my campus greener?",
      "How can I save water in college?",
      "Where should I dispose of plastic waste?",
      "What is composting?",
      "How can students reduce electricity consumption?"
    ]);
  };

  /**
   * Simple safe markdown-to-HTML parser for bot responses
   */
  const formatMarkdown = (text) => {
    if (!text) return '';
    let html = text
      // Escape basic html
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Code inline
      .replace(/`(.*?)`/g, '<code class="bg-light px-1 rounded text-success">$1</code>');

    // Split lines and parse lists
    const lines = html.split('\n');
    let inList = false;
    let listType = '';
    let formattedLines = [];

    lines.forEach((line) => {
      const trimmed = line.trim();
      const bulletMatch = trimmed.match(/^([•\-\*])\s+(.+)$/);
      const numberMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);

      if (bulletMatch) {
        if (!inList) {
          formattedLines.push('<ul class="mb-2">');
          inList = true;
          listType = 'ul';
        }
        formattedLines.push(`<li>${bulletMatch[2]}</li>`);
      } else if (numberMatch) {
        if (!inList) {
          formattedLines.push('<ol class="mb-2">');
          inList = true;
          listType = 'ol';
        }
        formattedLines.push(`<li>${numberMatch[2]}</li>`);
      } else {
        if (inList) {
          formattedLines.push(listType === 'ul' ? '</ul>' : '</ol>');
          inList = false;
        }
        if (trimmed) {
          formattedLines.push(`<p class="mb-2">${trimmed}</p>`);
        }
      }
    });

    if (inList) {
      formattedLines.push(listType === 'ul' ? '</ul>' : '</ol>');
    }

    return formattedLines.join('');
  };

  /**
   * Sends user message to backend
   */
  const sendMessage = async (customText = null) => {
    if (isGenerating) return;

    const text = customText || elements.chatInput.value.trim();
    if (!text) return;

    // Reset input field
    elements.chatInput.value = '';
    elements.chatInput.focus();

    // Append User Message to UI
    appendUserMessage(text);
    conversationHistory.push({ role: 'user', content: text });

    // Show typing indicator
    showTyping();
    isGenerating = true;

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: conversationHistory
        })
      });

      const data = await response.json();
      hideTyping();
      isGenerating = false;

      if (data.response) {
        appendBotMessage(data.response, data.source, data.api_notice);
        conversationHistory.push({ role: 'assistant', content: data.response });

        // Update suggestions if returned
        if (data.suggestions && data.suggestions.length > 0) {
          renderSuggestedChips(data.suggestions);
        }

        // Update AI status text if configured
        if (data.source === 'openai') {
          if (elements.aiStatusText) elements.aiStatusText.textContent = `OpenAI (${data.model || 'Active'})`;
          if (elements.knowledgeBanner) elements.knowledgeBanner.classList.add('d-none');
        } else {
          if (elements.knowledgeBanner) {
            elements.knowledgeBanner.classList.remove('d-none');
            const noticeSpan = elements.knowledgeBanner.querySelector('.banner-text');
            if (noticeSpan && data.api_notice) noticeSpan.textContent = data.api_notice;
          }
        }
      } else {
        appendBotMessage("I encountered an unexpected issue while retrieving that information. Please try asking again!", "error");
      }
    } catch (error) {
      hideTyping();
      isGenerating = false;
      console.error('Chat error:', error);
      appendBotMessage("Connection to EcoBot server was interrupted. Please check if the Flask server is running.", "error");
    }
  };

  /**
   * Appends User Message to UI
   */
  const appendUserMessage = (text) => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement('div');
    row.className = 'message-row user-message';
    row.innerHTML = `
      <div class="msg-avatar user-avatar-badge" title="You">
        <i class="bi bi-person-fill"></i>
      </div>
      <div class="message-bubble">
        <p class="mb-0">${escapeHtml(text)}</p>
        <span class="msg-time">${timeStr}</span>
      </div>
    `;
    elements.chatMessages.appendChild(row);
    scrollToBottom();
  };

  /**
   * Appends Bot Message to UI with copy and text-to-speech actions
   */
  const appendBotMessage = (rawText, source = 'ai', notice = '') => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const formattedHtml = formatMarkdown(rawText);

    const row = document.createElement('div');
    row.className = 'message-row bot-message';
    row.innerHTML = `
      <div class="msg-avatar" title="EcoBot">
        <img src="/static/img/ecobot_avatar.svg" alt="EcoBot Avatar">
      </div>
      <div class="message-bubble">
        ${formattedHtml}
        <div class="d-flex align-items-center justify-content-between mt-2 pt-1 border-top border-light">
          <span class="msg-time mb-0">EcoBot • ${timeStr} ${source === 'knowledge_engine' ? '<span class="badge bg-light text-success border ms-1" style="font-size:0.65rem;">Knowledge Engine</span>' : ''}</span>
          <div class="bot-msg-actions d-flex gap-2">
            <button class="btn btn-sm text-secondary p-0 btn-copy-msg" title="Copy text">
              <i class="bi bi-clipboard"></i>
            </button>
            <button class="btn btn-sm text-secondary p-0 btn-speak-msg" title="Read aloud">
              <i class="bi bi-volume-up"></i>
            </button>
          </div>
        </div>
      </div>
    `;

    // Copy button listener
    const copyBtn = row.querySelector('.btn-copy-msg');
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(rawText);
      copyBtn.innerHTML = '<i class="bi bi-check text-success"></i>';
      setTimeout(() => { copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>'; }, 2000);
    });

    // Speech synthesis listener
    const speakBtn = row.querySelector('.btn-speak-msg');
    speakBtn.addEventListener('click', () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        // Strip markdown characters for spoken text
        const plainSpeech = rawText.replace(/[*#_`]/g, '');
        const utterance = new SpeechSynthesisUtterance(plainSpeech);
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    });

    elements.chatMessages.appendChild(row);
    scrollToBottom();
  };

  /**
   * Renders quick reply suggestion chips
   */
  const renderSuggestedChips = (suggestions) => {
    if (!elements.quickRepliesContainer) return;
    elements.quickRepliesContainer.innerHTML = `
      <div class="quick-replies-label">
        <i class="bi bi-stars text-warning"></i> Suggestions:
      </div>
    `;

    suggestions.forEach((q) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'suggestion-chip';
      chip.innerHTML = `<i class="bi bi-chat-quote"></i> ${escapeHtml(q)}`;
      chip.addEventListener('click', () => {
        sendMessage(q);
      });
      elements.quickRepliesContainer.appendChild(chip);
    });
  };

  const showTyping = () => {
    elements.typingIndicator.style.display = 'flex';
    scrollToBottom();
  };

  const hideTyping = () => {
    elements.typingIndicator.style.display = 'none';
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, 50);
  };

  const clearChat = () => {
    elements.chatMessages.innerHTML = '';
    conversationHistory = [];

    // Re-add initial greeting
    const welcome = "Chat cleared! I'm EcoBot. What green campus topic would you like to explore next? 🌿";
    appendBotMessage(welcome, 'knowledge_engine');
    conversationHistory.push({ role: 'assistant', content: welcome });

    renderSuggestedChips([
      "How can I make my campus greener?",
      "How can I save water in college?",
      "Where should I dispose of plastic waste?",
      "What is composting?",
      "How can students reduce electricity consumption?"
    ]);

    if (window.App) window.App.showToast("Chat history cleared", "info");
  };

  const escapeHtml = (str) => {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  return {
    init,
    sendMessage
  };
})();
