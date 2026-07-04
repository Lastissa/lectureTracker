(function () {
  'use strict';

  /* ============================================================
     CONFIG
     ============================================================ */
  var SIGNUP_ENDPOINT = '/backupData/json/';
  var REDIRECT_ON_SUCCESS = '/login/';
  var REQUEST_TIMEOUT_MS = 15000;
  var RING_CIRCUMFERENCE = 351.86; // 2 * PI * 56, matches the SVG radius

  /* ============================================================
     ELEMENTS
     ============================================================ */
  var form = document.getElementById('signupForm');
  var usernameInput = document.getElementById('username');
  var emailInput = document.getElementById('email');
  var passwordInput = document.getElementById('password');
  var confirmInput = document.getElementById('confirmPassword');
  var submitBtn = document.getElementById('submitBtn');
  var togglePasswordBtn = document.getElementById('togglePassword');

  var ring = document.getElementById('setupRing');
  var ringPctLabel = document.getElementById('ringPct');
  var setupPctLabel = document.getElementById('setupPctLabel');
  var checklist = document.getElementById('setupChecklist');

  var strengthFill = document.getElementById('strengthFill');
  var strengthLabel = document.getElementById('strengthLabel');

  var toastStack = document.getElementById('toastStack');

  if (!form) return; // fail quietly if the page markup ever changes

  /* ============================================================
     VALIDATION RULES
     (kept in sync with what the backend actually enforces, plus
     a couple of sane client-side extras)
     ============================================================ */
  function isNonEmpty(value) {
    return value.trim().length > 0;
  }

  function isGmail(value) {
    return /^[^\s@]+@gmail\.com$/i.test(value.trim());
  }

  function passwordMeetsMinimum(value) {
    // backend hard requirement is >= 2 characters; we ask for 6+ client-side
    // as good practice, but never block anything the backend would accept.
    return value.length >= 6;
  }

  function fieldState() {
    return {
      username: isNonEmpty(usernameInput.value),
      email: isGmail(emailInput.value),
      password: passwordMeetsMinimum(passwordInput.value)
    };
  }

  /* ============================================================
     SIGNATURE ELEMENT — SETUP RING + CHECKLIST
     ============================================================ */
  function updateSetupRing() {
    var state = fieldState();
    var doneCount = (state.username ? 1 : 0) + (state.email ? 1 : 0) + (state.password ? 1 : 0);
    var pct = Math.round((doneCount / 3) * 100);

    var offset = RING_CIRCUMFERENCE - (RING_CIRCUMFERENCE * pct) / 100;
    ring.style.strokeDashoffset = offset.toFixed(2);
    ring.style.stroke = pct === 100 ? 'var(--success)' : 'var(--accent)';

    ringPctLabel.textContent = pct + '%';
    setupPctLabel.textContent = pct + '%';

    Object.keys(state).forEach(function (key) {
      var li = checklist.querySelector('[data-field="' + key + '"]');
      if (!li) return;
      li.classList.toggle('done', state[key]);
    });
  }

  /* ============================================================
     PASSWORD STRENGTH (visual only, never blocks submission)
     ============================================================ */
  function updateStrengthMeter() {
    var value = passwordInput.value;
    var score = 0;
    if (value.length >= 6) score++;
    if (value.length >= 10) score++;
    if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++;
    if (/\d/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;

    var pct = value.length === 0 ? 0 : Math.min(100, (score / 5) * 100);
    var label = '';
    var color = 'var(--danger)';

    if (value.length === 0) {
      label = '';
    } else if (score <= 1) {
      label = 'Weak';
      color = 'var(--danger)';
    } else if (score <= 3) {
      label = 'Fair';
      color = 'var(--warn)';
    } else {
      label = 'Strong';
      color = 'var(--success)';
    }

    strengthFill.style.width = pct + '%';
    strengthFill.style.background = color;
    strengthLabel.textContent = label;
  }

  /* ============================================================
     INLINE FIELD ERRORS
     ============================================================ */
  function setFieldError(input, errorEl, message) {
    if (message) {
      input.classList.add('invalid');
      input.classList.remove('valid');
      errorEl.textContent = message;
      errorEl.classList.add('show');
    } else {
      input.classList.remove('invalid');
      errorEl.classList.remove('show');
      errorEl.textContent = '';
    }
  }

  function markValid(input) {
    input.classList.remove('invalid');
    input.classList.add('valid');
  }

  function validateUsername(showError) {
    var value = usernameInput.value;
    var errorEl = document.getElementById('usernameError');
    if (!isNonEmpty(value)) {
      if (showError) setFieldError(usernameInput, errorEl, 'Username or email is required.');
      return false;
    }
    setFieldError(usernameInput, errorEl, '');
    markValid(usernameInput);
    return true;
  }

  function validateEmail(showError) {
    var value = emailInput.value;
    var errorEl = document.getElementById('emailError');
    if (!isNonEmpty(value)) {
      if (showError) setFieldError(emailInput, errorEl, 'Email is required.');
      return false;
    }
    if (!isGmail(value)) {
      if (showError) setFieldError(emailInput, errorEl, 'Please use a Gmail address (e.g. name@gmail.com).');
      return false;
    }
    setFieldError(emailInput, errorEl, '');
    markValid(emailInput);
    return true;
  }

  function validatePassword(showError) {
    var value = passwordInput.value;
    var errorEl = document.getElementById('passwordError');
    if (value.length < 2) {
      if (showError) setFieldError(passwordInput, errorEl, 'Password is required.');
      return false;
    }
    if (value.length < 6) {
      if (showError) setFieldError(passwordInput, errorEl, 'Use at least 6 characters for a stronger password.');
      return false;
    }
    setFieldError(passwordInput, errorEl, '');
    markValid(passwordInput);
    return true;
  }

  function validateConfirm(showError) {
    var errorEl = document.getElementById('confirmPasswordError');
    if (confirmInput.value.length === 0) {
      if (showError) setFieldError(confirmInput, errorEl, 'Please confirm your password.');
      return false;
    }
    if (confirmInput.value !== passwordInput.value) {
      if (showError) setFieldError(confirmInput, errorEl, 'Passwords do not match.');
      return false;
    }
    setFieldError(confirmInput, errorEl, '');
    markValid(confirmInput);
    return true;
  }

  function validateAll(showErrors) {
    var okUsername = validateUsername(showErrors);
    var okEmail = validateEmail(showErrors);
    var okPassword = validatePassword(showErrors);
    var okConfirm = validateConfirm(showErrors);
    return okUsername && okEmail && okPassword && okConfirm;
  }

  /* ============================================================
     LIVE LISTENERS
     ============================================================ */
  usernameInput.addEventListener('input', function () {
    validateUsername(false);
    updateSetupRing();
  });
  usernameInput.addEventListener('blur', function () { validateUsername(true); });

  emailInput.addEventListener('input', function () {
    validateEmail(false);
    updateSetupRing();
  });
  emailInput.addEventListener('blur', function () { validateEmail(true); });

  passwordInput.addEventListener('input', function () {
    validatePassword(false);
    updateStrengthMeter();
    updateSetupRing();
    if (confirmInput.value.length > 0) validateConfirm(true);
  });
  passwordInput.addEventListener('blur', function () { validatePassword(true); });

  confirmInput.addEventListener('input', function () { validateConfirm(false); });
  confirmInput.addEventListener('blur', function () { validateConfirm(true); });

  togglePasswordBtn.addEventListener('click', function () {
    var showing = togglePasswordBtn.classList.toggle('showing');
    var type = showing ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    confirmInput.setAttribute('type', type);
    togglePasswordBtn.setAttribute('aria-label', showing ? 'Hide password' : 'Show password');
  });

  /* ============================================================
     TOAST NOTIFICATIONS
     ============================================================ */
  var TOAST_ICONS = {
    success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
  };

  var TOAST_TITLES = {
    success: 'Success',
    error: 'Something went wrong',
    warning: 'Heads up',
    info: 'Notice'
  };

  function showToast(type, message, opts) {
    opts = opts || {};
    type = TOAST_ICONS[type] ? type : 'info';

    var toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');

    toast.innerHTML =
      '<span class="toast-icon">' + TOAST_ICONS[type] + '</span>' +
      '<div class="toast-body">' +
        '<p class="toast-title">' + (opts.title || TOAST_TITLES[type]) + '</p>' +
        '<p class="toast-msg"></p>' +
      '</div>' +
      '<button type="button" class="toast-close" aria-label="Dismiss notification">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
      '</button>';

    // set message via textContent (never innerHTML) so it's always displayed
    // safely and exactly as received, with no markup injection risk.
    toast.querySelector('.toast-msg').textContent = message;

    var dismissTimer;
    function dismiss() {
      clearTimeout(dismissTimer);
      toast.classList.remove('in');
      toast.classList.add('out');
      toast.addEventListener('transitionend', function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, { once: true });
    }

    toast.querySelector('.toast-close').addEventListener('click', dismiss);

    toastStack.appendChild(toast);
    requestAnimationFrame(function () { toast.classList.add('in'); });

    var duration = opts.duration || (type === 'error' ? 7000 : 5000);
    dismissTimer = setTimeout(dismiss, duration);

    return { dismiss: dismiss };
  }

  /* ============================================================
     CSRF HELPER (harmless no-op if the endpoint doesn't need it)
     ============================================================ */
  function getCookie(name) {
    var match = document.cookie.match('(^|;\\s*)(' + name + ')=([^;]*)');
    return match ? decodeURIComponent(match[3]) : null;
  }

  /* ============================================================
     RESPONSE MESSAGE EXTRACTION
     The backend is inconsistent about response shape: most views
     return {"message": "..."} but account creation returns a bare
     string. This normalizes both (and anything else) into a safe
     string we can always display.
     ============================================================ */
  function extractMessage(data, status) {
    if (typeof data === 'string' && data.trim().length > 0) {
      return data;
    }
    if (data && typeof data === 'object') {
      if (typeof data.message === 'string' && data.message.trim().length > 0) {
        return data.message;
      }
      if (typeof data.detail === 'string' && data.detail.trim().length > 0) {
        return data.detail;
      }
    }
    // last-resort fallback so the user is never shown a blank toast
    var fallbacks = {
      200: 'Updated successfully.',
      201: 'Account created successfully.',
      203: 'No new data to save.',
      400: 'Please check the details you entered.',
      401: 'Your session has expired. Please try again.',
      409: 'That account already exists with a different password.',
      500: 'Something went wrong on our end. Please try again shortly.'
    };
    return fallbacks[status] || ('Unexpected response (status ' + status + ').');
  }

  function toastTypeForStatus(status) {
    if (status >= 200 && status < 300) return 'success';
    if (status === 401 || status === 409) return 'warning';
    if (status >= 400 && status < 500) return 'error';
    return 'error';
  }

  /* ============================================================
     SUBMIT
     ============================================================ */
  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.classList.toggle('loading', isLoading);
  }

  function focusFirstInvalid() {
    var order = [
      [usernameInput, validateUsername],
      [emailInput, validateEmail],
      [passwordInput, validatePassword],
      [confirmInput, validateConfirm]
    ];
    for (var i = 0; i < order.length; i++) {
      if (!order[i][1](true)) {
        order[i][0].focus();
        return;
      }
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    if (submitBtn.disabled) return; // guard against double submit

    var valid = validateAll(true);
    updateSetupRing();

    if (!valid) {
      focusFirstInvalid();
      showToast('warning', 'Fix the highlighted fields before continuing.');
      return;
    }

    var payload = {
      username: usernameInput.value.trim(),
      email: emailInput.value.trim(),
      password: passwordInput.value,
      history: [],
      currentData: []
    };

    var controller = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    var timeoutId = controller ? setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT_MS) : null;

    var csrfToken = getCookie('csrftoken');
    var headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    setLoading(true);

    fetch(SIGNUP_ENDPOINT, {
      method: 'POST',
      headers: headers,
      credentials: 'same-origin',
      body: JSON.stringify(payload),
      signal: controller ? controller.signal : undefined
    })
      .then(function (response) {
        if (timeoutId) clearTimeout(timeoutId);

        // Read as text first so a non-JSON error page (e.g. a raw 500 HTML
        // page) never throws an unhandled parse error.
        return response.text().then(function (rawText) {
          var data = null;
          if (rawText && rawText.trim().length > 0) {
            try {
              data = JSON.parse(rawText);
            } catch (parseError) {
              data = rawText; // treat as a plain-text message
            }
          }
          return { status: response.status, ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        var message = extractMessage(result.data, result.status);
        var toastType = toastTypeForStatus(result.status);

        showToast(toastType, message);

        if (result.status === 201) {
          form.reset();
          updateSetupRing();
          updateStrengthMeter();
          setLoading(true); // keep it disabled through the redirect
          setTimeout(function () {
            window.location.href = REDIRECT_ON_SUCCESS;
          }, 1400);
          return; // don't re-enable the button before navigating away
        }

        if (result.status === 400) {
          // best-effort mapping of known backend messages to the field
          // that actually caused them, so the person knows what to fix
          var lower = (message || '').toLowerCase();
          if (lower.indexOf('email') !== -1) {
            setFieldError(emailInput, document.getElementById('emailError'), message);
          } else if (lower.indexOf('username') !== -1) {
            setFieldError(usernameInput, document.getElementById('usernameError'), message);
          } else if (lower.indexOf('password') !== -1) {
            setFieldError(passwordInput, document.getElementById('passwordError'), message);
          }
        }

        setLoading(false);
      })
      .catch(function (error) {
        if (timeoutId) clearTimeout(timeoutId);
        setLoading(false);

        if (error && error.name === 'AbortError') {
          showToast('error', 'The request took too long. Check your connection and try again.');
        } else {
          showToast('error', 'Could not reach the server. Check your connection and try again.');
        }
      });
  });

  /* ============================================================
     INIT
     ============================================================ */
  updateSetupRing();
  updateStrengthMeter();
})();