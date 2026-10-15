/**
 * Dashboard & Analytics Module.
 * Integrates Chart.js visualizations, animated statistic counters,
 * resource conservation metrics, and the real-time campus activity feed.
 */

let activityChartInstance = null;
let resourceChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  // Initial load if starting on dashboard
  if (EcoApp.activeTab === 'dashboard') {
    window.loadDashboard();
  }
});

/**
 * Load dashboard statistics and render charts
 */
window.loadDashboard = async function() {
  try {
    const [statsRes, activitiesRes] = await Promise.all([
      fetch('/api/dashboard/stats'),
      fetch('/api/activities?limit=10')
    ]);

    const statsData = await statsRes.json();
    const activitiesData = await activitiesRes.json();

    if (statsData.success && statsData.stats) {
      updateDashboardCards(statsData.stats);
      renderActivityChart(statsData.stats.type_breakdown);
      renderResourceChart(statsData.stats.impact_estimates);
    }

    if (activitiesData.success && activitiesData.activities) {
      renderActivityFeed(activitiesData.activities);
    }
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
};

/**
 * Update dashboard counter numbers
 */
function updateDashboardCards(stats) {
  const tipsEl = document.getElementById('dashTotalTips');
  const activitiesEl = document.getElementById('dashTotalActivities');
  const challengesEl = document.getElementById('dashCompletedChallenges');
  const plasticEl = document.getElementById('dashPlasticSaved');
  const waterEl = document.getElementById('dashWaterSaved');
  const energyEl = document.getElementById('dashEnergySaved');
  const treesEl = document.getElementById('dashTreesPlanted');

  if (tipsEl) tipsEl.innerText = stats.total_tips;
  if (activitiesEl) activitiesEl.innerText = stats.total_activities;
  if (challengesEl) challengesEl.innerText = `${stats.completed_challenges} / ${stats.total_challenges}`;

  if (stats.impact_estimates) {
    if (plasticEl) plasticEl.innerText = stats.impact_estimates.plastic_bottles_saved.toLocaleString();
    if (waterEl) waterEl.innerText = stats.impact_estimates.water_saved_liters.toLocaleString() + ' L';
    if (energyEl) energyEl.innerText = stats.impact_estimates.kwh_energy_saved.toLocaleString() + ' kWh';
    if (treesEl) treesEl.innerText = stats.impact_estimates.trees_planted.toLocaleString();
  }

  // Update Hero counters as well if present
  const heroPlastic = document.getElementById('heroPlasticCount');
  const heroWater = document.getElementById('heroWaterCount');
  const heroEnergy = document.getElementById('heroEnergyCount');
  const heroTrees = document.getElementById('heroTreesCount');

  if (heroPlastic && stats.impact_estimates) heroPlastic.innerText = stats.impact_estimates.plastic_bottles_saved.toLocaleString();
  if (heroWater && stats.impact_estimates) heroWater.innerText = stats.impact_estimates.water_saved_liters.toLocaleString() + ' L';
  if (heroEnergy && stats.impact_estimates) heroEnergy.innerText = stats.impact_estimates.kwh_energy_saved.toLocaleString() + ' kWh';
  if (heroTrees && stats.impact_estimates) heroTrees.innerText = stats.impact_estimates.trees_planted.toLocaleString();
}

/**
 * Render Doughnut Chart for Activity Type Breakdown
 */
function renderActivityChart(typeBreakdown) {
  const canvas = document.getElementById('activityBreakdownChart');
  if (!canvas) return;

  const labels = typeBreakdown.map(item => item.activity_type);
  const dataValues = typeBreakdown.map(item => item.count);

  const colors = [
    '#2d6a4f',
    '#52b788',
    '#74c69d',
    '#b7e4c7',
    '#e9c46a',
    '#3a86ff',
    '#f4a261'
  ];

  if (activityChartInstance) {
    activityChartInstance.destroy();
  }

  activityChartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: dataValues,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { family: 'Plus Jakarta Sans', size: 12 }
          }
        }
      },
      cutout: '65%'
    }
  });
}

/**
 * Render Bar Chart for Resource Conservation Estimates
 */
function renderResourceChart(estimates) {
  const canvas = document.getElementById('resourceSavingsChart');
  if (!canvas || !estimates) return;

  if (resourceChartInstance) {
    resourceChartInstance.destroy();
  }

  resourceChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['Plastic Bottles Diverted', 'Water Saved (Liters / 10)', 'Energy Conserved (kWh)', 'Trees Planted (x10)'],
      datasets: [{
        label: 'Cumulative Campus Impact Metric',
        data: [
          estimates.plastic_bottles_saved,
          Math.round(estimates.water_saved_liters / 10),
          estimates.kwh_energy_saved,
          estimates.trees_planted * 10
        ],
        backgroundColor: [
          'rgba(45, 106, 79, 0.85)',
          'rgba(58, 134, 255, 0.85)',
          'rgba(233, 196, 106, 0.85)',
          'rgba(82, 183, 136, 0.85)'
        ],
        borderColor: [
          '#1b4332',
          '#2563eb',
          '#d97706',
          '#2d6a4f'
        ],
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0, 0, 0, 0.05)' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

/**
 * Render the list of recent campus activity records
 */
function renderActivityFeed(activities) {
  const container = document.getElementById('recentActivitiesContainer');
  if (!container) return;

  if (activities.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4 text-muted">
        <p>No campus activities recorded yet. Be the first to log an eco-activity!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = activities.map(act => {
    const roleLower = (act.role || 'student').toLowerCase();
    const roleClass = `role-${roleLower}`;

    return `
      <div class="activity-feed-item">
        <div class="stat-icon" style="background:#e8f7ee; color:#1b4332; width:44px; height:44px; font-size:1.2rem;">
          <i class="bi bi-patch-check-fill"></i>
        </div>
        <div class="flex-grow-1">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <div>
              <strong>${escapeHtml(act.student_name)}</strong>
              <span class="activity-role-badge ${roleClass} ms-2">${escapeHtml(act.role)}</span>
            </div>
            <small class="text-muted">${act.created_at ? act.created_at.substring(0, 10) : 'Today'}</small>
          </div>
          <p class="mb-1 text-dark small">${escapeHtml(act.description)}</p>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-light text-success border small"><i class="bi bi-tag me-1"></i>${escapeHtml(act.activity_type)}</span>
            <span class="badge bg-success-subtle text-success small"><i class="bi bi-lightning-charge me-1"></i>${escapeHtml(act.impact_value)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}
