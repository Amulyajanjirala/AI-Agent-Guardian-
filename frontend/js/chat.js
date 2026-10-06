/**
 * AI Agent Guardian - Chat Interface Logic
 */

let currentSessionId = null;

document.addEventListener('DOMContentLoaded', async () => {
  const token = GuardianAPI.getAuthToken();
  if (!token) {
    window.location.href = '/login.html';
    return;
  }

  // Load mini agent fleet status in sidebar
  await loadMiniAgentStatus();

  // Load chat session history
  await loadSessions();

  // Setup Chat Form
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');

  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;
      chatInput.value = '';
      await sendMessage(message);
    });
  }

  // Setup Prompt Chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const prompt = btn.getAttribute('data-prompt') || btn.textContent.trim();
      await sendMessage(prompt);
    });
  });

  // Check URL params for direct agent inquiry
  const params = new URLSearchParams(window.location.search);
  const targetAgent = params.get('agent');
  if (targetAgent) {
    await sendMessage(`Why is ${targetAgent} risky?`);
  }
});

async function loadMiniAgentStatus() {
  try {
    const agents = await GuardianAPI.getAgents();
    const container = document.getElementById('agent-mini-list');
    if (!container) return;

    container.innerHTML = '';
    agents.forEach(a => {
      const div = document.createElement('div');
      div.className = 'agent-mini-row';
      div.innerHTML = `
        <span style="font-weight:500;">${escapeHtml(a.name)}</span>
        <span class="badge badge-${a.risk_level.toLowerCase()}">${a.risk_score} ${a.risk_level}</span>
      `;
      div.style.cursor = 'pointer';
      div.onclick = () => sendMessage(`Why is ${a.name} ${a.risk_level.toLowerCase()} risk?`);
      container.appendChild(div);
    });
  } catch (err) {
    console.error('Failed to load mini agent list:', err);
  }
}

async function loadSessions() {
  try {
    const sessions = await GuardianAPI.getChatSessions();
    const list = document.getElementById('session-list');
    if (!list) return;

    list.innerHTML = '';
    sessions.forEach(sess => {
      const li = document.createElement('li');
      li.className = `session-item ${sess.id === currentSessionId ? 'active' : ''}`;
      li.innerHTML = `
        <span class="session-name">${escapeHtml(sess.title || 'Security Conversation')}</span>
        <span class="session-meta">${formatDate(sess.created_at)}</span>
      `;
      li.onclick = () => selectSession(sess.id);
      list.appendChild(li);
    });
  } catch (err) {
    console.error('Failed to load sessions:', err);
  }
}

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  await loadSessions();

  try {
    const messages = await GuardianAPI.getChatHistory(sessionId);
    const container = document.getElementById('messages-stream');
    if (!container) return;

    container.innerHTML = '';
    messages.forEach(msg => {
      let metadata = null;
      if (msg.metadata_json) {
        try { metadata = JSON.parse(msg.metadata_json); } catch (e) {}
      }
      renderMessage(msg.sender, msg.message, msg.intent, metadata, msg.timestamp);
    });
    scrollToBottom();
  } catch (err) {
    console.error('Failed to load session messages:', err);
  }
}

async function sendMessage(text) {
  const container = document.getElementById('messages-stream');
  if (!container) return;

  // Render User Message immediately
  renderMessage('user', text, null, null, new Date().toISOString());
  scrollToBottom();

  // Render Typing Placeholder
  const typingIndicator = document.createElement('div');
  typingIndicator.className = 'msg-row guardian';
  typingIndicator.id = 'typing-indicator';
  typingIndicator.innerHTML = `
    <div class="msg-avatar guardian">AG</div>
    <div class="msg-content-box">
      <div class="msg-bubble" style="color:var(--text-muted); font-size:0.85rem;">
        ⚡ Analyzing security intent and evaluating agent metrics...
      </div>
    </div>
  `;
  container.appendChild(typingIndicator);
  scrollToBottom();

  try {
    const res = await GuardianAPI.sendChatMessage(text, currentSessionId);
    typingIndicator.remove();

    currentSessionId = res.session_id;

    // Render Guardian Message with structured payload
    renderMessage('guardian', res.response, res.intent, res.data, new Date().toISOString());
    scrollToBottom();

    // Refresh session list
    loadSessions();
  } catch (err) {
    typingIndicator.remove();
    renderMessage('guardian', `Security Error: Unable to query Guardian backend. ${err.message}`, 'ERROR');
    scrollToBottom();
  }
}

function renderMessage(sender, text, intent = null, data = null, timestamp = null) {
  const container = document.getElementById('messages-stream');
  if (!container) return;

  const row = document.createElement('div');
  row.className = `msg-row ${sender}`;

  const avatarLabel = sender === 'guardian' ? 'AG' : 'ME';
  const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  let structuredHtml = '';
  if (sender === 'guardian' && Array.isArray(data) && data.length > 0) {
    structuredHtml = renderStructuredDataCards(intent, data);
  }

  row.innerHTML = `
    <div class="msg-avatar ${sender}">${avatarLabel}</div>
    <div class="msg-content-box">
      <div class="msg-bubble">
        ${escapeHtml(text)}
        ${structuredHtml}
      </div>
      <div class="msg-meta">
        ${intent ? `<span class="intent-pill">INTENT: ${escapeHtml(intent)}</span>` : ''}
        <span>${timeStr}</span>
      </div>
    </div>
  `;

  container.appendChild(row);
}

function renderStructuredDataCards(intent, data) {
  if (intent === 'GET_HIGH_RISK_AGENTS' || intent === 'GET_AGENTS') {
    return `
      <div class="chat-card-container">
        ${data.map(agent => `
          <div class="chat-agent-card">
            <div class="chat-agent-header">
              <span class="chat-agent-title">${escapeHtml(agent.name)}</span>
              <span class="badge badge-${agent.risk_level.toLowerCase()}">${agent.risk_score} ${agent.risk_level}</span>
            </div>
            <div style="font-size:0.78rem; color:var(--text-muted); display:flex; justify-content:space-between;">
              <span>Type: ${escapeHtml(agent.agent_type || 'general')}</span>
              <span>Status: ${escapeHtml(agent.status)}</span>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  if (intent === 'GET_AGENT_RISK' && data.length > 0) {
    const item = data[0];
    const reasons = item.reasons || [];
    return `
      <div class="chat-card-container">
        <div class="chat-agent-card">
          <div class="chat-agent-header">
            <span class="chat-agent-title">Risk Analysis: ${escapeHtml(item.name || item.id)}</span>
            <span class="badge badge-${item.risk_level.toLowerCase()}">${item.risk_score} ${item.risk_level}</span>
          </div>
          ${reasons.length > 0 ? `
            <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:4px;">
              <strong>Key Risk Factors:</strong>
              <ul style="margin-left:16px; margin-top:4px;">
                ${reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.recommendation ? `
            <div style="font-size:0.78rem; color:#10b981; margin-top:6px; border-top:1px solid rgba(255,255,255,0.06); padding-top:6px;">
              🛡️ <strong>Recommendation:</strong> ${escapeHtml(item.recommendation)}
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  if (intent === 'GET_SECURITY_EVENTS' && data.length > 0) {
    return `
      <div class="chat-card-container">
        ${data.slice(0, 4).map(evt => `
          <div class="chat-agent-card" style="border-left-color: var(--sev-${evt.severity.toLowerCase()});">
            <div class="chat-agent-header">
              <span class="badge badge-${evt.severity.toLowerCase()}">${escapeHtml(evt.severity)}</span>
              <span style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">${formatRelativeTime(evt.timestamp)}</span>
            </div>
            <div style="font-size:0.82rem; color:#fff; font-weight:500; margin-top:4px;">${escapeHtml(evt.description)}</div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Target: ${escapeHtml(evt.agent_id)} • Source: ${escapeHtml(evt.source)}</div>
          </div>
        `).join('')}
      </div>
    `;
  }

  if (intent === 'UNKNOWN' && data.length > 0) {
    return `
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">
        ${data.map(d => `
          <button class="chip-btn" onclick="sendMessage('${escapeHtml(d.suggestion)}')">${escapeHtml(d.suggestion)}</button>
        `).join('')}
      </div>
    `;
  }

  return '';
}

function scrollToBottom() {
  const container = document.getElementById('messages-stream');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

window.sendMessage = sendMessage;

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffSec = Math.floor((now - date) / 1000);
  if (diffSec < 60) return 'Just now';
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}
