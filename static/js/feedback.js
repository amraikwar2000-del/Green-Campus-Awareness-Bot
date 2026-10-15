/**
 * Feedback Module.
 * Manages star rating selection, feedback form submission,
 * and loading community reviews.
 */

let selectedRating = 5;

document.addEventListener('DOMContentLoaded', () => {
  initFeedback();
});

function initFeedback() {
  // Star rating click and hover
  const stars = document.querySelectorAll('#starRatingBox .star');
  stars.forEach(star => {
    star.addEventListener('click', () => {
      selectedRating = parseInt(star.getAttribute('data-value'), 10);
      updateStarDisplay(selectedRating);
    });

    star.addEventListener('mouseenter', () => {
      const hoverVal = parseInt(star.getAttribute('data-value'), 10);
      highlightStars(hoverVal);
    });
  });

  const starBox = document.getElementById('starRatingBox');
  if (starBox) {
    starBox.addEventListener('mouseleave', () => {
      updateStarDisplay(selectedRating);
    });
  }

  // Form submit
  const form = document.getElementById('feedbackForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitFeedback();
    });
  }
}

function highlightStars(val) {
  const stars = document.querySelectorAll('#starRatingBox .star');
  stars.forEach(star => {
    const starVal = parseInt(star.getAttribute('data-value'), 10);
    if (starVal <= val) {
      star.classList.add('active');
    } else {
      star.classList.remove('active');
    }
  });
}

function updateStarDisplay(val) {
  highlightStars(val);
  const ratingText = document.getElementById('selectedRatingText');
  if (ratingText) {
    const labels = {
      1: "Needs Improvement ⭐",
      2: "Fair ⭐⭐",
      3: "Good ⭐⭐⭐",
      4: "Very Good ⭐⭐⭐⭐",
      5: "Excellent! 🌿 ⭐⭐⭐⭐⭐"
    };
    ratingText.innerText = labels[val] || `${val} Stars`;
  }
}

/**
 * Fetch feedback and reviews from backend
 */
window.loadFeedback = async function() {
  const container = document.getElementById('feedbackReviewsList');
  if (!container) return;

  try {
    const res = await fetch('/api/feedback');
    const data = await res.json();
    if (data.success && data.data) {
      const { items, avg_rating, total_count } = data.data;

      const avgRatingEl = document.getElementById('feedbackAvgScore');
      const totalCountEl = document.getElementById('feedbackTotalCount');

      if (avgRatingEl) avgRatingEl.innerText = avg_rating.toFixed(1);
      if (totalCountEl) totalCountEl.innerText = `${total_count} Community Reviews`;

      if (items.length === 0) {
        container.innerHTML = `
          <div class="text-center py-4 text-muted">
            <p>No feedback submitted yet. Share your experience!</p>
          </div>
        `;
        return;
      }

      container.innerHTML = items.map(fb => {
        const starIcons = '★'.repeat(fb.rating) + '☆'.repeat(5 - fb.rating);
        return `
          <div class="feedback-review-card eco-card">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <div>
                <strong>${escapeHtml(fb.user_name)}</strong>
                <span class="badge bg-light text-secondary border small ms-2">${escapeHtml(fb.role)}</span>
              </div>
              <div class="text-warning fw-bold fs-5">${starIcons}</div>
            </div>
            <div class="badge bg-success-subtle text-success small mb-2">${escapeHtml(fb.category)}</div>
            <p class="text-muted small mb-1">${escapeHtml(fb.message)}</p>
            <div class="text-end text-muted" style="font-size:0.75rem;">
              ${fb.created_at ? fb.created_at.substring(0, 10) : 'Recent'}
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    console.error("Failed to load feedback:", err);
  }
};

/**
 * Submit user feedback
 */
async function submitFeedback() {
  const nameInput = document.getElementById('feedbackName');
  const roleSelect = document.getElementById('feedbackRole');
  const catSelect = document.getElementById('feedbackCategory');
  const msgInput = document.getElementById('feedbackMessage');
  const submitBtn = document.getElementById('feedbackSubmitBtn');

  if (!msgInput) return;

  const name = nameInput.value.trim() || 'Campus Member';
  const role = roleSelect.value || 'Student';
  const category = catSelect.value || 'General Suggestion';
  const message = msgInput.value.trim();

  if (!message) {
    showEcoToast("Please write a short message or suggestion.", "info");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';

  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_name: name,
        role: role,
        rating: selectedRating,
        category: category,
        message: message
      })
    });

    const data = await res.json();
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-send me-1"></i>Submit Feedback';

    if (data.success) {
      showEcoToast("Thank you for your valuable feedback! 🌿", "success");
      msgInput.value = '';
      window.loadFeedback();
    } else {
      showEcoToast(data.error || "Failed to submit feedback", "info");
    }
  } catch (err) {
    console.error("Feedback submission error:", err);
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-send me-1"></i>Submit Feedback';
    showEcoToast("Server connection error.", "info");
  }
}
