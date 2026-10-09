const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const heroFilm = document.querySelector('.hero-intro');
const heroLoop = document.querySelector('.hero-loop');
let finalLoopStarted = false;
if (heroFilm) {
  heroFilm.muted = true;
  heroLoop.muted = true;
  if (reduced) {
    heroFilm.pause();
    heroLoop.pause();
  } else {
    heroFilm.play().catch(() => {});
  }
  heroFilm.addEventListener('timeupdate', () => {
    if (!finalLoopStarted && heroFilm.currentTime >= 10.25) {
      finalLoopStarted = true;
      heroLoop.currentTime = 0;
      heroLoop.play().catch(() => {});
    }
  });
  heroFilm.addEventListener('ended', () => {
    heroFilm.pause();
    document.querySelector('.hero').classList.add('is-final');
    if (!finalLoopStarted) heroLoop.play().catch(() => {});
  });
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
menu.addEventListener('click', () => {
  const open = header.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
header.querySelectorAll('nav a').forEach(link => link.addEventListener('click', () => {
  header.classList.remove('open');
  menu.setAttribute('aria-expanded', 'false');
}));

const canHover = matchMedia('(hover:hover)').matches;
document.querySelectorAll('.story-card').forEach(card => {
  const video = card.querySelector('video');
  const sound = card.querySelector('.sound-toggle');
  const name = card.dataset.name;
  const start = () => {
    document.querySelectorAll('.story-card.playing').forEach(other => {
      if (other !== card) other.dispatchEvent(new CustomEvent('stop-preview'));
    });
    card.classList.add('playing');
    video.play().catch(() => {});
  };
  const stop = () => {
    card.classList.remove('playing', 'sound-on');
    video.pause();
    video.muted = true;
    sound.lastChild.textContent = ' Sound off';
    sound.setAttribute('aria-label', `Sound is off for ${name}. Click to turn it on.`);
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
    start();
    const turnOn = video.muted;
    video.muted = !turnOn;
    card.classList.toggle('sound-on', turnOn);
    sound.lastChild.textContent = turnOn ? ' Sound on' : ' Sound off';
    sound.setAttribute('aria-label', `Sound is ${turnOn ? 'on' : 'off'} for ${name}. Click to turn it ${turnOn ? 'off' : 'on'}.`);
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
  location.href = `mailto:info@gbltechnologies.com?subject=${encodeURIComponent('Website project enquiry')}&body=${encodeURIComponent(body)}`;
  document.querySelector('#form-status').textContent = 'Your email draft is ready. Send it from your email app to begin the conversation.';
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
