/* ════════════════════════════════════════════════════════
   UCVN — Main JavaScript
   ════════════════════════════════════════════════════════ */

(function() {
  'use strict';

  // ─── MOBILE NAV ───────────────────────────────────────

  const burger  = document.querySelector('.site-header__burger');
  const mobileNav = document.getElementById('mobile-nav');
  const closeNav  = document.querySelector('.mobile-nav__close');
  const body      = document.body;

  function openMobileNav() {
    mobileNav && mobileNav.classList.add('is-open');
    burger && burger.setAttribute('aria-expanded', 'true');
    body.style.overflow = 'hidden';
  }

  function closeMobileNav() {
    mobileNav && mobileNav.classList.remove('is-open');
    burger && burger.setAttribute('aria-expanded', 'false');
    body.style.overflow = '';
  }

  burger  && burger.addEventListener('click', openMobileNav);
  closeNav && closeNav.addEventListener('click', closeMobileNav);

  // Close on overlay click
  mobileNav && mobileNav.addEventListener('click', function(e) {
    if (e.target === mobileNav) closeMobileNav();
  });

  // ─── AUTH MODALS ──────────────────────────────────────

  function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.add('is-open');
    body.style.overflow = 'hidden';
    const first = modal.querySelector('input, button');
    first && setTimeout(() => first.focus(), 50);
  }

  function closeModal(modal) {
    modal.classList.remove('is-open');
    body.style.overflow = '';
  }

  function closeAllModals() {
    document.querySelectorAll('.auth-modal-overlay.is-open').forEach(closeModal);
    document.querySelectorAll('.modal-overlay.is-open').forEach(closeModal);
  }

  // Open modal buttons
  document.addEventListener('click', function(e) {
    const trigger = e.target.closest('[data-modal-open]');
    if (trigger) {
      e.preventDefault();
      closeAllModals();
      const modalId = trigger.getAttribute('data-modal-open');
      openModal(modalId);
    }
  });

  // Close buttons
  document.addEventListener('click', function(e) {
    const closer = e.target.closest('[data-modal-close]');
    if (closer && !closer.hasAttribute('data-modal-open')) {
      closeAllModals();
    }
  });

  // Close on overlay click
  document.addEventListener('click', function(e) {
    if (e.target.matches('.auth-modal-overlay') || e.target.matches('.modal-overlay')) {
      closeModal(e.target);
    }
  });

  // Close on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeAllModals();
  });

  // ─── REGISTER MODAL — step 2 ──────────────────────────

  document.querySelectorAll('[data-choice="new"]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const step1 = document.getElementById('register-step-1');
      const step2 = document.getElementById('register-step-2');
      if (step1) step1.style.display = 'none';
      if (step2) step2.classList.remove('is-hidden');
    });
  });

  // ─── CAROUSEL ─────────────────────────────────────────

  document.querySelectorAll('[data-carousel]').forEach(function(carousel) {
    const track   = carousel.querySelector('[data-carousel-track]');
    if (!track) return;

    const section = carousel.closest('section') || carousel.parentElement;
    const prevBtn = section.querySelector('[data-carousel-prev]');
    const nextBtn = section.querySelector('[data-carousel-next]');

    let idx      = 0;
    let isDragging = false;
    let startX   = 0;
    let scrollLeft = 0;

    function getCardWidth() {
      const card = track.firstElementChild;
      if (!card) return 300;
      return card.offsetWidth + parseInt(getComputedStyle(track).gap || 24);
    }

    function scrollTo(pos) {
      track.style.transform = `translateX(${pos}px)`;
    }

    function slide(dir) {
      const total = track.children.length;
      const visible = Math.floor(carousel.offsetWidth / getCardWidth());
      idx = Math.max(0, Math.min(idx + dir, total - visible));
      scrollTo(-idx * getCardWidth());
    }

    prevBtn && prevBtn.addEventListener('click', () => slide(-1));
    nextBtn && nextBtn.addEventListener('click', () => slide(1));

    // Touch/drag
    track.addEventListener('mousedown', function(e) {
      isDragging = true;
      startX = e.pageX;
      scrollLeft = idx * getCardWidth();
      track.style.transition = 'none';
    });

    document.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      const dx = e.pageX - startX;
      scrollTo(-scrollLeft + dx);
    });

    document.addEventListener('mouseup', function(e) {
      if (!isDragging) return;
      isDragging = false;
      track.style.transition = '';
      const dx = e.pageX - startX;
      if (Math.abs(dx) > 50) slide(dx < 0 ? 1 : -1);
      else scrollTo(-idx * getCardWidth());
    });

    // Touch support (iOS Safari)
    track.addEventListener('touchstart', function(e) {
      startX = e.touches[0].pageX;
      scrollLeft = idx * getCardWidth();
      track.style.transition = 'none';
    }, { passive: true });

    track.addEventListener('touchend', function(e) {
      track.style.transition = '';
      const dx = e.changedTouches[0].pageX - startX;
      if (Math.abs(dx) > 40) slide(dx < 0 ? 1 : -1);
      else scrollTo(-idx * getCardWidth());
    }, { passive: true });
  });

  // ─── MARQUEE — duplicate for infinite ─────────────────

  document.querySelectorAll('.marquee__track').forEach(function(track) {
    const texts = track.querySelectorAll('.marquee__text');
    if (texts.length < 3) {
      // Ensure enough duplicates for seamless loop
      texts.forEach(function(t) {
        const clone = t.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        track.appendChild(clone);
      });
    }
  });

  // ─── FILTERS PANEL ───────────────────────────────────

  const filtersPanel = document.getElementById('filters-panel');

  function openFilters() {
    if (!filtersPanel) return;
    filtersPanel.hidden = false;
    body.style.overflow = 'hidden';
  }

  function closeFilters() {
    if (!filtersPanel) return;
    filtersPanel.hidden = true;
    body.style.overflow = '';
  }

  document.querySelectorAll('[data-filters-open]').forEach(function(btn) {
    btn.addEventListener('click', openFilters);
  });

  document.querySelectorAll('[data-filters-close]').forEach(function(btn) {
    btn.addEventListener('click', closeFilters);
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && filtersPanel && !filtersPanel.hidden) {
      closeFilters();
    }
  });

  // ─── LISTING SIDEBAR — авто-застосування фільтрів ─────

  document.querySelectorAll('.listing-sidebar form input[type="radio"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
      sessionStorage.setItem('sidebarScrollY', String(window.scrollY));
      var form = radio.closest('form');
      if (form) form.submit();
    });
  });

  (function() {
    var savedY = sessionStorage.getItem('sidebarScrollY');
    if (savedY !== null) {
      sessionStorage.removeItem('sidebarScrollY');
      window.scrollTo(0, parseInt(savedY, 10));
    }
  })();

  // ─── STRIPE CHECKOUT ─────────────────────────────────

  var PENDING_CHECKOUT_KEY = 'pendingCheckout';

  function getCheckoutCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el && el.value) return el.value;
    var meta = document.querySelector('body');
    var hxHeaders = meta ? meta.getAttribute('hx-headers') : '';
    try {
      return JSON.parse(hxHeaders)['X-CSRFToken'] || '';
    } catch (_) {
      return '';
    }
  }

  function postStripeCheckout(orderType, itemId) {
    var formData = new FormData();
    formData.append('order_type', orderType);
    formData.append('item_id', itemId);
    return fetch('/payments/checkout/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCheckoutCsrfToken() },
      body: formData,
      credentials: 'same-origin',
    });
  }

  function runCheckoutForButton(btn) {
    var orderType = btn.getAttribute('data-order-type');
    var itemId = btn.getAttribute('data-item-id');
    if (!orderType || !itemId) return;

    var originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Обробка...';

    postStripeCheckout(orderType, itemId)
      .then(function(resp) {
        if (resp.status === 401) {
          try {
            sessionStorage.setItem(PENDING_CHECKOUT_KEY, JSON.stringify({
              orderType: orderType,
              itemId: itemId,
            }));
          } catch (_) {}
          btn.disabled = false;
          btn.textContent = originalText;
          openModal('modal-login');
          return null;
        }
        if (!resp.ok) {
          return resp.json().then(function(body) {
            btn.disabled = false;
            if (body && body.error === 'stripe_not_configured') {
              btn.textContent = 'Оплата наразі недоступна';
            } else {
              btn.textContent = 'Помилка. Спробуйте ще раз';
            }
            return null;
          }).catch(function() {
            btn.disabled = false;
            btn.textContent = 'Помилка. Спробуйте ще раз';
            return null;
          });
        }
        return resp.json();
      })
      .then(function(data) {
        if (!data) return;
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        } else {
          btn.disabled = false;
          btn.textContent = 'Помилка. Спробуйте ще раз';
        }
      })
      .catch(function() {
        btn.disabled = false;
        btn.textContent = 'Помилка мережі';
      });
  }

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-checkout]');
    if (!btn) return;
    e.preventDefault();
    runCheckoutForButton(btn);
  });

  // ─── BUNNY.NET VIDEO PLAYER (Player.js) ─────────────

  function initVideoPlayer() {
    var iframe = document.getElementById('bunny-stream-embed');
    if (!iframe || typeof playerjs === 'undefined') return;

    var player = new playerjs.Player(iframe);

    player.on('ready', function() {
      var container = iframe.closest('[data-video-player]');
      if (container) {
        container.classList.add('video-player--ready');
      }
    });

    player.on('ended', function() {
      var nextBtn = document.querySelector('.lesson-content__nav .btn-red');
      if (nextBtn) {
        nextBtn.classList.add('btn--pulse');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(initVideoPlayer, 500);
    });
  } else {
    setTimeout(initVideoPlayer, 500);
  }

  // ─── HTMX events ──────────────────────────────────────

  document.addEventListener('htmx:afterRequest', function(e) {
    if (!e.detail.successful) return;
    var form = e.detail.elt;
    if (!form.closest('.auth-modal')) return;

    var redirect = e.detail.xhr.getResponseHeader('HX-Redirect');
    if (!redirect) return;

    var isLoginModal = form.closest('#modal-login');
    var pendingRaw = null;
    try {
      pendingRaw = sessionStorage.getItem(PENDING_CHECKOUT_KEY);
    } catch (_) {}

    if (isLoginModal && pendingRaw) {
      var pending = null;
      try {
        pending = JSON.parse(pendingRaw);
      } catch (_) {}

      if (pending && pending.orderType && pending.itemId) {
        try {
          sessionStorage.removeItem(PENDING_CHECKOUT_KEY);
        } catch (_) {}

        closeAllModals();

        postStripeCheckout(pending.orderType, pending.itemId)
          .then(function(resp) {
            if (resp.ok) return resp.json();
            window.location.href = redirect;
            return null;
          })
          .then(function(data) {
            if (data && data.checkout_url) {
              window.location.href = data.checkout_url;
            } else if (data !== null) {
              window.location.href = redirect;
            }
          })
          .catch(function() {
            window.location.href = redirect;
          });
        return;
      }
    }

    setTimeout(function() {
      closeAllModals();
      window.location.href = redirect;
    }, 300);
  });

})();
