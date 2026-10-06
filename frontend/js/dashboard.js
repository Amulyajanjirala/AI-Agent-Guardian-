/**
 * AI Agent Guardian - Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Check auth
  const token = GuardianAPI.getAuthToken();
  if (!token) {
    window.location.href = '/login.html';
    return;
  }

  await loadDashboardData();

  // Setup refresh button if present
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', async () => {
      refreshBtn.textContent = 'Refreshing...';
      await loadDashboardData();
      refreshBtn.textContent = '🔄 Refresh Telemetry';
    });
  }

  // Setup modal close handler
  const modalOverlay = document.getElementById('agent-modal');
  const modalCloseBtn = document.getElementById('modal-close');
  if (modalCloseBtn && modalOverlay) {
    modalCloseBtn.addEventListener('click', () => {
      modalOverlay.classList.remove('active');
    });
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        modalOverlay.classList.remove('active');
      }
    });
  }
});

async function loadDashboardData() {
  try {
    const data = await GuardianAPI.getDashboard();

    // Update Top Stat Cards
    const totalAgentsEl = document.getElementById('stat-total-agents');
    const activeAgentsEl = document.getElementById('stat-active-agents');
    const totalEventsEl = document.getElementById('stat-total-events');
    const highRiskEl = document.getElementById('stat-high-risk');

    if (totalAgentsEl) totalAgentsEl.textContent = data.total_agents;
    if (activeAgentsEl) activeAgentsEl.textContent = data.active_agents;
    if (totalEventsEl) totalEventsEl.textContent = data.security_events_count;
    if (highRiskEl) highRiskEl.textContent = data.high_risk_agents;

    // Render Agents Overview Table
    renderAgentsTable(data.agents_overview);

    // Render Recent Events Stream
    renderEventsStream(data.recent_alerts);

  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

function renderAgentsTable(agents) {
  const tableBody = document.getElementById('agents-table-body');
  if (!tableBody) return;

  tableBody.innerHTML = '';

  if (!agents || agents.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px;">No agents registered yet.</td></tr>';
    return;
  }

  agents.forEach(agent => {
    const tr = document.createElement('tr');
    
    const riskLevelClass = `badge-${agent.risk_level.toLowerCase()}`;
    const statusClass = `badge-${agent.status.toLowerCase()}`;
    const lastActive = formatRelativeTime(agent.last_activity);

    tr.innerHTML = `
      <td>
        <div class="agent-cell-name">
          <span>${escapeHtml(agent.name)}</span>
          <span class="agent-cell-id">${escapeHtml(agent.id)}</span>
        </div>
      </td>
      <td>
        <span class="badge ${statusClass}">${escapeHtml(agent.status)}</span>
      </td>
      <td>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-family:var(--font-mono); font-weight:700;">${agent.risk_score}</span>
          <span style="color:var(--text-muted); font-size:0.75rem;">/100</span>
        </div>
        <div class="risk-bar-container">
          <div class="risk-bar ${agent.risk_level.toLowerCase()}" style="width: ${agent.risk_score}%"></div>
        </div>
      </td>
      <td>
        <span class="badge ${riskLevelClass}">${escapeHtml(agent.risk_level)}</span>
      </td>
      <td style="font-size:0.8rem; font-family:var(--font-mono);">${lastActive}</td>
      <td>
        <button class="btn btn-secondary" style="padding:4px 10px; font-size:0.75rem;" onclick="inspectAgent('${agent.id}')">
          🔍 Inspect
        </button>
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

function renderEventsStream(events) {
  const feedContainer = document.getElementById('events-stream');
  if (!feedContainer) return;

  feedContainer.innerHTML = '';

  if (!events || events.length === 0) {
    feedContainer.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:20px;">No security events recorded.</div>';
    return;
  }

  events.forEach(evt => {
    const item = document.createElement('div');
    item.className = 'event-item';
    const sevClass = `badge-${evt.severity.toLowerCase()}`;
    const timeAgo = formatRelativeTime(evt.timestamp);

    item.innerHTML = `
      <div class="event-top-row">
        <div class="event-title">
          <span class="badge ${sevClass}">${escapeHtml(evt.severity)}</span>
          <span>${formatEventType(evt.event_type)}</span>
        </div>
        <span class="event-time">${timeAgo}</span>
      </div>
      <div class="event-desc">${escapeHtml(evt.description)}</div>
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.72rem;">
        <span style="color:var(--text-muted);">Target: <strong>${escapeHtml(evt.agent_name || evt.agent_id)}</strong></span>
        <span class="event-source-tag">[${escapeHtml(evt.source)}]</span>
      </div>
    `;
    feedContainer.appendChild(item);
  });
}

async function inspectAgent(agentId) {
  try {
    const data = await GuardianAPI.getAgentDetails(agentId);
    const modal = document.getElementById('agent-modal');
    const content = document.getElementById('modal-agent-content');
    if (!modal || !content) return;

    const explanation = data.risk_explanation || {};
    const reasons = explanation.reasons || [];
    const breakdown = explanation.severity_breakdown || {};

    content.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
        <div>
          <h2 style="font-size:1.4rem; color:#fff; margin-bottom:4px;">${escapeHtml(data.name)}</h2>
          <div style="display:flex; gap:8px; align-items:center;">
            <span class="badge badge-${data.status.toLowerCase()}">${escapeHtml(data.status)}</span>
            <span style="color:var(--text-muted); font-size:0.8rem; font-family:var(--font-mono);">${escapeHtml(data.id)}</span>
            <span style="color:var(--text-muted); font-size:0.8rem;">• ${escapeHtml(data.agent_type)}</span>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:1.8rem; font-weight:800; font-family:var(--font-mono); color:#fff;">
            ${data.risk_score}<span style="font-size:1rem; color:var(--text-muted);">/100</span>
          </div>
          <span class="badge badge-${data.risk_level.toLowerCase()}">${escapeHtml(data.risk_level)} RISK</span>
        </div>
      </div>

      <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:20px; line-height:1.5;">
        ${escapeHtml(data.description || 'No agent description provided.')}
      </p>

      <div style="background:#090f1a; border:1px solid var(--border-color); border-radius:var(--radius-sm); padding:16px; margin-bottom:20px;">
        <h4 style="font-size:0.85rem; color:var(--accent-cyan); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">
          🛡️ Risk Engine Explanation
        </h4>
        <ul style="list-style:none; display:flex; flex-direction:column; gap:6px; font-size:0.85rem; color:var(--text-secondary);">
          ${reasons.map(r => `<li>⚠️ ${escapeHtml(r)}</li>`).join('')}
        </ul>
      </div>

      <div style="background:#090f1a; border:1px solid var(--border-color); border-radius:var(--radius-sm); padding:16px; margin-bottom:20px;">
        <h4 style="font-size:0.85rem; color:#10b981; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">
          📋 Guardian Security Recommendation
        </h4>
        <p style="font-size:0.85rem; color:var(--text-primary);">
          ${escapeHtml(explanation.recommendation || 'Maintain normal surveillance.')}
        </p>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">
        <span style="font-size:0.8rem; color:var(--text-muted);">
          Events Analyzed: ${data.events ? data.events.length : 0}
        </span>
        <a href="/chat.html?agent=${encodeURIComponent(data.name)}" class="btn btn-cyber" style="padding:6px 14px; font-size:0.82rem;">
          💬 Ask Guardian About This Agent
        </a>
      </div>
    `;

    modal.classList.add('active');
  } catch (err) {
    console.error('Failed to load agent details:', err);
  }
}

window.inspectAgent = inspectAgent;

// Utility Helpers
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatEventType(type) {
  if (!type) return 'Security Event';
  return type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return 'Unknown';
  const date = new Date(dateStr);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);

  if (diffSec < 60) return 'Just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}
