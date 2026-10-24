const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const heroFilm = document.querySelector('.hero-intro');
if (heroFilm) {
  heroFilm.muted = true;
  if (reduced) {
    heroFilm.pause();
  } else {
    heroFilm.play().catch(() => {});
  }
}
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('visible');
    revealObserver.unobserve(entry.target);
  });
}, { threshold: .12 });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

const progress = document.querySelector('.progress');
const header = document.querySelector('.site-header');
const hero = document.querySelector('.hero');
let ticking = false;
const syncPage = () => {
  const range = document.documentElement.scrollHeight - innerHeight;
  progress.style.width = `${range ? (scrollY / range) * 100 : 0}%`;
  header.classList.toggle('hero-header', scrollY < hero.offsetHeight - header.offsetHeight);
  ticking = false;
};
addEventListener('scroll', () => {
  if (ticking) return;
  ticking = true;
  requestAnimationFrame(syncPage);
}, { passive: true });
addEventListener('resize', syncPage);
syncPage();

const menu = document.querySelector('.menu-button');
const dropdownButtons = [...header.querySelectorAll('.dropdown-toggle')];
// Measure the expanded panel for one continuous header-and-dropdown backdrop.
const syncDropdownSurface = () => {
  const expanded = dropdownButtons.find(button => button.getAttribute('aria-expanded') === 'true');
  const panel = expanded && document.getElementById(expanded.getAttribute('aria-controls'));
  header.style.setProperty('--dropdown-height', `${panel ? panel.offsetHeight : 0}px`);
};
const dropdownSurfaceObserver = new ResizeObserver(syncDropdownSurface);
header.querySelectorAll('.dropdown-panel').forEach(panel => dropdownSurfaceObserver.observe(panel));

const closeDropdowns = () => dropdownButtons.forEach(button => {
  button.setAttribute('aria-expanded', 'false');
  document.getElementById(button.getAttribute('aria-controls')).hidden = true;
});
const closeNavigation = () => {
  closeDropdowns();
  header.classList.remove('open');
  menu.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-label', 'Open navigation');
};
menu.addEventListener('click', () => {
  const open = !header.classList.contains('open');
  closeNavigation();
  header.classList.toggle('open', open);
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
dropdownButtons.filter(button => button.tagName === 'BUTTON').forEach(button => button.addEventListener('click', () => {
  const open = button.getAttribute('aria-expanded') !== 'true';
  closeDropdowns();
  button.setAttribute('aria-expanded', String(open));
  document.getElementById(button.getAttribute('aria-controls')).hidden = !open;
}));
// Desktop hover keeps the panel open while moving between its trigger and links.
const hoverNavigation = matchMedia('(hover: hover) and (min-width: 901px)');
let dropdownLeaveTimer;
header.querySelectorAll('.nav-dropdown').forEach(dropdown => {
  const button = dropdown.querySelector('.dropdown-toggle');
  dropdown.addEventListener('pointerenter', event => {
    if (!hoverNavigation.matches || event.pointerType === 'touch') return;
    clearTimeout(dropdownLeaveTimer);
    closeDropdowns();
    button.setAttribute('aria-expanded', 'true');
    document.getElementById(button.getAttribute('aria-controls')).hidden = false;
  });
  dropdown.addEventListener('pointerleave', event => {
    if (!hoverNavigation.matches || event.pointerType === 'touch') return;
    dropdownLeaveTimer = setTimeout(() => {
      if (!dropdown.contains(document.activeElement)) closeDropdowns();
    }, 180);
  });
});

header.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  closeNavigation();
}));
document.addEventListener('click', event => { if (!header.contains(event.target)) closeNavigation(); });
header.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    const active = dropdownButtons.find(button => button.getAttribute('aria-expanded') === 'true');
    if (active) { closeDropdowns(); active.focus(); }
    else { closeNavigation(); menu.focus(); }
  }
});
header.addEventListener('focusout', event => {
  if (!header.contains(event.relatedTarget)) closeNavigation();
});
matchMedia('(max-width: 900px)').addEventListener('change', closeNavigation);

const canHover = matchMedia('(hover:hover)').matches;
const storyCards = [...document.querySelectorAll('.story-card')];
let testimonialSoundOn = false;
const syncTestimonialSound = on => {
  testimonialSoundOn = on;
  storyCards.forEach(item => {
    const itemVideo = item.querySelector('video');
    const itemSound = item.querySelector('.sound-toggle');
    const itemName = item.dataset.name;
    itemVideo.muted = !on;
    item.classList.toggle('sound-on', on);
    itemSound.lastChild.textContent = on ? ' Sound on' : ' Sound off';
    itemSound.setAttribute('aria-label', `Sound is ${on ? 'on' : 'off'} for all client stories. Click to turn it ${on ? 'off' : 'on'}. Current story: ${itemName}.`);
  });
};
storyCards.forEach(card => {
  const video = card.querySelector('video');
  const sound = card.querySelector('.sound-toggle');
  const start = () => {
    document.querySelectorAll('.story-card.playing').forEach(other => {
      if (other !== card) other.dispatchEvent(new CustomEvent('stop-preview'));
    });
    card.classList.add('playing');
    video.muted = !testimonialSoundOn;
    video.play().catch(() => {});
  };
  const stop = () => {
    card.classList.remove('playing');
    video.pause();
    video.muted = !testimonialSoundOn;
    try { video.currentTime = .2; } catch {}
  };
  card.addEventListener('stop-preview', stop);
  new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) stop();
  }, { threshold: .2 }).observe(card);
  if (canHover) {
    card.addEventListener('mouseenter', start);
    card.addEventListener('mouseleave', stop);
  } else {
    card.addEventListener('click', event => {
      if (event.target.closest('.sound-toggle')) return;
      video.paused ? start() : stop();
    });
  }
  sound.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    syncTestimonialSound(!testimonialSoundOn);
    start();
  });
});

const storyViewport = document.querySelector('.story-viewport');
const slideBy = direction => storyViewport.scrollBy({ left: direction * Math.min(innerWidth * .72, 500), behavior: reduced ? 'auto' : 'smooth' });
document.querySelector('.slide-prev').addEventListener('click', () => slideBy(-1));
document.querySelector('.slide-next').addEventListener('click', () => slideBy(1));

document.querySelector('#contact-form').addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const body = `Name: ${data.get('name')}\nEmail: ${data.get('email')}\n\nWhat the next website should do better:\n${data.get('message')}`;
  location.href = `mailto:info@point0.com?subject=${encodeURIComponent('Website project enquiry')}&body=${encodeURIComponent(body)}`;
});






const proofCounter = document.querySelector('.proof-count span');
if (proofCounter) {
  const target = 60;
  if (reduced) {
    proofCounter.textContent = String(target);
  } else {
    proofCounter.textContent = '0';
    const counterObserver = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting) return;
      counterObserver.disconnect();
      const duration = 1500;
      const startedAt = performance.now();
      const count = now => {
        const progress = Math.min((now - startedAt) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        proofCounter.textContent = String(Math.round(target * eased));
        if (progress < 1) requestAnimationFrame(count);
      };
      requestAnimationFrame(count);
    }, { threshold: .4 });
    counterObserver.observe(proofCounter);
  }
}

if (storyViewport && !reduced) {
  const storyTrack = storyViewport.querySelector('.story-track');
  let storyAutoTimer = null;
  let storyIsMoving = false;
  const autoAdvanceStories = () => {
    if (document.hidden || storyIsMoving || storyViewport.matches(':hover')) return;
    const first = storyTrack.firstElementChild;
    const second = first?.nextElementSibling;
    if (!first || !second) return;
    const stride = second.offsetLeft - first.offsetLeft;
    storyIsMoving = true;
    storyViewport.scrollBy({ left: stride, behavior: 'smooth' });
    setTimeout(() => {
      storyTrack.append(first);
      storyViewport.style.scrollBehavior = 'auto';
      storyViewport.scrollLeft = Math.max(0, storyViewport.scrollLeft - stride);
      storyViewport.style.removeProperty('scroll-behavior');
      storyIsMoving = false;
    }, 750);
  };
  const storyVisibility = new IntersectionObserver(entries => {
    clearInterval(storyAutoTimer);
    storyAutoTimer = entries[0].isIntersecting ? setInterval(autoAdvanceStories, 5000) : null;
  }, { threshold: .2 });
  storyVisibility.observe(storyViewport);
}

// Editorial page choreography: each surface opens like a page as it enters.
const editorialPanels = [...document.querySelectorAll('main > section:not(.hero)')];
const editorialProjectCards = [...document.querySelectorAll('.projects .project')];
const editorialLightSections = new Set(['intro', 'why', 'work', 'consequence', 'contact']);
const syncEditorial = () => {
  if (!document.body.classList.contains('editorial')) return;
  const vh = innerHeight;
  document.body.classList.toggle('past-hero', scrollY > hero.offsetHeight * .72);
  editorialPanels.forEach(panel => {
    if (reduced || panel.id === 'work') {
      panel.style.setProperty('--panel-inset', '0px');
      panel.style.setProperty('--panel-radius', '0px');
      return;
    }
    const rect = panel.getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, (vh - rect.top) / (vh * .72)));
    const inset = (1 - progress) * Math.min(innerWidth * .045, 58);
    panel.style.setProperty('--panel-inset', `${inset.toFixed(1)}px`);
    panel.style.setProperty('--panel-radius', `${((1 - progress) * 22).toFixed(1)}px`);
  });
  editorialProjectCards.forEach(card => {
    if (reduced) {
      card.style.setProperty('--project-inset', '0px');
      card.style.setProperty('--project-radius', '0px');
      return;
    }
    const rect = card.getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, (vh - rect.top) / (vh * .72)));
    const inset = (1 - progress) * Math.min(innerWidth * .045, 58);
    card.style.setProperty('--project-inset', `${inset.toFixed(1)}px`);
    card.style.setProperty('--project-radius', `${((1 - progress) * 22).toFixed(1)}px`);
  });
  const headerLine = header.offsetHeight;
  const active = editorialPanels.find(panel => {
    const rect = panel.getBoundingClientRect();
    return rect.top <= headerLine && rect.bottom > headerLine;
  });
  header.classList.toggle('header-on-light', Boolean(active && editorialLightSections.has(active.id)));
  header.classList.toggle('header-on-dark', Boolean(active && !editorialLightSections.has(active.id)));
};
if (document.body.classList.contains('editorial')) {
  let editorialTicking = false;
  const requestEditorialSync = () => {
    if (editorialTicking) return;
    editorialTicking = true;
    requestAnimationFrame(() => {
      syncEditorial();
      editorialTicking = false;
    });
  };
  addEventListener('scroll', requestEditorialSync, { passive:true });
  addEventListener('resize', requestEditorialSync);
  syncEditorial();
}
