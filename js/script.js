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
    const closeMenu = () => {
      navToggle.classList.remove('active');
      navLinks.classList.remove('active');
      navToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };

    navToggle.addEventListener('click', () => {
      const isActive = navLinks.classList.toggle('active');
      navToggle.classList.toggle('active', isActive);
      navToggle.setAttribute('aria-expanded', String(isActive));
      document.body.style.overflow = isActive ? 'hidden' : '';
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Escape key closes mobile menu and refocuses toggle
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navLinks.classList.contains('active')) {
        closeMenu();
        navToggle.focus();
      }
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
    rootMargin: ['0px', '0px', '-30px', '0px'].join(' ')
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


  // ── Testimonials Carousel ──
  const track = document.querySelector('.testimonials-track');
  const prevBtn = document.querySelector('.carousel-btn.prev');
  const nextBtn = document.querySelector('.carousel-btn.next');
  const dotsContainer = document.querySelector('.carousel-dots-container');

  if (track && dotsContainer) {
    const cards = Array.from(track.children);
    let currentIndex = 0;
    let autoplayTimer = null;

    // Create dots
    cards.forEach((_, index) => {
      const dot = document.createElement('button');
      dot.classList.add('carousel-dot');
      dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
      if (index === 0) dot.classList.add('active');
      dot.addEventListener('click', () => {
        goToSlide(index);
        resetAutoplay();
      });
      dotsContainer.appendChild(dot);
    });

    const dots = Array.from(dotsContainer.children);

    const updateSlidePosition = () => {
      track.style.transform = `translateX(-${currentIndex * 100}%)`;
      dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentIndex);
      });
    };

    const goToSlide = (index) => {
      if (index < 0) {
        currentIndex = cards.length - 1;
      } else if (index >= cards.length) {
        currentIndex = 0;
      } else {
        currentIndex = index;
      }
      updateSlidePosition();
    };

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        goToSlide(currentIndex - 1);
        resetAutoplay();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        goToSlide(currentIndex + 1);
        resetAutoplay();
      });
    }

    // Touch Swipe Support
    let startX = 0;
    let isSwiping = false;

    track.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isSwiping = true;
    }, { passive: true });

    track.addEventListener('touchmove', (e) => {
      if (!isSwiping) return;
      const diffX = e.touches[0].clientX - startX;
      if (Math.abs(diffX) > 50) {
        if (diffX > 0) {
          goToSlide(currentIndex - 1);
        } else {
          goToSlide(currentIndex + 1);
        }
        isSwiping = false;
        resetAutoplay();
      }
    }, { passive: true });

    track.addEventListener('touchend', () => {
      isSwiping = false;
    });

    // Autoplay
    const startAutoplay = () => {
      autoplayTimer = setInterval(() => {
        goToSlide(currentIndex + 1);
      }, 6000);
    };

    const resetAutoplay = () => {
      clearInterval(autoplayTimer);
      startAutoplay();
    };

    startAutoplay();

    // Pause on hover
    const wrapper = document.querySelector('.testimonials-carousel-wrapper');
    if (wrapper) {
      wrapper.addEventListener('mouseenter', () => clearInterval(autoplayTimer));
      wrapper.addEventListener('mouseleave', startAutoplay);
    }
  }


  // ── GA4 CTA Click Tracking ──
  // Fires a 'cta_click' event for every Book a Call / strategy call button
  const ctaSelectors = [
    '.btn-primary[href*="/book"]',
    '.nav-cta[href*="/book"]',
    '.btn-ghost[href*="/book"]',
    '#finalCta'
  ];

  document.querySelectorAll(ctaSelectors.join(',')).forEach(el => {
    el.addEventListener('click', () => {
      if (typeof gtag === 'function') {
        gtag('event', 'cta_click', {
          event_category: 'engagement',
          event_label: el.textContent.trim(),
          link_url: el.getAttribute('href')
        });
      }
    });
  });

  // ── Cookie Consent Banner ──
  const consent = localStorage.getItem("cookie-consent");
  if (!consent) {
    createCookieBanner();
  } else if (consent === "declined") {
    disableGoogleAnalytics();
  }

  function createCookieBanner() {
    const banner = document.createElement("div");
    banner.id = "cookie-consent-banner";
    banner.className = "cookie-banner";
    banner.innerHTML = `
      <div class="cookie-banner-content">
        <p>We use cookies to analyze site traffic and optimize your experience. Read our <a href="/privacy#cookies" class="cookie-policy-link">Cookie Policy</a>.</p>
        <div class="cookie-banner-actions">
          <button id="cookie-decline" class="btn-cookie-decline">Decline</button>
          <button id="cookie-accept" class="btn-cookie-accept">Accept All</button>
        </div>
      </div>
    `;
    document.body.appendChild(banner);

    // Slide-up animation delay
    setTimeout(() => {
      banner.classList.add("show");
    }, 1000);

    document.getElementById("cookie-accept").addEventListener("click", () => {
      localStorage.setItem("cookie-consent", "accepted");
      banner.classList.remove("show");
      setTimeout(() => banner.remove(), 400);
    });

    document.getElementById("cookie-decline").addEventListener("click", () => {
      localStorage.setItem("cookie-consent", "declined");
      disableGoogleAnalytics();
      banner.classList.remove("show");
      setTimeout(() => banner.remove(), 400);
    });
  }

  function disableGoogleAnalytics() {
    window['ga-disable-G-77X4J912VN'] = true;
  }

});

