/**
 * Main application coordinator for Green Campus Awareness Bot.
 * Manages view/tab transitions, toast notifications, and global state.
 */

// Global State
const EcoApp = {
  activeTab: 'home',
  sessionId: 'session_' + Math.random().toString(36).substring(2, 10),
  aiLive: false,
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  // Check AI integration status
  checkAiStatus();

  // Read initial tab from URL or data attribute
  const urlParams = new URLSearchParams(window.location.search);
  const requestedTab = urlParams.get('tab') || window.location.pathname.replace('/', '') || 'home';
  switchTab(requestedTab);

  // Setup navigation event listeners
  document.querySelectorAll('[data-nav-target]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const target = el.getAttribute('data-nav-target');
      if (target) {
        switchTab(target);
      }
    });
  });

  // Load Tip of the Day in Hero
  loadTipOfTheDay();
});

/**
 * Switch active application tab/section smoothly.
 */
function switchTab(tabId) {
  const validTabs = ['home', 'chatbot', 'challenges', 'tips', 'dashboard', 'about', 'feedback'];
  if (!validTabs.includes(tabId)) {
    tabId = 'home';
  }

  EcoApp.activeTab = tabId;

  // Update navbar links
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    if (link.getAttribute('data-nav-target') === tabId) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Update view sections
  document.querySelectorAll('.app-section').forEach(section => {
    section.classList.remove('active');
  });

  const targetSection = document.getElementById(`section-${tabId}`);
  if (targetSection) {
    targetSection.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Trigger lazy data loading for specific tabs
  if (tabId === 'challenges' && window.loadChallenges) {
    window.loadChallenges();
  } else if (tabId === 'tips' && window.loadTips) {
    window.loadTips();
  } else if (tabId === 'dashboard' && window.loadDashboard) {
    window.loadDashboard();
  } else if (tabId === 'feedback' && window.loadFeedback) {
    window.loadFeedback();
  } else if (tabId === 'chatbot') {
    // Focus chat input
    const input = document.getElementById('chatInput');
    if (input) setTimeout(() => input.focus(), 200);
  }

  // Update browser history title and URL without full reload
  window.history.pushState({ tab: tabId }, '', `?tab=${tabId}`);
}

/**
 * Handle browser back/forward buttons
 */
window.addEventListener('popstate', (e) => {
  if (e.state && e.state.tab) {
    switchTab(e.state.tab);
  }
});

/**
 * Check AI status from backend
 */
async function checkAiStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.success && data.ai) {
      EcoApp.aiLive = data.ai.is_live;
      const statusPill = document.getElementById('navAiStatus');
      const chatStatusPill = document.getElementById('chatModelBadge');
      if (statusPill) {
        statusPill.innerHTML = `
          <span class="status-pulse"></span>
          <span>${data.ai.status_label}</span>
        `;
      }
      if (chatStatusPill) {
        chatStatusPill.innerText = data.ai.is_live ? `Powered by OpenAI (${data.ai.model})` : "Campus Knowledge Engine (Demo Mode)";
      }
    }
  } catch (err) {
    console.warn("Could not check AI status:", err);
  }
}

/**
 * Display a modern toast alert to the user.
 */
function showEcoToast(message, type = 'success') {
  let toastEl = document.getElementById('ecoToast');
  if (!toastEl) {
    toastEl = document.createElement('div');
    toastEl.id = 'ecoToast';
    toastEl.className = 'eco-toast';
    document.body.appendChild(toastEl);
  }

  const iconClass = type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-info-circle-fill text-primary';
  toastEl.innerHTML = `
    <i class="bi ${iconClass} fs-4"></i>
    <div>
      <strong>Green Campus Bot</strong>
      <div class="small text-muted">${message}</div>
    </div>
  `;

  toastEl.classList.add('show');
  setTimeout(() => {
    toastEl.classList.remove('show');
  }, 4200);
}

/**
 * Load Tip of the Day in Hero Section
 */
async function loadTipOfTheDay() {
  const container = document.getElementById('heroTipOfTheDay');
  if (!container) return;

  try {
    const res = await fetch('/api/tips');
    const data = await res.json();
    if (data.success && data.tips && data.tips.length > 0) {
      // Pick random tip
      const randomTip = data.tips[Math.floor(Math.random() * data.tips.length)];
      container.innerHTML = `
        <div class="d-flex align-items-center gap-3">
          <div class="tip-icon-badge flex-shrink-0" style="background:#eafaf1; color:#1b4332;">
            <i class="bi ${randomTip.icon}"></i>
          </div>
          <div>
            <div class="text-uppercase text-success fw-bold small" style="letter-spacing:0.05em;">🌿 Eco Tip of the Day • ${randomTip.category}</div>
            <h6 class="mb-1 fw-bold text-dark">${randomTip.title}</h6>
            <p class="mb-0 text-muted small">${randomTip.content}</p>
          </div>
        </div>
      `;
    }
  } catch (e) {
    console.error("Tip of the day failed:", e);
  }
}
