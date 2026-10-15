/**
 * Environmental Tips Controller
 * Manages categorized sustainability tips, instant search filtering, and quick actions.
 */

const TipsController = (() => {
  let allTips = [];
  let currentCategory = 'all';

  const elements = {
    tipsContainer: document.getElementById('tipsContainer'),
    tipsFilterBar: document.getElementById('tipsFilterBar'),
    tipsSearchInput: document.getElementById('tipsSearchInput'),
    tipsResultCount: document.getElementById('tipsResultCount')
  };

  const init = () => {
    loadTips();

    if (elements.tipsSearchInput) {
      elements.tipsSearchInput.addEventListener('input', (e) => {
        filterTips();
      });
    }
  };

  const loadTips = async () => {
    try {
      const response = await fetch('/api/tips');
      const data = await response.json();
      allTips = data.tips || [];

      renderFilterPills(data.categories || []);
      renderTips(allTips);
    } catch (error) {
      console.error('Error loading tips:', error);
      if (elements.tipsContainer) {
        elements.tipsContainer.innerHTML = `
          <div class="col-12 text-center py-5 text-muted">
            <i class="bi bi-exclamation-triangle fs-2 text-warning"></i>
            <p class="mt-2">Unable to load green tips currently.</p>
          </div>
        `;
      }
    }
  };

  const renderFilterPills = (categories) => {
    if (!elements.tipsFilterBar) return;
    elements.tipsFilterBar.innerHTML = '';

    const allPill = document.createElement('button');
    allPill.type = 'button';
    allPill.className = `filter-pill ${currentCategory === 'all' ? 'active' : ''}`;
    allPill.innerHTML = `<i class="bi bi-grid-fill"></i> All Tips`;
    allPill.addEventListener('click', () => {
      currentCategory = 'all';
      updateActivePill(allPill);
      filterTips();
    });
    elements.tipsFilterBar.appendChild(allPill);

    const iconMap = {
      'Water Conservation': 'bi-droplet-fill',
      'Energy Conservation': 'bi-lightning-charge-fill',
      'Waste Management': 'bi-recycle',
      'Air Quality': 'bi-wind',
      'Biodiversity': 'bi-tree-fill',
      'Sustainable Transportation': 'bi-bicycle'
    };

    categories.forEach((cat) => {
      const pill = document.createElement('button');
      pill.type = 'button';
      pill.className = `filter-pill ${currentCategory === cat ? 'active' : ''}`;
      const icon = iconMap[cat] || 'bi-leaf-fill';
      pill.innerHTML = `<i class="bi ${icon}"></i> ${escapeHtml(cat)}`;

      pill.addEventListener('click', () => {
        currentCategory = cat;
        updateActivePill(pill);
        filterTips();
      });

      elements.tipsFilterBar.appendChild(pill);
    });
  };

  const updateActivePill = (activeElement) => {
    const pills = elements.tipsFilterBar.querySelectorAll('.filter-pill');
    pills.forEach((p) => p.classList.remove('active'));
    activeElement.classList.add('active');
  };

  const filterTips = () => {
    const searchTerm = (elements.tipsSearchInput?.value || '').toLowerCase().trim();

    const filtered = allTips.filter((tip) => {
      const matchCat = currentCategory === 'all' || tip.category === currentCategory;
      const matchSearch = !searchTerm ||
        tip.title.toLowerCase().includes(searchTerm) ||
        tip.content.toLowerCase().includes(searchTerm) ||
        tip.category.toLowerCase().includes(searchTerm);
      return matchCat && matchSearch;
    });

    renderTips(filtered);
  };

  const renderTips = (tips) => {
    if (!elements.tipsContainer) return;
    elements.tipsContainer.innerHTML = '';

    if (elements.tipsResultCount) {
      elements.tipsResultCount.textContent = `Showing ${tips.length} tip${tips.length !== 1 ? 's' : ''}`;
    }

    if (tips.length === 0) {
      elements.tipsContainer.innerHTML = `
        <div class="col-12 text-center py-5">
          <div class="p-4 bg-white rounded-4 shadow-sm border mx-auto" style="max-width: 450px;">
            <i class="bi bi-search fs-1 text-muted"></i>
            <h5 class="mt-3 text-secondary">No matching tips found</h5>
            <p class="text-muted small mb-0">Try clearing your search term or select another category.</p>
          </div>
        </div>
      `;
      return;
    }

    tips.forEach((tip) => {
      const col = document.createElement('div');
      col.className = 'col-lg-4 col-md-6 mb-4';

      col.innerHTML = `
        <div class="tip-card">
          <div class="tip-card-header">
            <div class="tip-category-icon">
              <i class="bi ${tip.icon || 'bi-lightbulb-fill'}"></i>
            </div>
            <span class="badge ${tip.impact_level === 'High' ? 'bg-success' : 'bg-primary-subtle text-primary'} px-2 py-1 rounded-pill small">
              ${escapeHtml(tip.impact_level || 'Medium')} Impact
            </span>
          </div>
          <div class="tip-title">${escapeHtml(tip.title)}</div>
          <div class="tip-content">${escapeHtml(tip.content)}</div>
          <div class="tip-card-footer">
            <span class="text-muted small"><i class="bi bi-tag-fill me-1"></i>${escapeHtml(tip.category)}</span>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-success btn-ask-tip" title="Ask EcoBot about this" data-query="Tell me more about ${escapeHtml(tip.title)}">
                <i class="bi bi-chat-dots-fill"></i> Ask Bot
              </button>
              <button class="btn btn-sm btn-light border btn-copy-tip" title="Copy Tip">
                <i class="bi bi-clipboard"></i>
              </button>
            </div>
          </div>
        </div>
      `;

      // Copy Tip
      const copyBtn = col.querySelector('.btn-copy-tip');
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(`${tip.title} - ${tip.content}`);
        copyBtn.innerHTML = '<i class="bi bi-check text-success"></i>';
        setTimeout(() => { copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>'; }, 2000);
        if (window.App) window.App.showToast("Tip copied to clipboard!", "success");
      });

      // Ask Bot button
      const askBtn = col.querySelector('.btn-ask-tip');
      askBtn.addEventListener('click', () => {
        const query = askBtn.getAttribute('data-query');
        // Scroll to chat section and trigger
        const chatSection = document.getElementById('chatbot-section');
        if (chatSection) {
          chatSection.scrollIntoView({ behavior: 'smooth' });
          setTimeout(() => {
            if (ChatController && ChatController.sendMessage) {
              ChatController.sendMessage(query);
            }
          }, 600);
        }
      });

      elements.tipsContainer.appendChild(col);
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
    loadTips
  };
})();
