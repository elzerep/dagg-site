(() => {
  const links = [...document.querySelectorAll('[data-nav]')];
  const boards = [...document.querySelectorAll('[data-board]')];

  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach((link) => {
      const current = link.dataset.nav === visible.target.dataset.board;
      if (current) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  }, { threshold: [0.18, 0.38, 0.62], rootMargin: '-18% 0px -58% 0px' });

  boards.forEach((board) => observer.observe(board));
})();
