(function() {
  'use strict';

  // ============================================================
  // THEME TOGGLE
  // ============================================================
  const themeToggle = document.getElementById('themeToggle');
  const htmlEl = document.documentElement;

  const savedTheme = localStorage.getItem('theme');
  const preferDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme) {
    htmlEl.setAttribute('data-theme', savedTheme);
  } else {
    htmlEl.setAttribute('data-theme', preferDark ? 'dark' : 'light');
  }

  themeToggle.addEventListener('click', () => {
    const currentTheme = htmlEl.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    htmlEl.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  });

  // ============================================================
  // CANONICAL URL (set to current page)
  // ============================================================
  const canonical = document.querySelector('link[rel="canonical"]');
  if (canonical) {
    canonical.href = window.location.href.split('?')[0]; // clean version
  }

  // ============================================================
  // ACTION BAR SCROLL BEHAVIOR
  // ============================================================
  const ctaSection = document.getElementById('ctaSection');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    if (scrollY > 300) {
      ctaSection.classList.add('visible');
    } else {
      ctaSection.classList.remove('visible');
    }
    lastScroll = scrollY;
  }, { passive: true });

  // ============================================================
  // HERO RING ANIMATION
  // ============================================================
  function animateRing() {
    const ring = document.getElementById('progressRing');
    const pctLabel = document.getElementById('ringPct');
    if (!ring || !pctLabel) return;

    const circumference = 351.86;
    const target = 92; // percentage
    let started = false;

    function run() {
      if (started) return;
      started = true;
      const duration = 1400;
      const start = performance.now();

      function frame(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        const current = Math.round(eased * target);
        pctLabel.textContent = current + '%';
        ring.style.strokeDashoffset = circumference - (eased * target / 100) * circumference;
        if (t < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    const demoEl = document.querySelector('.demo-card');
    if ('IntersectionObserver' in window && demoEl) {
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) { run(); obs.disconnect(); } });
      }, { threshold: 0.3 });
      obs.observe(demoEl);
    } else {
      run();
    }
  }
  animateRing();

  // ============================================================
  // STATS COUNT-UP
  // ============================================================
  function animateCounts() {
    const nums = document.querySelectorAll('.stat-block .num');
    if (!nums.length) return;

    function runCount(el) {
      const target = parseInt(el.getAttribute('data-count'), 10) || 0;
      const suffix = el.getAttribute('data-suffix') || '';
      const duration = 1300;
      const start = performance.now();

      function frame(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        el.textContent = Math.round(eased * target) + suffix;
        if (t < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            runCount(e.target);
            obs.unobserve(e.target);
          }
        });
      }, { threshold: 0.4 });
      nums.forEach(n => obs.observe(n));
    } else {
      nums.forEach(runCount);
    }
  }
  animateCounts();

  // ============================================================
  // ROBOT CUSTOMER CARE LAUNCHER
  // ============================================================
  function setupBot() {
    const botBtn = document.getElementById('botBtn');
    const botSpeech = document.getElementById('botSpeech');
    if (!botBtn) return;

    const greeting =
      "This is Dev Ope, the founder of LectureTracker 👋 How can we help you today?";

    botBtn.addEventListener('click', () => {
      const text = encodeURIComponent(greeting);
      window.open(`https://wa.me/+2348113577875?text=${text}`, '_blank');
    });

    // Hide speech bubble after 8 seconds, but re‑show on hover
    setTimeout(() => {
      if (botSpeech) botSpeech.style.display = 'none';
    }, 8000);

    botBtn.addEventListener('mouseenter', () => {
      if (botSpeech) botSpeech.style.display = 'flex';
    });
    botBtn.addEventListener('mouseleave', () => {
      setTimeout(() => {
        if (botSpeech) botSpeech.style.display = 'none';
      }, 1600);
    });
  }
  setupBot();
})();