(() => {
  document.documentElement.classList.add('js');

  const toggle = document.querySelector('.nav__toggle');
  const navLinks = document.querySelector('.nav__links');

  const closeMenu = ({ returnFocus = false } = {}) => {
    if (!toggle || !navLinks) return;
    navLinks.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation menu');
    document.body.classList.remove('nav-open');
    if (returnFocus) toggle.focus();
  };

  const openMenu = () => {
    if (!toggle || !navLinks) return;
    navLinks.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Close navigation menu');
    document.body.classList.add('nav-open');
    navLinks.querySelector('a')?.focus();
  };

  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      if (isOpen) closeMenu();
      else openMenu();
    });

    navLinks.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });

    document.addEventListener('click', (event) => {
      if (
        toggle.getAttribute('aria-expanded') === 'true' &&
        !event.target.closest('.nav__inner')
      ) {
        closeMenu();
      }
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeMenu();
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
      closeMenu({ returnFocus: true });
    }
  });

  const path = decodeURIComponent(window.location.pathname).replace(/\\/g, '/');
  const currentSection = path.includes('/projects/')
    ? 'projects.html'
    : path.includes('/writing/')
      ? 'writing.html'
      : path.split('/').pop() || 'index.html';
  const inNotes = path.includes('/notes/');

  document.querySelectorAll('.nav__links a').forEach((link) => {
    const linkFile = new URL(link.href, window.location.href).pathname.split('/').pop();
    // notes/index.html and the home page share a file name, so the notes link is matched by section.
    const isNotesLink = link.dataset.nav === 'notes';
    const isCurrent = inNotes ? isNotesLink : !isNotesLink && linkFile === currentSection;
    if (isCurrent) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });

  document.querySelectorAll('[data-showcase]').forEach((showcase) => {
    const tabs = Array.from(showcase.querySelectorAll('[role="tab"]'));
    const panel = showcase.querySelector('[role="tabpanel"]');
    const image = showcase.querySelector('[data-showcase-image]');
    const link = showcase.querySelector('[data-showcase-link]');
    const caption = showcase.querySelector('[data-showcase-caption]');
    if (!tabs.length || !panel || !image || !link || !caption) return;

    const select = (tab, { focus = false } = {}) => {
      tabs.forEach((item) => {
        const selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
      });
      panel.setAttribute('aria-labelledby', tab.id);
      link.href = tab.dataset.full || tab.dataset.src;
      link.dataset.alt = tab.dataset.alt;
      caption.textContent = tab.dataset.caption;
      if (focus) tab.focus();
      if (image.getAttribute('src') === tab.dataset.src) return;
      image.classList.add('is-swapping');
      window.setTimeout(() => {
        image.src = tab.dataset.src;
        image.alt = tab.dataset.alt;
        image.classList.remove('is-swapping');
      }, 180);
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', (event) => {
        const next = {
          ArrowRight: (index + 1) % tabs.length,
          ArrowLeft: (index - 1 + tabs.length) % tabs.length,
          Home: 0,
          End: tabs.length - 1,
        }[event.key];
        if (next === undefined) return;
        event.preventDefault();
        select(tabs[next], { focus: true });
      });
      new Image().src = tab.dataset.src;
    });
  });

  document.querySelectorAll('a[target="_blank"]').forEach((link) => {
    if (!link.getAttribute('aria-label')) {
      const label = link.textContent.trim();
      if (label) link.setAttribute('aria-label', `${label} (opens in a new tab)`);
    }
  });

  document.querySelectorAll('[data-current-year]').forEach((element) => {
    element.textContent = new Date().getFullYear();
  });

  document.querySelectorAll('[data-print-page]').forEach((button) => {
    button.addEventListener('click', () => window.print());
  });

  document.querySelectorAll('[data-filter-group]').forEach((group) => {
    const buttons = group.querySelectorAll('[data-filter]');
    const targetSelector = group.dataset.filterTargets;
    const targets = targetSelector ? document.querySelectorAll(targetSelector) : [];

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const filter = button.dataset.filter;
        buttons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
        targets.forEach((target) => {
          target.hidden = filter !== 'all' && target.dataset.category !== filter;
        });
      });
    });
  });

  const lightbox = document.getElementById('project-lightbox');
  const lightboxImage = document.getElementById('lightbox-image');
  const lightboxClose = document.getElementById('lightbox-close');
  const lightboxPrev = document.getElementById('lightbox-prev');
  const lightboxNext = document.getElementById('lightbox-next');
  const lightboxCounter = document.getElementById('lightbox-counter');
  const triggers = Array.from(document.querySelectorAll('[data-lightbox]'));

  if (
    lightbox &&
    lightboxImage &&
    lightboxClose &&
    lightboxPrev &&
    lightboxNext &&
    lightboxCounter &&
    triggers.length
  ) {
    let currentIndex = 0;
    let previousFocus = null;

    const renderImage = (index) => {
      const target = triggers[index];
      if (!target) return;
      currentIndex = index;
      lightboxImage.src = target.getAttribute('href');
      lightboxImage.alt = target.dataset.alt || target.querySelector('img')?.alt || 'Project image';
      lightboxCounter.textContent = `${index + 1} / ${triggers.length}`;
    };

    const closeLightbox = () => {
      lightbox.classList.remove('is-open');
      lightbox.setAttribute('aria-hidden', 'true');
      lightbox.inert = true;
      lightboxCounter.textContent = '';
      document.body.style.removeProperty('overflow');
      previousFocus?.focus();
    };

    const openLightbox = (index, trigger) => {
      previousFocus = trigger;
      renderImage(index);
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      lightbox.inert = false;
      document.body.style.overflow = 'hidden';
      lightboxClose.focus();
    };

    const showNext = () => renderImage((currentIndex + 1) % triggers.length);
    const showPrev = () => renderImage((currentIndex - 1 + triggers.length) % triggers.length);

    triggers.forEach((trigger, index) => {
      trigger.addEventListener('click', (event) => {
        event.preventDefault();
        openLightbox(index, trigger);
      });
    });

    lightboxClose.addEventListener('click', closeLightbox);
    lightboxPrev.addEventListener('click', showPrev);
    lightboxNext.addEventListener('click', showNext);
    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox) closeLightbox();
    });

    lightbox.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeLightbox();
      if (event.key === 'ArrowRight') showNext();
      if (event.key === 'ArrowLeft') showPrev();

      if (event.key === 'Tab') {
        const controls = [lightboxPrev, lightboxNext, lightboxClose];
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
  }
})();
