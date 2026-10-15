/**
 * Eco-Challenges and Activity Tracking Module.
 * Manages challenge completions, user score calculations,
 * and activity logging with live database persistence.
 */

let allChallenges = [];
let challengeFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
  initChallenges();
});

function initChallenges() {
  // Activity form listener
  const activityForm = document.getElementById('activityLogForm');
  if (activityForm) {
    activityForm.addEventListener('submit', (e) => {
      e.preventDefault();
      submitActivityLog();
    });
  }

  // Filter pill listeners
  document.querySelectorAll('.challenge-filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.challenge-filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      challengeFilter = pill.getAttribute('data-frequency') || 'all';
      renderChallenges();
    });
  });
}

/**
 * Fetch and load challenges from API
 */
window.loadChallenges = async function() {
  const container = document.getElementById('challengesList');
  if (!container) return;

  try {
    const res = await fetch('/api/challenges');
    const data = await res.json();
    if (data.success && data.challenges) {
      allChallenges = data.challenges;
      renderChallenges();
      updateScoreSummary();
    }
  } catch (err) {
    console.error("Failed to load challenges:", err);
  }
};

/**
 * Render challenge cards according to the active filter
 */
function renderChallenges() {
  const container = document.getElementById('challengesList');
  if (!container) return;

  let filtered = allChallenges;
  if (challengeFilter !== 'all') {
    filtered = allChallenges.filter(c => c.frequency.toLowerCase() === challengeFilter.toLowerCase());
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5 text-muted">
        <i class="bi bi-tree fs-1 text-success mb-2 d-block"></i>
        <p>No challenges found in this category.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(ch => {
    const isCompleted = ch.is_completed === 1;
    return `
      <div class="challenge-item ${isCompleted ? 'completed' : ''}" id="challenge-item-${ch.id}">
        <button class="challenge-checkbox-btn" onclick="toggleChallengeCompletion(${ch.id})" title="${isCompleted ? 'Completed! Click to unmark' : 'Click to mark as done'}">
          <i class="bi bi-check-lg"></i>
        </button>
        <div class="challenge-details">
          <div class="d-flex align-items-center gap-2 mb-1 flex-wrap">
            <span class="badge-tag"><i class="bi ${ch.icon || 'bi-leaf'} me-1"></i>${ch.category}</span>
            <span class="badge-points">+${ch.points} Eco-Points</span>
            <span class="badge bg-light text-secondary border small">${ch.frequency}</span>
            ${isCompleted ? '<span class="badge bg-success text-white small"><i class="bi bi-check-circle-fill me-1"></i>Completed</span>' : ''}
          </div>
          <h5 class="challenge-title">${ch.title}</h5>
          <p class="challenge-desc mb-2">${ch.description}</p>
          <div class="small text-muted">
            <i class="bi bi-people me-1"></i>Completed <strong>${ch.completed_count}</strong> times by campus members
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Toggle completion of a challenge via backend API
 */
async function toggleChallengeCompletion(challengeId) {
  try {
    const res = await fetch('/api/challenges/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ challenge_id: challengeId })
    });
    const data = await res.json();
    if (data.success && data.challenge) {
      // Update local item
      const idx = allChallenges.findIndex(c => c.id === challengeId);
      if (idx !== -1) {
        allChallenges[idx] = data.challenge;
      }
      renderChallenges();
      updateScoreSummary();

      const actionText = data.challenge.is_completed === 1
        ? `Great job! You earned +${data.challenge.points} Eco-Points! 🌿`
        : "Challenge marked as uncompleted.";
      showEcoToast(actionText, 'success');

      // Refresh dashboard if loaded
      if (window.loadDashboard) {
        window.loadDashboard();
      }
    }
  } catch (err) {
    console.error("Failed to toggle challenge:", err);
  }
}

/**
 * Update the user's progress bar and point score
 */
function updateScoreSummary() {
  const completed = allChallenges.filter(c => c.is_completed === 1);
  const total = allChallenges.length;
  const percentage = total > 0 ? Math.round((completed.length / total) * 100) : 0;
  const earnedPoints = completed.reduce((sum, c) => sum + c.points, 0);

  const completedCountEl = document.getElementById('completedChallengesCount');
  const totalChallengesCountEl = document.getElementById('totalChallengesCount');
  const progressBarEl = document.getElementById('challengesProgressBar');
  const userScoreEl = document.getElementById('userEcoScore');

  if (completedCountEl) completedCountEl.innerText = completed.length;
  if (totalChallengesCountEl) totalChallengesCountEl.innerText = total;
  if (progressBarEl) {
    progressBarEl.style.width = `${percentage}%`;
    progressBarEl.innerText = `${percentage}%`;
  }
  if (userScoreEl) userScoreEl.innerText = earnedPoints;
}

/**
 * Submit a student activity log to the database
 */
async function submitActivityLog() {
  const nameInput = document.getElementById('activityStudentName');
  const roleSelect = document.getElementById('activityRole');
  const typeSelect = document.getElementById('activityType');
  const descInput = document.getElementById('activityDescription');
  const impactInput = document.getElementById('activityImpact');
  const submitBtn = document.getElementById('activitySubmitBtn');

  if (!typeSelect || !descInput) return;

  const name = nameInput.value.trim() || 'Campus Student';
  const role = roleSelect.value || 'Student';
  const activityType = typeSelect.value;
  const description = descInput.value.trim();
  const impactValue = impactInput.value.trim() || '1 Eco Action';

  if (!activityType || !description) {
    showEcoToast("Please fill in the activity type and description.", "info");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

  try {
    const res = await fetch('/api/activities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_name: name,
        role: role,
        activity_type: activityType,
        description: description,
        impact_value: impactValue
      })
    });

    const data = await res.json();
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-send me-1"></i>Log Eco-Activity';

    if (data.success) {
      showEcoToast("Activity recorded successfully! 🌱", "success");
      // Reset form
      descInput.value = '';
      impactInput.value = '';

      // Reload dashboard & activities
      if (window.loadDashboard) {
        window.loadDashboard();
      }
    } else {
      showEcoToast(data.error || "Failed to record activity", "info");
    }
  } catch (err) {
    console.error("Error submitting activity:", err);
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-send me-1"></i>Log Eco-Activity';
    showEcoToast("Server connection error.", "info");
  }
}
