(function() {
  'use strict';

  // ============================================================
  // THEME TOGGLE
  // ============================================================
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;
  const stored = localStorage.getItem('theme');
  if (stored) html.setAttribute('data-theme', stored);
  else if (window.matchMedia('(prefers-color-scheme: dark)').matches) html.setAttribute('data-theme', 'dark');

  themeToggle.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });

  // ============================================================
  // SIDEBAR TOGGLE (mobile)
  // ============================================================
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
  // close sidebar on outside click
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });

  // ============================================================
  // CLOCK
  // ============================================================
  function updateClock() {
    const now = new Date();
    document.getElementById('clockDisplay').textContent = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('dateDisplay').textContent = now.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
  setInterval(updateClock, 1000);
  updateClock();

  // ============================================================
  // COPYRIGHT YEAR
  // ============================================================
  document.getElementById('currentYear').textContent = new Date().getFullYear();

  // ============================================================
  // CSRF TOKEN HELPER
  // ============================================================
  function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const c = cookies[i].trim();
        if (c.substring(0, name.length + 1) === (name + '=')) {
          value = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return value;
  }

  // ============================================================
  // LOGOUT
  // ============================================================
  document.getElementById('logoutBtn').addEventListener('click', async () => {
    const btn = document.getElementById('logoutBtn');
    btn.disabled = true;
    btn.textContent = 'Logging out…';
    try {
      const res = await fetch('/admin/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({})
      });
      if (res.ok) {
        document.body.innerHTML = `
          <div style="height:100vh;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:700;background:var(--bg);color:var(--text);">
            Session terminated.
          </div>
        `;
      } else {
        alert('Logout failed. Please refresh.');
      }
    } catch (err) {
      alert('Network error during logout.');
    }
    btn.disabled = false;
    btn.textContent = 'Logout';
  });

  // ============================================================
  // TELEMETRY FETCH (users count)
  // ============================================================
  async function fetchTelemetry(endpoint, key, targetId) {
    const el = document.getElementById(targetId);
    el.textContent = '…';
    try {
      const res = await fetch(endpoint);
      const data = await res.json();
      el.textContent = data[key] !== undefined ? data[key] : 'Err';
    } catch (err) {
      el.textContent = '—';
    }
  }

  document.getElementById('refreshTotalUsersBtn').addEventListener('click', () => {
    fetchTelemetry('/allUser/', 'all_user', 'totalUsersCount');
  });
  document.getElementById('refreshActiveUsersBtn').addEventListener('click', () => {
    fetchTelemetry('/allActiveUser/', 'active_user', 'activeUsersCount');
  });

  // Initial load
  fetchTelemetry('/allUser/', 'all_user', 'totalUsersCount');
  fetchTelemetry('/allActiveUser/', 'active_user', 'activeUsersCount');

  // ============================================================
  // BROADCAST EMAIL
  // ============================================================
  document.getElementById('sendMailBtn').addEventListener('click', async () => {
    const body = document.getElementById('emailBody').value.trim();
    if (!body) {
      alert('Please enter a message.');
      return;
    }
    const btn = document.getElementById('sendMailBtn');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    try {
      const res = await fetch('/send-broadcast/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ message: body })
      });
      const data = await res.json();
      if (res.ok) {
        alert('Broadcast sent successfully!');
        document.getElementById('emailBody').value = '';
      } else {
        alert('Error: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Network error. Please try again.');
    }
    btn.disabled = false;
    btn.textContent = 'Send to All Users';
  });

})();