import { initTelemetry } from './views/telemetry.js?v=13';
import { initActuarial } from './views/actuarial.js?v=13';
import { initPredictiveAsset } from './views/predictive_asset.js?v=13';
import { initAIStrategy } from './views/ai_strategy.js?v=13';
import { initESG } from './views/esg.js?v=13';
import { initAdjuster } from './views/adjuster.js?v=13';

const viewModules = {
    'telemetry-view':  { path: '/static/partials/telemetry_tab.html?v=13',  init: initTelemetry },
    'executive-view':  { path: '/static/partials/executive_tab.html?v=13',  init: initActuarial },
    'asset-view':      { path: '/static/partials/asset_tab.html?v=13',      init: initPredictiveAsset },
    'ai-view':         { path: '/static/partials/ai_tab.html?v=13',         init: initAIStrategy },
    'esg-view':        { path: '/static/partials/esg_tab.html?v=13',        init: initESG },
    'adjuster-view':   { path: '/static/partials/adjuster_tab.html?v=13',   init: initAdjuster }
};

const loadedViews = new Set();

document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const viewSections = document.querySelectorAll('.view-section');

    async function loadView(targetId) {
        const section = document.getElementById(targetId);
        if (!section) return;

        // Hide all, show target
        viewSections.forEach(sec => sec.classList.remove('active'));
        section.classList.add('active');
        if (window.lucide) setTimeout(() => lucide.createIcons(), 50);

        if (!loadedViews.has(targetId)) {
            loadedViews.add(targetId); // Prevent race condition on rapid clicks
            try {
                const config = viewModules[targetId];
                if (!config) return;

                const response = await fetch(config.path);
                if (!response.ok) throw new Error('Failed to load partial');
                const html = await response.text();
                section.innerHTML = html;

                // Instantly translate the newly injected HTML
                if (window.setLanguage) {
                    window.setLanguage(localStorage.getItem('cyclesync_lang') || 'en');
                }

                if (config.init) {
                    config.init();
                }

                // Re-run Lucide after content is rendered
                if (window.lucide) setTimeout(() => lucide.createIcons(), 80);

            } catch (err) {
                loadedViews.delete(targetId); // Revert if failed
                console.error(`Error loading view ${targetId}:`, err);
            }
        }

        // Force resize Chart.js instances
        setTimeout(() => {
            if (typeof window.Chart !== 'undefined') {
                for (let id in window.Chart.instances) {
                    window.Chart.instances[id].resize();
                }
            }
        }, 50);
    }

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(nav => nav.classList.remove('active'));
            e.currentTarget.classList.add('active');
            const targetId = e.currentTarget.getAttribute('data-target');
            loadView(targetId);
        });
    });

    // Load initial view
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) {
        loadView(activeItem.getAttribute('data-target'));
    }

    console.log('CycleSync Frontend Shell Initialized v13.');
});
