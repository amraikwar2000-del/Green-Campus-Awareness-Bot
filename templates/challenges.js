/**
 * Eco-Challenges Controller
 * Manages daily student green challenges, completion tracking, gamified XP points, and badges.
 */

const ChallengesController = (() => {
  let challengesList = [];

  const elements = {
    challengesContainer: document.getElementById('challengesContainer'),
    progressFill: document.getElementById('ecoProgressFill'),
    progressText: document.getElementById('ecoProgressText'),
    completedCount: document.getElementById('completedChallengesCount'),
    totalCount: document.getElementById('totalChallengesCount'),
    totalPoints: document.getElementById('totalPointsDisplay'),
    ecoBadge: document.getElementById('ecoBadgeDisplay'),
    ecoLevel: document.getElementById('ecoLevelDisplay')
  };

  const init = () => {
    loadChallenges();
  };

  const loadChallenges = async () => {
    try {
      const response = await fetch('/api/challenges');
      const data = await response.json();
      challengesList = data.challenges || [];

      renderSummary(data);
      renderList(challengesList);
    } catch (error) {
      console.error('Error loading challenges:', error);
      if (elements.challengesContainer) {
        elements.challengesContainer.innerHTML = `
          <div class="text-center py-4 text-muted">
            <i class="bi bi-exclamation-triangle fs-2 text-warning"></i>
            <p class="mt-2">Unable to load campus eco-challenges at this time.</p>
          </div>
        `;
      }
    }
  };

  const renderSummary = (data) => {
    if (elements.progressFill) elements.progressFill.style.width = `${data.completion_percentage}%`;
    if (elements.progressText) elements.progressText.textContent = `${data.completion_percentage}% Completed`;
    if (elements.completedCount) elements.completedCount.textContent = data.completed;
    if (elements.totalCount) elements.totalCount.textContent = data.total;
    if (elements.totalPoints) elements.totalPoints.textContent = `${data.total_points} XP`;
    if (elements.ecoBadge) elements.ecoBadge.textContent = data.badge;
    if (elements.ecoLevel) elements.ecoLevel.textContent = data.level;
  };

  const renderList = (items) => {
    if (!elements.challengesContainer) return;
    elements.challengesContainer.innerHTML = '';

    items.forEach((item) => {
      const card = document.createElement('div');
      const isCompleted = Boolean(item.is_completed);
      card.className = `challenge-item-card ${isCompleted ? 'completed' : ''}`;
      card.id = `challenge-card-${item.id}`;

      card.innerHTML = `
        <div class="custom-checkbox-wrapper">
          <div class="custom-checkbox ${isCompleted ? 'checked' : ''}" data-id="${item.id}" role="checkbox" aria-checked="${isCompleted}" tabindex="0">
            ${isCompleted ? '<i class="bi bi-check-lg"></i>' : ''}
          </div>
        </div>
        <div class="flex-grow-1">
          <div class="d-flex align-items-center justify-content-between flex-wrap gap-2">
            <div class="challenge-title">${escapeHtml(item.title)}</div>
            <div class="challenge-tags">
              <span class="badge-tag badge-points">+${item.points} XP</span>
              <span class="badge-tag badge-category">${escapeHtml(item.category)}</span>
              <span class="badge-tag badge-difficulty">${escapeHtml(item.difficulty)}</span>
            </div>
          </div>
          <div class="challenge-desc">${escapeHtml(item.description)}</div>
          ${item.completed_at ? `<small class="text-success"><i class="bi bi-check-circle-fill"></i> Completed on ${item.completed_at.slice(0, 10)}</small>` : ''}
        </div>
      `;

      // Checkbox click listener
      const checkbox = card.querySelector('.custom-checkbox');
      checkbox.addEventListener('click', () => {
        toggleChallenge(item.id, !isCompleted);
      });

      // Keyboard accessibility (Space or Enter)
      checkbox.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggleChallenge(item.id, !isCompleted);
        }
      });

      elements.challengesContainer.appendChild(card);
    });
  };

  const toggleChallenge = async (challengeId, newStatus) => {
    try {
      const response = await fetch('/api/challenges/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_id: challengeId,
          completed: newStatus
        })
      });

      const result = await response.json();
      if (result.success) {
        // Refresh challenges and stats
        await loadChallenges();
        if (window.App && window.App.refreshStats) {
          window.App.refreshStats();
        }

        if (newStatus) {
          if (window.App) window.App.showToast("🎉 Eco-Challenge completed! Keep up the green work!", "success");
        } else {
          if (window.App) window.App.showToast("Challenge marked as pending.", "info");
        }
      }
    } catch (error) {
      console.error('Error toggling challenge:', error);
      if (window.App) window.App.showToast("Failed to update challenge status.", "danger");
    }
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
    loadChallenges
  };
})();
