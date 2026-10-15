/**
 * Environmental Tips Module.
 * Provides categorized filtering, real-time search,
 * copying tips to clipboard, and local favorites saving.
 */

let allTips = [];
let activeTipCategory = 'all';

document.addEventListener('DOMContentLoaded', () => {
  initTips();
});

function initTips() {
  const searchInput = document.getElementById('tipsSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterAndRenderTips(e.target.value.trim().toLowerCase());
    });
  }

  // Category filter listeners
  document.querySelectorAll('.tip-category-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.tip-category-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeTipCategory = pill.getAttribute('data-category') || 'all';
      const query = (document.getElementById('tipsSearchInput')?.value || '').trim().toLowerCase();
      filterAndRenderTips(query);
    });
  });
}

/**
 * Fetch tips from API
 */
window.loadTips = async function() {
  const container = document.getElementById('tipsGridContainer');
  if (!container) return;

  try {
    const res = await fetch('/api/tips');
    const data = await res.json();
    if (data.success && data.tips) {
      allTips = data.tips;
      filterAndRenderTips('');
    }
  } catch (err) {
    console.error("Failed to fetch tips:", err);
  }
};

/**
 * Filter and render tips
 */
function filterAndRenderTips(searchQuery = '') {
  const container = document.getElementById('tipsGridContainer');
  if (!container) return;

  let filtered = allTips;

  if (activeTipCategory !== 'all') {
    filtered = filtered.filter(t => t.category.toLowerCase() === activeTipCategory.toLowerCase());
  }

  if (searchQuery) {
    filtered = filtered.filter(t =>
      t.title.toLowerCase().includes(searchQuery) ||
      t.content.toLowerCase().includes(searchQuery) ||
      (t.tags && t.tags.toLowerCase().includes(searchQuery))
    );
  }

  const countBadge = document.getElementById('tipsCountBadge');
  if (countBadge) {
    countBadge.innerText = `${filtered.length} Tips`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5">
        <i class="bi bi-search text-muted fs-1 mb-2 d-block"></i>
        <h5 class="text-muted">No tips found matching your criteria</h5>
        <p class="text-muted small">Try searching for keywords like "water", "plastic", "lights", or "compost".</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(tip => {
    return `
      <div class="col-md-6 col-lg-4 mb-4">
        <div class="tip-card eco-card" id="tip-card-${tip.id}">
          <div>
            <div class="tip-header">
              <span class="badge bg-success-subtle text-success fw-semibold small">${tip.category}</span>
              <div class="tip-icon-badge">
                <i class="bi ${tip.icon}"></i>
              </div>
            </div>
            <h5 class="tip-title">${tip.title}</h5>
            <p class="tip-content">${tip.content}</p>
          </div>
          <div class="tip-impact-footer">
            <span><i class="bi bi-graph-up-arrow me-1"></i>${tip.impact_metric}</span>
            <button class="btn btn-sm btn-outline-success rounded-pill px-2 py-1" onclick="copyTipText('${escapeHtml(tip.title)}', '${escapeHtml(tip.content)}')">
              <i class="bi bi-share me-1"></i>Share
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Copy tip text to clipboard
 */
function copyTipText(title, content) {
  const shareText = `🌿 Green Campus Tip: ${title}\n\n${content}\n\n— shared from Green Campus Awareness Bot`;
  navigator.clipboard.writeText(shareText).then(() => {
    showEcoToast("Tip copied to clipboard! Ready to share 🌿", "success");
  });
}
