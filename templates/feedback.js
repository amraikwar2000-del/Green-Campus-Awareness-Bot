/**
 * Feedback System Controller
 * Handles interactive 5-star rating, suggestion submissions, and community review display.
 */

const FeedbackController = (() => {
  let selectedRating = 5;

  const elements = {
    form: document.getElementById('feedbackForm'),
    starRatingBox: document.getElementById('starRatingBox'),
    inputRating: document.getElementById('feedbackRatingInput'),
    inputName: document.getElementById('feedbackName'),
    inputRole: document.getElementById('feedbackRole'),
    inputCategory: document.getElementById('feedbackCategory'),
    inputComment: document.getElementById('feedbackComment'),
    btnSubmit: document.getElementById('btnSubmitFeedback'),
    testimonialsContainer: document.getElementById('testimonialsContainer'),
    averageRatingText: document.getElementById('averageRatingText'),
    totalReviewsText: document.getElementById('totalReviewsText')
  };

  const init = () => {
    initStarRating();
    loadFeedbacks();

    if (elements.form) {
      elements.form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitFeedback();
      });
    }
  };

  const initStarRating = () => {
    if (!elements.starRatingBox) return;
    const stars = elements.starRatingBox.querySelectorAll('i');

    const updateStars = (val) => {
      stars.forEach((star) => {
        const starVal = parseInt(star.getAttribute('data-value'), 10);
        if (starVal <= val) {
          star.classList.remove('bi-star');
          star.classList.add('bi-star-fill', 'selected');
        } else {
          star.classList.remove('bi-star-fill', 'selected');
          star.classList.add('bi-star');
        }
      });
    };

    stars.forEach((star) => {
      star.addEventListener('mouseenter', () => {
        const hoverVal = parseInt(star.getAttribute('data-value'), 10);
        stars.forEach((s) => {
          const val = parseInt(s.getAttribute('data-value'), 10);
          if (val <= hoverVal) {
            s.classList.add('hovered');
          } else {
            s.classList.remove('hovered');
          }
        });
      });

      star.addEventListener('mouseleave', () => {
        stars.forEach((s) => s.classList.remove('hovered'));
      });

      star.addEventListener('click', () => {
        selectedRating = parseInt(star.getAttribute('data-value'), 10);
        if (elements.inputRating) elements.inputRating.value = selectedRating;
        updateStars(selectedRating);
      });
    });

    updateStars(selectedRating);
  };

  const loadFeedbacks = async () => {
    try {
      const response = await fetch('/api/feedback');
      const data = await response.json();

      if (elements.averageRatingText) elements.averageRatingText.textContent = `${data.average_rating} / 5.0`;
      if (elements.totalReviewsText) elements.totalReviewsText.textContent = `Based on ${data.total_count} campus ratings`;

      renderTestimonials(data.feedbacks || []);
    } catch (error) {
      console.error('Error loading feedback:', error);
    }
  };

  const renderTestimonials = (feedbacks) => {
    if (!elements.testimonialsContainer) return;
    elements.testimonialsContainer.innerHTML = '';

    if (feedbacks.length === 0) {
      elements.testimonialsContainer.innerHTML = `
        <div class="text-center py-4 text-muted">
          <p>No feedback submitted yet. Be the first to share your thoughts!</p>
        </div>
      `;
      return;
    }

    feedbacks.forEach((item) => {
      const bubble = document.createElement('div');
      bubble.className = 'testimonial-bubble';

      let starsHtml = '';
      for (let i = 1; i <= 5; i++) {
        if (i <= item.rating) {
          starsHtml += '<i class="bi bi-star-fill text-warning"></i>';
        } else {
          starsHtml += '<i class="bi bi-star text-muted"></i>';
        }
      }

      bubble.innerHTML = `
        <div class="d-flex align-items-center justify-content-between mb-2">
          <div>
            <strong class="d-block text-dark">${escapeHtml(item.user_name)}</strong>
            <span class="badge bg-success-subtle text-success small">${escapeHtml(item.user_role)}</span>
          </div>
          <div class="small">${starsHtml}</div>
        </div>
        <p class="text-secondary small mb-1">"${escapeHtml(item.comment)}"</p>
        <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top border-light">
          <span class="badge bg-light text-muted border">${escapeHtml(item.category)}</span>
          <small class="text-muted" style="font-size: 0.72rem;">${item.created_at ? item.created_at.slice(0, 10) : ''}</small>
        </div>
      `;

      elements.testimonialsContainer.appendChild(bubble);
    });
  };

  const submitFeedback = async () => {
    const comment = elements.inputComment.value.trim();
    if (!comment) {
      if (window.App) window.App.showToast("Please enter a short comment or suggestion.", "warning");
      return;
    }

    elements.btnSubmit.disabled = true;
    elements.btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Submitting...';

    try {
      const payload = {
        user_name: elements.inputName.value.trim() || 'Anonymous Student',
        user_role: elements.inputRole.value || 'Student',
        rating: selectedRating,
        category: elements.inputCategory.value || 'General',
        comment: comment
      };

      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      elements.btnSubmit.disabled = false;
      elements.btnSubmit.innerHTML = '<i class="bi bi-send-fill me-1"></i> Submit Feedback';

      if (response.ok && data.success) {
        elements.inputComment.value = '';
        if (window.App) {
          window.App.showToast("🌟 Thank you! Your feedback helps our campus stay green.", "success");
          if (window.App.refreshStats) window.App.refreshStats();
        }
        loadFeedbacks();
      } else {
        if (window.App) window.App.showToast(data.error || "Failed to submit feedback.", "danger");
      }
    } catch (error) {
      elements.btnSubmit.disabled = false;
      elements.btnSubmit.innerHTML = '<i class="bi bi-send-fill me-1"></i> Submit Feedback';
      console.error('Feedback submit error:', error);
      if (window.App) window.App.showToast("Could not submit feedback. Please check server connection.", "danger");
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
    loadFeedbacks
  };
})();
