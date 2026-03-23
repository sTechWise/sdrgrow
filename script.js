/* ============================================
   SDR GROW v3 — Interactive Behaviors
   Lightweight Vanilla JS — All bugs fixed
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Announcement Bar Dismiss ──
  const announcementBar = document.getElementById('announcementBar');
  const closeAnnouncement = document.getElementById('closeAnnouncement');

  if (closeAnnouncement && announcementBar) {
    closeAnnouncement.addEventListener('click', () => {
      announcementBar.classList.add('hidden');
    });
  }


  // ── Navbar Scroll Effect ──
  const navbar = document.getElementById('navbar');

  const handleNavScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };

  window.addEventListener('scroll', handleNavScroll, { passive: true });


  // ── Mobile Menu Toggle ──
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isActive = navLinks.classList.toggle('active');
      navToggle.classList.toggle('active', isActive);
      document.body.style.overflow = isActive ? 'hidden' : '';
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('active');
        navLinks.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
  }


  // ── FAQ Accordion — Fixed smooth open & close ──
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');

    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Close all — set explicit pixel height first, then collapse to allow CSS transition
      faqItems.forEach(other => {
        if (other.classList.contains('active')) {
          const otherAnswer = other.querySelector('.faq-answer');
          otherAnswer.style.maxHeight = otherAnswer.scrollHeight + 'px';
          // Force reflow so transition fires on the way down
          void otherAnswer.offsetHeight;
          otherAnswer.style.maxHeight = '0';
          other.classList.remove('active');
        }
      });

      // Open current if it wasn't active
      if (!isActive) {
        item.classList.add('active');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });


  // ── Intersection Observer — Scroll Animations ──
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -30px 0px'
  };

  const animateOnScroll = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        animateOnScroll.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right').forEach(el => {
    animateOnScroll.observe(el);
  });


  // ── Counter Animation — Fixed: uses data-suffix attribute ──
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.target);
        if (isNaN(target)) return;

        animateCounter(el, target);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('[data-target]').forEach(el => {
    counterObserver.observe(el);
  });

  function animateCounter(element, target) {
    const duration = 1600;
    const startTime = performance.now();
    // Fixed: read suffix from data attribute, not DOM text (prevents race condition)
    const suffix = element.dataset.suffix || '';

    function easeOutExpo(t) {
      return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutExpo(progress);
      const current = Math.round(easedProgress * target);

      element.textContent = current.toLocaleString() + suffix;

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }


  // ── Dashboard Bar Animation — Fixed: skip when hero visual is hidden (mobile) ──
  let barsAnimated = false;

  function animateBars() {
    if (barsAnimated) return;
    barsAnimated = true;

    document.querySelectorAll('.bar-fill').forEach((bar, index) => {
      const width = bar.dataset.width;
      setTimeout(() => {
        bar.style.width = width;
      }, index * 120);
    });
  }

  const dashboard = document.querySelector('.hero-dashboard');
  if (dashboard) {
    const dashboardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Fixed: check if the hero visual section is actually visible
          const heroVisual = document.querySelector('.hero-visual');
          if (!heroVisual || window.getComputedStyle(heroVisual).display !== 'none') {
            setTimeout(animateBars, 600);
          }
          dashboardObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    dashboardObserver.observe(dashboard);
  }


  // ── Smooth Scroll for Anchor Links ──
  // CSS scroll-behavior: smooth has been removed; this JS version handles the navbar offset
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const navHeight = navbar ? navbar.offsetHeight : 0;
        const targetPosition = targetEl.getBoundingClientRect().top + window.scrollY - navHeight - 16;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });


  // ── Active Nav Link Highlighting — Fixed: uses CSS class not inline styles ──
  const sections = document.querySelectorAll('section[id]');

  function highlightNav() {
    const scrollPos = window.scrollY + (navbar ? navbar.offsetHeight : 0) + 80;

    sections.forEach(section => {
      const top = section.offsetTop;
      const bottom = top + section.offsetHeight;
      const id = section.getAttribute('id');
      const link = navLinks ? navLinks.querySelector(`a[href="#${id}"]`) : null;

      if (link && !link.classList.contains('nav-cta')) {
        if (scrollPos >= top && scrollPos < bottom) {
          link.classList.add('nav-active');
        } else {
          link.classList.remove('nav-active');
        }
      }
    });
  }

  window.addEventListener('scroll', highlightNav, { passive: true });


  // ── Mouse Tracking Glow Effect for Module Cards — Simplified & working ──
  const cards = document.querySelectorAll('.module-card');

  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });

});
