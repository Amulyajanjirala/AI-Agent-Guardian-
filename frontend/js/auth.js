/**
 * AI Agent Guardian - Authentication Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');

  // Handle Login Form
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById('username');
      const passwordInput = document.getElementById('password');
      const rememberCheckbox = document.getElementById('remember-me');
      const submitBtn = loginForm.querySelector('button[type="submit"]');

      const username_or_email = usernameInput.value.trim();
      const password = passwordInput.value;
      const remember_me = rememberCheckbox ? rememberCheckbox.checked : false;

      if (!username_or_email || !password) {
        GuardianAPI.showToast('Please enter both username/email and password.', 'error');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Verifying Credentials...';

      try {
        const response = await GuardianAPI.login({
          username_or_email,
          password,
          remember_me
        });

        if (response.success && response.token) {
          GuardianAPI.setAuthToken(response.token, remember_me);
          localStorage.setItem('guardian_user', JSON.stringify(response.user));
          GuardianAPI.showToast('Authentication successful. Initializing Guardian...', 'success');
          setTimeout(() => {
            window.location.href = '/dashboard.html';
          }, 600);
        }
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In to Guardian';
      }
    });
  }

  // Handle User Header Display & Logout on Protected Pages
  const userProfileEl = document.getElementById('user-profile-display');
  const logoutBtn = document.getElementById('logout-btn');

  if (userProfileEl) {
    const cachedUser = localStorage.getItem('guardian_user');
    if (cachedUser) {
      try {
        const user = JSON.parse(cachedUser);
        const nameEl = userProfileEl.querySelector('.user-name');
        const roleEl = userProfileEl.querySelector('.user-role');
        const avatarEl = userProfileEl.querySelector('.user-avatar');

        if (nameEl) nameEl.textContent = user.username;
        if (roleEl) roleEl.textContent = (user.role || 'Admin').toUpperCase();
        if (avatarEl) avatarEl.textContent = user.username.substring(0, 2).toUpperCase();
      } catch (e) {}
    }
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      GuardianAPI.clearAuthToken();
      localStorage.removeItem('guardian_user');
      GuardianAPI.showToast('Logged out securely.', 'info');
      setTimeout(() => {
        window.location.href = '/login.html';
      }, 400);
    });
  }
});
