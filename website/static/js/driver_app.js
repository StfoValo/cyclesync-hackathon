// CycleSync Driver App — Main Logic
const DRIVER_ID = 1; // Demo driver
let driverData = null;
let activeVin = null;
let componentData = null;

// ── Init ─────────────────────────────────────────────────────────────────
async function initDriverApp() {
    try {
        const res = await fetch(`/api/driver/${DRIVER_ID}`);
        driverData = await res.json();
        if (driverData.error) { console.error(driverData.error); return; }
        activeVin = driverData.pinned_vin || driverData.vehicles[0]?.vin;
        renderVehicleStrip();
        renderProfileTab();
        await loadVehicleData(activeVin);
    } catch(e) { console.error('Init error:', e); }
}

// ── Vehicle Strip (Home) ─────────────────────────────────────────────────
function renderVehicleStrip() {
    const strip = document.getElementById('vehicle-strip');
    if (!strip || !driverData) return;
    strip.innerHTML = driverData.vehicles.map(v => {
        const active = v.vin === activeVin;
        const icon = v.powertrain === 'electric' ? '⚡' : v.powertrain?.includes('hybrid') ? '🔋' : '⛽';
        return `<button onclick="selectVehicle('${v.vin}')" class="shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-2xl transition-all ${active ? 'bg-brand-600 text-black shadow-[0_0_15px_rgba(0,229,255,0.3)]' : 'bg-slate-800 border border-white/10 text-white'}">
            <span class="text-lg">${icon}</span>
            <div class="text-left">
                <div class="text-xs font-bold leading-tight">${v.manufacturer} ${v.model.replace(v.manufacturer+' ','')}</div>
                <div class="text-[10px] ${active?'text-black/60':'text-slate-400'}">${v.plate}${v.is_pinned?' ⭐':''}</div>
            </div>
        </button>`;
    }).join('');
}

window.selectVehicle = async function(vin) {
    activeVin = vin;
    renderVehicleStrip();
    await loadVehicleData(vin);
};

// ── Load Vehicle Data ────────────────────────────────────────────────────
async function loadVehicleData(vin) {
    const v = driverData.vehicles.find(x => x.vin === vin);
    if (!v) return;
    // Update header
    const nameEl = document.getElementById('home-vehicle-name');
    if (nameEl) nameEl.textContent = `${v.manufacturer} ${v.model.replace(v.manufacturer+' ','')}`;
    const plateEl = document.getElementById('home-vehicle-plate');
    if (plateEl) plateEl.textContent = v.plate;

    // VSI
    const vsiEl = document.getElementById('home-vsi-score');
    if (vsiEl) vsiEl.textContent = v.vsi_score || '--';
    const vsiLabel = document.getElementById('home-vsi-label');
    const score = v.vsi_score || 0;
    if (vsiLabel) {
        if (score >= 80) { vsiLabel.textContent = 'Excellent'; vsiLabel.className = 'text-[10px] font-bold text-emerald-400 uppercase'; }
        else if (score >= 60) { vsiLabel.textContent = 'Good'; vsiLabel.className = 'text-[10px] font-bold text-brand-400 uppercase'; }
        else if (score >= 40) { vsiLabel.textContent = 'Fair'; vsiLabel.className = 'text-[10px] font-bold text-amber-400 uppercase'; }
        else { vsiLabel.textContent = 'Poor'; vsiLabel.className = 'text-[10px] font-bold text-rose-400 uppercase'; }
    }
    // VSI ring color
    const ring = document.getElementById('vsi-ring');
    if (ring) ring.style.background = `conic-gradient(${score>=70?'#10b981':score>=40?'#f59e0b':'#ef4444'} ${score*3.6}deg, #1e293b ${score*3.6}deg)`;

    // Telemetry badge
    const bbBadge = document.getElementById('home-bb-badge');
    if (bbBadge) {
        if (v.has_blackbox) { bbBadge.textContent = '📡 Full Telemetry'; bbBadge.className = 'text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full'; }
        else { bbBadge.textContent = '🔌 ECU Only'; bbBadge.className = 'text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full'; }
    }

    // Odometer
    const odoEl = document.getElementById('home-odometer');
    if (odoEl) odoEl.textContent = (v.odometer_km||0).toLocaleString() + ' km';

    // Load component lifecycle
    try {
        const res = await fetch(`/api/driver/vehicle/${vin}/component-life`);
        componentData = await res.json();
        renderComponentHealth(componentData);
        renderAlerts(componentData);
        renderVSITips(componentData.vsi_tips);
        renderDTCAlerts(componentData.dtc_alerts);
    } catch(e) { console.error(e); }
}

// ── Component Health Grid ────────────────────────────────────────────────
function renderComponentHealth(data) {
    const grid = document.getElementById('component-health-grid');
    if (!grid) return;
    const comps = data.components || [];
    if (!comps.length) { grid.innerHTML = '<p class="text-slate-500 text-sm p-4">No components tracked</p>'; return; }

    grid.innerHTML = comps.map(c => {
        const icon = c.category === 'tire' ? '🛞' : c.category === 'brake_pad' ? '🛑' : '🔋';
        const label = c.category === 'tire' ? `Tire ${c.position}` : c.category === 'brake_pad' ? `Brake ${c.position}` : 'EV Battery';
        const wear = c.wear_percent || 0;
        const barColor = c.urgency === 'critical' ? 'bg-rose-500' : c.urgency === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
        const textColor = c.urgency === 'critical' ? 'text-rose-400' : c.urgency === 'warning' ? 'text-amber-400' : 'text-emerald-400';
        const remKm = c.est_remaining_km?.toLocaleString() || '—';
        return `<div class="glass-card p-3 cursor-pointer hover:border-brand-500/30 transition-all" onclick="this.querySelector('.comp-detail').classList.toggle('hidden')">
            <div class="flex items-center justify-between mb-1.5">
                <span class="text-sm font-semibold text-white flex items-center gap-1.5">${icon} ${label}</span>
                <span class="text-[10px] font-bold ${textColor} uppercase">${c.urgency}</span>
            </div>
            <div class="flex items-center gap-2 mb-1">
                <div class="flex-1 bg-slate-800 rounded-full h-1.5"><div class="${barColor} rounded-full h-1.5" style="width:${wear}%"></div></div>
                <span class="text-xs font-bold ${textColor}">${wear}%</span>
            </div>
            <div class="flex justify-between text-[10px] text-slate-400">
                <span>~${remKm} km left</span>
                <span>${c.brand || ''}</span>
            </div>
            <div class="comp-detail hidden mt-2 pt-2 border-t border-white/5 text-[11px] text-slate-400">
                <p class="mb-1">${c.consequence || 'Normal operation'}</p>
                ${c.est_remaining_days ? `<p>Est. replacement in <span class="text-white font-bold">${c.est_remaining_days}</span> days</p>` : ''}
            </div>
        </div>`;
    }).join('');
}

// ── VSI Tips ─────────────────────────────────────────────────────────────
function renderVSITips(tips) {
    const el = document.getElementById('vsi-tips');
    if (!el || !tips?.length) return;
    el.innerHTML = tips.map(t => `<div class="flex items-start gap-2 mb-1"><span class="text-brand-400 mt-0.5">💡</span><span class="text-slate-300 text-xs">${t}</span></div>`).join('');
}

// ── DTC Alerts ───────────────────────────────────────────────────────────
function renderDTCAlerts(dtcs) {
    const el = document.getElementById('dtc-section');
    if (!el) return;
    if (!dtcs?.length) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    document.getElementById('dtc-list').innerHTML = dtcs.map(d =>
        `<div class="flex items-start gap-2 p-2 bg-amber-500/5 rounded-lg border border-amber-500/20 mb-1">
            <span class="text-amber-400 font-mono text-xs font-bold mt-0.5">${d.code}</span>
            <span class="text-slate-300 text-xs">${d.description}</span>
        </div>`
    ).join('');
}

// ── Alerts Tab ───────────────────────────────────────────────────────────
function renderAlerts(data) {
    const list = document.getElementById('alerts-list');
    if (!list) return;
    const critical = (data.components || []).filter(c => c.urgency !== 'good');
    const dtcs = data.dtc_alerts || [];

    if (!critical.length && !dtcs.length) {
        list.innerHTML = '<div class="text-center py-12 text-slate-500"><p class="text-4xl mb-2">✅</p><p class="font-semibold">All clear!</p><p class="text-xs">No maintenance alerts</p></div>';
        return;
    }

    let html = '';
    // Component alerts
    critical.sort((a,b) => (a.urgency==='critical'?0:1) - (b.urgency==='critical'?0:1));
    critical.forEach(c => {
        const icon = c.category === 'tire' ? '🛞' : c.category === 'brake_pad' ? '🛑' : '🔋';
        const label = c.category === 'tire' ? `Tire ${c.position}` : c.category === 'brake_pad' ? `Brake ${c.position}` : 'EV Battery';
        const isCrit = c.urgency === 'critical';
        const borderC = isCrit ? 'border-rose-500/30 bg-rose-500/5' : 'border-amber-500/20 bg-amber-500/5';
        const badgeC = isCrit ? 'bg-rose-500 text-white' : 'bg-amber-500 text-black';
        html += `<div class="glass-card p-4 mb-3 border ${borderC}">
            <div class="flex items-center justify-between mb-2">
                <span class="font-semibold text-white flex items-center gap-2">${icon} ${label}</span>
                <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${badgeC}">${c.urgency}</span>
            </div>
            <p class="text-xs text-slate-400 mb-2">${c.consequence}</p>
            <div class="flex items-center justify-between text-[10px]">
                <span class="text-slate-500">Wear: <span class="text-white font-bold">${c.wear_percent}%</span> · ~${c.est_remaining_km?.toLocaleString()} km left</span>
            </div>
            <button onclick="getRepairQuote('${c.category}','${c.position||''}','${c.brand||''}','${c.wear_percent}')" 
                class="mt-3 w-full bg-brand-600 hover:bg-brand-500 text-black text-xs font-bold py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5">
                💰 Get Repair Quote
            </button>
        </div>`;
    });
    // DTC alerts
    dtcs.forEach(d => {
        html += `<div class="glass-card p-4 mb-3 border border-amber-500/20 bg-amber-500/5">
            <div class="flex items-center gap-2 mb-1"><span class="font-mono text-amber-400 text-sm font-bold">⚠️ ${d.code}</span></div>
            <p class="text-xs text-slate-300">${d.description}</p>
        </div>`;
    });
    list.innerHTML = html;
}

// ── Repair Quote ─────────────────────────────────────────────────────────
window.getRepairQuote = function(category, position, brand, wear) {
    const modal = document.getElementById('quote-modal');
    const output = document.getElementById('quote-output');
    if (!modal || !output) return;
    modal.classList.remove('hidden');
    const label = category === 'tire' ? `Tire ${position}` : category === 'brake_pad' ? `Brake Pad ${position}` : 'EV Battery';
    
    // AI-estimated pricing
    const prices = {
        'tire': { low: 60, high: 120, labor: 20, name: 'tire replacement' },
        'brake_pad': { low: 40, high: 90, labor: 50, name: 'brake pad replacement' },
        'ev_battery': { low: 2000, high: 8000, labor: 200, name: 'battery service' },
    };
    const p = prices[category] || prices['tire'];
    const partCost = Math.round(p.low + (p.high - p.low) * (parseFloat(wear)/100));
    const total = partCost + p.labor;
    const discount = Math.round(total * 0.08);

    output.innerHTML = `
        <div class="text-center mb-4"><span class="text-3xl">🔧</span></div>
        <h3 class="text-lg font-bold text-white text-center mb-4">AI Repair Estimate</h3>
        <div class="glass-card p-3 mb-3">
            <div class="flex justify-between text-sm mb-1"><span class="text-slate-400">${label} (${brand})</span><span class="text-white font-bold">€${partCost}</span></div>
            <div class="flex justify-between text-sm mb-1"><span class="text-slate-400">Labor</span><span class="text-white font-bold">€${p.labor}</span></div>
            <div class="flex justify-between text-sm pt-2 border-t border-white/10"><span class="text-slate-300 font-semibold">Subtotal</span><span class="text-white font-bold">€${total}</span></div>
        </div>
        <div class="glass-card p-3 mb-3 border border-emerald-500/20 bg-emerald-500/5">
            <div class="flex justify-between text-sm"><span class="text-emerald-400 font-semibold">🎫 CycleSync Discount</span><span class="text-emerald-400 font-bold">-€${discount}</span></div>
            <div class="flex justify-between text-lg pt-2 border-t border-emerald-500/20 mt-2"><span class="text-white font-bold">Total</span><span class="text-emerald-400 font-bold">€${total - discount}</span></div>
        </div>
        <p class="text-[10px] text-slate-500 text-center mb-3">⚡ AI estimate — final price confirmed by mechanic</p>
        <button onclick="switchView('view-map')" class="w-full bg-brand-500 text-black font-bold py-2.5 rounded-xl text-sm">Find Nearest Mechanic →</button>
        <button onclick="document.getElementById('quote-modal').classList.add('hidden')" class="w-full mt-2 bg-transparent border border-white/20 text-slate-300 font-semibold py-2.5 rounded-xl text-sm">Close</button>
    `;
};

// ── SOS ──────────────────────────────────────────────────────────────────
window.triggerSOS = async function() {
    switchView('view-sos');
    const output = document.getElementById('sos-output');
    const statusEl = document.getElementById('sos-status');
    if (!output || !activeVin) return;
    output.innerHTML = '<div class="flex items-center justify-center h-32"><div class="w-8 h-8 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div></div>';
    if (statusEl) statusEl.textContent = 'Analyzing vehicle telemetry...';

    try {
        const lang = localStorage.getItem('cyclesync_lang') || 'en';
        const res = await fetch(`/api/ai/sos/${activeVin}?lang=${lang}`);
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        output.innerHTML = '<div id="sos-content"></div>';
        const cd = document.getElementById('sos-content');
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            fullText += decoder.decode(value, { stream: true });
            if (cd) cd.innerHTML = renderMd(fullText);
            output.scrollTop = output.scrollHeight;
        }
        if (statusEl) statusEl.textContent = 'Analysis complete — Help dispatched';
    } catch(e) {
        output.innerHTML = '<p class="text-rose-400 p-4">Connection error. Calling 112...</p>';
    }
};

function renderMd(t) {
    t = t.replace(/### (.*?)(?:\n|$)/g, '<h4 class="text-white font-bold text-base border-b border-white/10 pb-1 mt-4 mb-2">$1</h4>');
    t = t.replace(/## (.*?)(?:\n|$)/g, '<h3 class="text-white font-bold text-lg border-b border-white/10 pb-1 mt-4 mb-2">$1</h3>');
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong class="text-brand-400 font-semibold">$1</strong>');
    t = t.replace(/^\* (.*?)$/gm, '<div class="flex items-start gap-2 mb-1"><span class="text-brand-500">•</span><span class="text-slate-300">$1</span></div>');
    t = t.replace(/\n/g, '<br>');
    return t;
}

// ── Profile Tab ──────────────────────────────────────────────────────────
function renderProfileTab() {
    if (!driverData) return;
    const el = id => document.getElementById(id);
    if (el('profile-name')) el('profile-name').textContent = driverData.display_name;
    if (el('profile-email')) el('profile-email').textContent = driverData.email;
    if (el('profile-phone')) el('profile-phone').textContent = driverData.phone || '—';

    const list = el('profile-vehicles');
    if (!list) return;
    list.innerHTML = driverData.vehicles.map(v => {
        const icon = v.powertrain === 'electric' ? '⚡' : v.powertrain?.includes('hybrid') ? '🔋' : '⛽';
        return `<div class="glass-card p-3 mb-2 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="text-2xl">${icon}</span>
                <div>
                    <div class="text-sm font-bold text-white">${v.manufacturer} ${v.model.replace(v.manufacturer+' ','')}</div>
                    <div class="text-[10px] text-slate-400">${v.plate} · ${v.year} · ${(v.odometer_km||0).toLocaleString()} km</div>
                </div>
            </div>
            <div class="flex items-center gap-2">
                ${v.is_pinned ? '<span class="text-brand-400 text-sm">⭐</span>' : `<button onclick="pinVehicle('${v.vin}')" class="text-[10px] text-slate-500 hover:text-brand-400">Pin</button>`}
                <button onclick="unlinkVehicle('${v.vin}')" class="text-[10px] text-slate-500 hover:text-rose-400 ml-1">✕</button>
            </div>
        </div>`;
    }).join('');
}

window.pinVehicle = async function(vin) {
    await fetch(`/api/driver/${DRIVER_ID}/pin/${vin}`, { method: 'PUT' });
    location.reload();
};

window.unlinkVehicle = async function(vin) {
    if (!confirm('Remove this vehicle?')) return;
    await fetch(`/api/driver/${DRIVER_ID}/vehicles/${vin}`, { method: 'DELETE' });
    location.reload();
};

window.linkVehicle = async function() {
    const input = document.getElementById('add-vehicle-input');
    if (!input?.value) return;
    const res = await fetch(`/api/driver/${DRIVER_ID}/vehicles`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ search: input.value })
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    input.value = '';
    location.reload();
};

// ── Log Maintenance ──────────────────────────────────────────────────────
window.logMaintenance = async function() {
    const type = document.getElementById('maint-type')?.value;
    const desc = document.getElementById('maint-desc')?.value;
    const km = document.getElementById('maint-km')?.value;
    if (!type || !activeVin) return;
    await fetch(`/api/driver/${DRIVER_ID}/maintenance`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ vin: activeVin, type, description: desc || type, mileage_km: parseInt(km)||0, date: new Date().toISOString().split('T')[0] })
    });
    alert('Maintenance logged ✓');
    document.getElementById('maint-desc').value = '';
    document.getElementById('maint-km').value = '';
};

// ── View Switching ───────────────────────────────────────────────────────
window.switchView = function(targetId) {
    document.querySelectorAll('.app-view').forEach(v => v.classList.remove('active'));
    document.getElementById(targetId)?.classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(b => { b.classList.remove('text-brand-400'); b.classList.add('text-slate-500'); });
    const map = { 'view-home':'nav-home','view-map':'nav-map','view-alert':'nav-alert','view-profile':'nav-profile' };
    const navId = map[targetId];
    if (navId) { document.getElementById(navId)?.classList.add('text-brand-400'); document.getElementById(navId)?.classList.remove('text-slate-500'); }
};

// Init on load
document.addEventListener('DOMContentLoaded', () => {
    initDriverApp();
    setTimeout(() => { if (window.setLanguage) window.setLanguage(localStorage.getItem('cyclesync_lang') || 'en'); }, 50);
});
