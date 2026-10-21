/* Shared homepage motion, adapted to the inner-page sections. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const panels = [...document.querySelectorAll('main > section:not(.page-intro)')];
  const cards = [...document.querySelectorAll('.portfolio-tile')];
  const reveals = [...document.querySelectorAll('.page-intro > *, .content-heading > *, .rich-copy > *, .project-facts dl > div, .portfolio-tile, .service-directory > a, .category-heading > *, .page-cta > *')];
  if (!('IntersectionObserver' in window) || reduced.matches) return;
  document.body.classList.add('motion-ready');
  reveals.forEach(element => element.classList.add('page-reveal'));
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: .1 });
  reveals.forEach(element => observer.observe(element));
  const header = document.querySelector('.site-header');
  const surfaces = [...document.querySelectorAll('main > section, main > figure')];
  let scheduled = false;
  const sync = () => {
    scheduled = false;
    const disabled = reduced.matches;
    panels.forEach(panel => {
      const rect = panel.getBoundingClientRect();
      const progress = disabled ? 1 : Math.max(0, Math.min(1, (innerHeight - rect.top) / (innerHeight * .72)));
      panel.style.setProperty('--panel-inset', `${((1-progress)*Math.min(innerWidth*.045,58)).toFixed(1)}px`);
      panel.style.setProperty('--panel-radius', `${((1-progress)*22).toFixed(1)}px`);
    });
    cards.forEach(card => {
      const progress = disabled ? 1 : Math.max(0, Math.min(1,(innerHeight-card.getBoundingClientRect().top)/(innerHeight*.72)));
      card.style.setProperty('--card-inset', `${((1-progress)*Math.min(innerWidth*.025,28)).toFixed(1)}px`);
    });
    const active = surfaces.find(panel => { const r=panel.getBoundingClientRect();return r.top<=header.offsetHeight && r.bottom>header.offsetHeight; });
    const dark = active?.dataset.surface === 'dark';
    header.classList.toggle('header-on-dark',dark);
    header.classList.toggle('header-on-light',!dark);
  };
  const requestSync = () => { if(!scheduled){scheduled=true;requestAnimationFrame(sync);} };
  addEventListener('scroll',requestSync,{passive:true});
  addEventListener('resize',requestSync);
  reduced.addEventListener('change',()=>{
    document.body.classList.toggle('motion-ready',!reduced.matches);
    if(reduced.matches) reveals.forEach(el=>el.classList.add('is-visible'));
    requestSync();
  });
  sync();
})();
