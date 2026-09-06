const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

const revealTargets = document.querySelectorAll('.case-card, .approach-grid li, .tool-matrix div, .writing-list a');
revealTargets.forEach((item) => item.setAttribute('data-reveal', ''));

if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.documentElement.classList.add('reveal-ready');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -48px' });
  revealTargets.forEach((item) => observer.observe(item));
}
