// ==========================================
// INTERNATIONALIZATION (i18n) ENGINE
// ==========================================
const translations = {
    en: {
        "hero-title": "The Sustainability <br /> <span class='text-brand-400 glow-text'>Digital Twin.</span>",
        "hero-subtitle": "Bridging the gap between a vehicle's birth, life, and second life. Moving the automotive industry beyond 'replace-by-default'.",
        "btn-enterprise": "Enterprise Portal",
        "btn-enterprise-sub": "Insurer & OEM Access",
        "btn-driver": "Driver Hub",
        "btn-driver-sub": "Consumer Mobile App"
    },
    it: {
        "hero-title": "Il <span class='text-brand-400 glow-text'>Digital Twin</span> <br /> della Sostenibilità.",
        "hero-subtitle": "Colmiamo il divario tra la nascita, la vita e la seconda vita di un veicolo. Oltre il concetto di 'sostituzione di default'.",
        "btn-enterprise": "Portale Enterprise",
        "btn-enterprise-sub": "Accesso Assicurazioni & OEM",
        "btn-driver": "App Guidatore",
        "btn-driver-sub": "App Mobile Utente"
    }
};

window.setLanguage = function (lang) {
    // 1. Save preference
    localStorage.setItem('cyclesync_lang', lang);

    // 2. Update UI Toggle styling
    const btnEn = document.getElementById('lang-en');
    const btnIt = document.getElementById('lang-it');

    if (lang === 'en') {
        if (btnEn) btnEn.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all bg-brand-500 text-slate-900 shadow-[0_0_10px_rgba(0,229,255,0.4)]";
        if (btnIt) btnIt.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all text-slate-400 hover:text-white bg-transparent shadow-none";
    } else {
        if (btnIt) btnIt.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all bg-brand-500 text-slate-900 shadow-[0_0_10px_rgba(0,229,255,0.4)]";
        if (btnEn) btnEn.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all text-slate-400 hover:text-white bg-transparent shadow-none";
    }

    // 3. Swap the text using the dictionary
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.innerHTML = translations[lang][key];
        }
    });
};

// ==========================================
// MAIN DOM LOAD (Animations & Init)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Language first
    const savedLang = localStorage.getItem('cyclesync_lang') || 'en';
    setLanguage(savedLang);

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