(() => {
  const nav = document.querySelector('.sidebar-nav');
  if (!nav) return;
  const sidebar = nav.closest('.reader-sidebar');
  const links = [...nav.querySelectorAll('a[href^="#"]')];
  const items = links.map(link => ({link, section: document.querySelector(link.getAttribute('href'))})).filter(item => item.section);
  let scheduled = false;
  const sync = () => {
    const line = Math.min(180, window.innerHeight * 0.28);
    let current = items[0];
    for (const item of items) {
      if (item.section.getBoundingClientRect().top <= line) current = item;
      else break;
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) current = items[items.length - 1];
    for (const item of items) {
      const active = item === current;
      item.link.classList.toggle('active', active);
      if (active) item.link.setAttribute('aria-current', 'location'); else item.link.removeAttribute('aria-current');
    }
    if (current && sidebar && sidebar.scrollHeight > sidebar.clientHeight) current.link.scrollIntoView({block:'nearest'});
    scheduled = false;
  };
  const schedule = () => { if (!scheduled) { scheduled = true; window.requestAnimationFrame(sync); } };
  document.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  window.addEventListener('hashchange', schedule);
  sync();
})();
