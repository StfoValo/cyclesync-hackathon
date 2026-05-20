import { initVehiclePassport } from './vehicle_passport.js?v=17';
import { initRegistry, loadRegistryTable } from './registry.js?v=17';

export function initTelemetry() {
    const mapFrame = document.getElementById('map-frame');
    if (mapFrame) mapFrame.src = '/api/fleet/map?view=fleet';

    // Initialize modules
    initVehiclePassport();
    initRegistry();

    // View toggle buttons
    const btnFleet = document.getElementById('btn-view-fleet');
    const btnRegistry = document.getElementById('btn-view-registry');
    const btnSuppliers = document.getElementById('btn-view-suppliers');
    const mapPanel = document.getElementById('map-view-panel');
    const registryPanel = document.getElementById('registry-view-panel');
    const filtersPanel = document.getElementById('registry-filters');
    const passportPanel = document.getElementById('vehicle-passport-panel');

    function activateBtn(btn) {
        [btnFleet, btnRegistry, btnSuppliers].forEach(b => {
            if (!b) return;
            b.classList.remove('bg-brand-600', 'text-white', 'shadow-lg');
            b.classList.add('text-slate-400', 'hover:text-white');
        });
        btn.classList.add('bg-brand-600', 'text-white', 'shadow-lg');
        btn.classList.remove('text-slate-400', 'hover:text-white');
    }

    function showView(view) {
        passportPanel?.classList.add('hidden');
        if (view === 'map') {
            mapPanel?.classList.remove('hidden');
            registryPanel?.classList.add('hidden');
            filtersPanel?.classList.add('hidden');
            activateBtn(btnFleet);
            if (mapFrame && !mapFrame.src.includes('fleet')) mapFrame.src = '/api/fleet/map?view=fleet';
        } else if (view === 'registry') {
            mapPanel?.classList.add('hidden');
            registryPanel?.classList.remove('hidden');
            filtersPanel?.classList.remove('hidden');
            activateBtn(btnRegistry);
            loadRegistryTable();
        } else if (view === 'suppliers') {
            mapPanel?.classList.remove('hidden');
            registryPanel?.classList.add('hidden');
            filtersPanel?.classList.add('hidden');
            activateBtn(btnSuppliers);
            if (mapFrame) mapFrame.src = '/api/fleet/map?view=suppliers';
        }
    }

    btnFleet?.addEventListener('click', () => showView('map'));
    btnRegistry?.addEventListener('click', () => showView('registry'));
    btnSuppliers?.addEventListener('click', () => showView('suppliers'));
}
