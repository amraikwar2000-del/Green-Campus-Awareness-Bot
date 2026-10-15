/**
 * Main Application Orchestrator
 * Coordinates dashboard metrics, system status check, navigation, and module lifecycles.
 */

window.App = (() => {
  const elements = {
    systemStatusBadge: document.getElementById('systemStatusBadge'),
    systemStatusText: document.getElementById('systemStatusText'),
    statTipsShared: document.getElementById('statTipsShared'),
    statActivities: document.getElementById('statActivities'),
    statPlasticBottles: document.getElementById('statPlasticBottles'),
    statWaterSaved: document.getElementById('statWaterSaved'),
    statEnergySaved: document.getElementById('statEnergySaved'),
    statCo2Reduced: document.getElementById('statCo2Reduced'),
    activitiesTimeline: document.getElementById('activitiesTimeline'),
    toastContainer: document.getElementById('toastContainer')
  };

  const init = () => {
    checkSystemStatus();
    loadDashboardStats();
    loadActivities();

    // Initialize submodules
    if (typeof ChatController !== 'undefined') ChatController.init();
    if (typeof ChallengesController !== 'undefined') ChallengesController.init();
    if (typeof TipsController !== 'undefined') TipsController.init();
    if (typeof FeedbackController !== 'undefined') FeedbackController.init();

    setupNavigationScroll();
  };

  /**
   * Queries backend health & AI configuration
   */
  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();

      if (elements.systemStatusText) {
        if (data.openai_configured) {
          elements.systemStatusText.textContent = `AI: ${data.model}`;
          elements.systemStatusBadge.classList.add('border-success');
        } else {
          elements.systemStatusText.textContent = `Mode: Campus Knowledge Engine`;
        }
      }
    } catch (e) {
      console.warn('Status check failed:', e);
      if (elements.systemStatusText) {
        elements.systemStatusText.textContent = 'Server Offline';
      }
    }
  };

  /**
   * Loads campus dashboard impact statistics
   */
  const loadDashboardStats = async () => {
    try {
      const response = await fetch('/api/stats');
      const data = await response.json();

      animateCounter(elements.statTipsShared, data.tips_count);
      animateCounter(elements.statActivities, data.activities_count);
      animateCounter(elements.statPlasticBottles, data.plastic_bottles_saved);
      animateCounter(elements.statWaterSaved, data.water_saved_liters);
      animateCounter(elements.statEnergySaved, data.energy_saved_kwh);
      animateCounter(elements.statCo2Reduced, data.co2_reduced_kg);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  /**
   * Smooth number counter animation
   */
  const animateCounter = (el, target) => {
    if (!el || target === undefined) return;
    const current = 0;
    const duration = 1200;
    const start = performance.now();

    const step = (timestamp) => {
      const progress = Math.min((timestamp - start) / duration, 1);
      const value = Math.floor(progress * target);
      el.textContent = value.toLocaleString();
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target.toLocaleString();
      }
    };

    requestAnimationFrame(step);
  };

  /**
   * Loads recent campus eco activities
   */
  const loadActivities = async () => {
    try {
      const response = await fetch('/api/activities');
      const data = await response.json();
      const list = data.activities || [];

      if (!elements.activitiesTimeline) return;
      elements.activitiesTimeline.innerHTML = '';

      if (list.length === 0) {
        elements.activitiesTimeline.innerHTML = '<p class="text-muted small">No recent campus activities logged.</p>';
        return;
      }

      list.slice(0, 5).forEach((act) => {
        const item = document.createElement('div');
        item.className = 'd-flex align-items-center justify-content-between p-2 mb-2 bg-light rounded-3 border';
        item.innerHTML = `
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-success-subtle text-success p-2 rounded-circle">
              <i class="bi bi-patch-check-fill"></i>
            </span>
            <div>
              <strong class="d-block text-dark small">${escapeHtml(act.title)}</strong>
              <small class="text-muted" style="font-size: 0.72rem;">${escapeHtml(act.details || '')}</small>
            </div>
          </div>
          <span class="badge bg-warning-subtle text-warning-emphasis">+${act.points_earned} XP</span>
        `;
        elements.activitiesTimeline.appendChild(item);
      });
    } catch (e) {
      console.error('Error fetching activities:', e);
    }
  };

  /**
   * Global Toast Notification
   */
  const showToast = (message, type = 'info') => {
    if (!elements.toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `eco-toast toast-${type}`;

    let icon = 'bi-info-circle-fill text-primary';
    if (type === 'success') icon = 'bi-check-circle-fill text-success';
    if (type === 'warning') icon = 'bi-exclamation-triangle-fill text-warning';
    if (type === 'danger') icon = 'bi-x-circle-fill text-danger';

    toast.innerHTML = `
      <i class="bi ${icon} fs-4"></i>
      <div class="flex-grow-1 text-dark small fw-semibold">${escapeHtml(message)}</div>
      <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
    `;

    toast.querySelector('.btn-close').addEventListener('click', () => {
      toast.remove();
    });

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  };

  /**
   * Scroll active spy
   */
  const setupNavigationScroll = () => {
    const navLinks = document.querySelectorAll('.eco-navbar .nav-link');
    window.addEventListener('scroll', () => {
      let currentSection = '';
      const sections = document.querySelectorAll('section[id]');
      sections.forEach((section) => {
        const sectionTop = section.offsetTop - 120;
        if (window.scrollY >= sectionTop) {
          currentSection = section.getAttribute('id');
        }
      });

      navLinks.forEach((link) => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
          link.classList.add('active');
        }
      });
    });
  };

  const escapeHtml = (str) => {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  };

  return {
    init,
    showToast,
    refreshStats: () => {
      loadDashboardStats();
      loadActivities();
    }
  };
})();

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  window.App.init();
});
