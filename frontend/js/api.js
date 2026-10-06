/**
 * AI Agent Guardian - Centralized API Client
 */

const API_BASE = window.location.origin;

class GuardianAPI {
  static getAuthToken() {
    return localStorage.getItem('guardian_token') || sessionStorage.getItem('guardian_token');
  }

  static setAuthToken(token, remember = false) {
    if (remember) {
      localStorage.setItem('guardian_token', token);
    } else {
      sessionStorage.setItem('guardian_token', token);
    }
  }

  static clearAuthToken() {
    localStorage.removeItem('guardian_token');
    sessionStorage.removeItem('guardian_token');
  }

  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const token = this.getAuthToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, { ...options, headers });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg = data.error?.message || `HTTP ${response.status}: Request failed`;
        if (response.status === 401 && !endpoint.includes('/login')) {
          // Token expired or invalid
          this.clearAuthToken();
          if (!window.location.pathname.includes('login.html')) {
            window.location.href = '/login.html';
          }
        }
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      GuardianAPI.showToast(err.message, 'error');
      throw err;
    }
  }

  static showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span>${type === 'error' ? '⚠️' : '🛡️'}</span>
      <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // API Methods
  static login(credentials) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
  }

  static getCurrentUser() {
    return this.request('/api/auth/me');
  }

  static getDashboard() {
    return this.request('/api/dashboard');
  }

  static getAgents() {
    return this.request('/api/agents');
  }

  static getAgentDetails(agentId) {
    return this.request(`/api/agents/${agentId}`);
  }

  static getEvents(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/api/events${qs ? '?' + qs : ''}`);
  }

  static getFleetRisk() {
    return this.request('/api/risk');
  }

  static sendChatMessage(message, sessionId = null) {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId })
    });
  }

  static getChatSessions() {
    return this.request('/api/chat/sessions');
  }

  static getChatHistory(sessionId) {
    return this.request(`/api/chat/history/${sessionId}`);
  }
}

window.GuardianAPI = GuardianAPI;
