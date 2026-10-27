const header=document.querySelector('.site-header');
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

document.querySelectorAll('footer a[href$="#top"], a[href="#top"]').forEach(link => {
  link.addEventListener('click', event => {
    event.preventDefault();
    closeNavigation();
    window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
});


addEventListener('scroll',()=>{const range=document.documentElement.scrollHeight-innerHeight;document.querySelector('.progress').style.width=(range?scrollY/range*100:0)+'%';},{passive:true});