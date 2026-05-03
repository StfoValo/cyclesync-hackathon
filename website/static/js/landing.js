// Language setup moved to i18n.js
// ==========================================
// MAIN DOM LOAD (Animations & Init)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Language init moved to i18n.js

    // 2. Scroll Animation Observer (The Fade-in Cards)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const fadeElements = document.querySelectorAll('.fade-in-section');
    fadeElements.forEach(el => observer.observe(el));
});