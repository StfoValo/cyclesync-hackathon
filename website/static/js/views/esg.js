import { componentIcon } from '/static/js/icons.js?v=17';

let tiresChart, brakesChart, batteriesChart;
let cachedEsgData = null;
let isInitialized = false;
let currentFilter = '', currentStatus = '', currentPage = 1, totalComponents = 0;
const PER_PAGE = 15;

export function initESG() {
    loadESGDashboard();
    loadComponentStats();
    loadComponentTable();
    if (!isInitialized) {
        setupSubTabs();
        setupReverseLogistics();
        setupComponentFilters();
        setupStatusToggle();
        setupComponentSort();
        setupPagination();
        setupBatchRecycling();
        isInitialized = true;
    }
}

// ── Sub-Tab Navigation ───────────────────────────────────────────────────
function setupSubTabs() {
    document.querySelectorAll('.esg-subtab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.esg-subtab').forEach(b => {
                b.classList.remove('active', 'text-white', 'border-brand-500');
                b.classList.add('text-slate-400', 'border-transparent');
            });
            btn.classList.add('active', 'text-white', 'border-brand-500');
            btn.classList.remove('text-slate-400', 'border-transparent');
            document.querySelectorAll('.esg-subtab-content').forEach(c => c.classList.add('hidden'));
            const target = document.getElementById('esg-subtab-' + btn.dataset.subtab);
            if (target) target.classList.remove('hidden');
            if (btn.dataset.subtab === 'triage') loadBatchKPIs();
        });
    });
}

// ── Batch KPIs ───────────────────────────────────────────────────────────
async function loadBatchKPIs() {
    try {
        const res = await fetch('/api/db/components/stats');
        if (!res.ok) return;
        const s = await res.json();
        setText('batch-kpi-all', s.stocked);
        // Per-category stocked counts
        for (const [cat, count] of Object.entries(s.by_category || {})) {
            const stocked = await fetch(`/api/db/components?status=stocked&category=${cat}&per_page=1`).then(r=>r.json());
            setText(`batch-kpi-${cat}`, stocked.total);
        }
    } catch(e) { console.error(e); }
}

// ── Batch Recycling AI ───────────────────────────────────────────────────
function setupBatchRecycling() {
    // Card clicks set the selector
    document.querySelectorAll('.batch-category-card').forEach(card => {
        card.addEventListener('click', () => {
            const sel = document.getElementById('batch-category-select');
            if (sel) sel.value = card.dataset.category;
            document.querySelectorAll('.batch-category-card').forEach(c => c.classList.remove('border-emerald-500/50', 'bg-emerald-500/5'));
            card.classList.add('border-emerald-500/50', 'bg-emerald-500/5');
        });
    });

    const btn = document.getElementById('btn-batch-recycling');
    if (!btn) return;
    btn.addEventListener('click', async () => {
        const category = document.getElementById('batch-category-select')?.value || 'all';
        const output = document.getElementById('batch-recycling-output');
        const dot = document.getElementById('batch-status-dot');
        const statusText = document.getElementById('batch-status-text');
        if (!output) return;

        btn.disabled = true;
        const orig = btn.innerHTML;
        btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> Analyzing...';
        if (dot) { dot.classList.remove('bg-emerald-500'); dot.classList.add('bg-amber-500'); }
        if (statusText) statusText.textContent = 'AI analysis in progress...';
        output.innerHTML = '<div id="batch-content"></div>';

        try {
            const lang = localStorage.getItem('cyclesync_lang') || 'en';
            const res = await fetch(`/api/ai/batch-recycling/${encodeURIComponent(category)}?lang=${lang}`);
            if (!res.ok) throw new Error("HTTP " + res.status);
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            const contentDiv = document.getElementById('batch-content');
            let fullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                fullText += decoder.decode(value, { stream: true });
                if (contentDiv) contentDiv.innerHTML = renderMd(fullText);
                output.scrollTop = output.scrollHeight;
            }
            if (dot) { dot.classList.remove('bg-amber-500'); dot.classList.add('bg-emerald-500'); }
            if (statusText) statusText.textContent = 'Analysis complete ✓';
        } catch(e) {
            console.error(e);
            output.innerHTML = '<div class="text-rose-400 p-4">Analysis failed. Try again.</div>';
            if (statusText) statusText.textContent = 'Error';
        } finally {
            btn.disabled = false;
            btn.innerHTML = orig;
        }
    });
}

function renderMd(text) {
    let t = text.replace(/UNIPOL/gi, 'CycleSync');
    t = t.replace(/### (.*?)(?:\n|$)/g, '<h4 class="text-white font-bold text-lg border-b border-white/10 pb-2 mt-6 mb-3">$1</h4>');
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-400 font-semibold">$1</strong>');
    t = t.replace(/^\* (.*?)(?:\n|$)/gm, '<div class="flex items-start gap-2 mb-1.5"><span class="text-emerald-500 mt-0.5">•</span><span class="text-slate-300">$1</span></div>');
    t = t.replace(/\n/g, '<br>');
    return t;
}

// ── DB Stats KPIs ────────────────────────────────────────────────────────
async function loadComponentStats() {
    try {
        const res = await fetch('/api/db/components/stats');
        if (!res.ok) return;
        const s = await res.json();
        setText('esg-kpi-total-components', s.total_components.toLocaleString());
        setText('esg-kpi-stocked', s.stocked.toLocaleString());
        setText('esg-kpi-recovery-value', '€' + s.total_recovery_value_eur.toLocaleString());
    } catch(e) { console.error(e); }
}

// ── Component Table (DB-backed) ──────────────────────────────────────────
async function loadComponentTable() {
    const tbody = document.getElementById('component-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">Loading...</td></tr>';
    try {
        let url = `/api/db/components?page=${currentPage}&per_page=${PER_PAGE}`;
        if (currentFilter) url += `&category=${encodeURIComponent(currentFilter)}`;
        if (currentStatus) url += `&status=${encodeURIComponent(currentStatus)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        totalComponents = data.total;
        renderTable(data.components);
        updatePagination(data);
        updateFooter(data);
    } catch(e) {
        console.error(e);
        if (tbody) tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-rose-400">Failed to load</td></tr>';
    }
}

function renderTable(comps) {
    const tbody = document.getElementById('component-table-body');
    if (!tbody || !comps.length) { if(tbody) tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">No components</td></tr>'; return; }
    const labels = { tire:'Tire', brake_pad:'Brake Pad', ev_battery:'EV Battery' };
    tbody.innerHTML = comps.map((c,i) => {
        const rec = c.ai_recommendation || '—';
        const isReuse = /Retread|Resell|Second-Life|Grid Storage/i.test(rec);
        const isRecycle = /Recycle|Recovery|Smelting|Black Mass/i.test(rec);
        const rowB = c.status==='installed' ? 'border-l-2 border-l-brand-500' : isReuse ? 'border-l-2 border-l-emerald-500' : isRecycle ? 'border-l-2 border-l-amber-500' : 'border-l-2 border-l-slate-600';
        const recC = isReuse ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' : isRecycle ? 'text-amber-400 bg-amber-500/10 border-amber-500/30' : 'text-slate-400 bg-slate-500/10 border-slate-500/30';
        const w = c.wear_percent||0;
        const wC = w>=80?'bg-rose-500':w>=60?'bg-amber-500':'bg-emerald-500';
        const wT = w>=80?'text-rose-400':w>=60?'text-amber-400':'text-emerald-400';
        const hC = {healthy:'text-emerald-400 bg-emerald-500/10',warning:'text-amber-400 bg-amber-500/10',critical:'text-rose-400 bg-rose-500/10',stocked:'text-brand-400 bg-brand-500/10'}[c.health_status]||'text-slate-400 bg-slate-500/10';
        let hint='';
        if(c.specs){if(c.category==='tire'&&c.specs.size)hint=c.specs.size;else if(c.category==='ev_battery'&&c.specs.capacity_kwh)hint=`${c.specs.capacity_kwh}kWh`;else if(c.category==='brake_pad')hint=c.specs.material||'';}
        return `<tr class="${rowB} hover:bg-white/[0.02] cursor-pointer transition-colors component-row" data-index="${i}">
            <td class="px-4 py-3 font-mono text-xs text-slate-300">${c.serial_number}</td>
            <td class="px-4 py-3"><span class="flex items-center gap-1.5">${componentIcon(c.category,'w-4 h-4')}<span class="text-white text-xs">${labels[c.category]||c.category}</span></span>${c.position?`<span class="text-[10px] text-slate-500 block mt-0.5">${c.position}</span>`:''}</td>
            <td class="px-4 py-3"><span class="text-white text-xs">${c.brand||'—'}</span><span class="text-[10px] text-slate-500 block mt-0.5">${c.model_name||'—'}${hint?' · '+hint:''}</span></td>
            <td class="px-4 py-3"><div class="flex items-center gap-2"><div class="w-16 bg-slate-700 rounded-full h-1.5"><div class="${wC} rounded-full h-1.5" style="width:${w}%"></div></div><span class="text-xs font-bold ${wT}">${w}%</span></div></td>
            <td class="px-4 py-3"><span class="font-mono font-bold text-white text-xs bg-black/40 px-1.5 py-0.5 rounded border border-slate-700">${c.plate_number||'—'}</span></td>
            <td class="px-4 py-3"><span class="text-[10px] font-bold px-2 py-1 rounded-full ${hC}">${c.status}</span></td>
            <td class="px-4 py-3">${rec!=='—'?`<span class="text-[10px] font-bold px-2 py-1 rounded-full border ${recC}">${rec}</span>`:'<span class="text-slate-600 text-xs">—</span>'}</td>
            <td class="px-4 py-3 text-xs font-bold ${c.recovery_value_eur?'text-emerald-400':'text-slate-600'}">${c.recovery_value_eur?'€'+c.recovery_value_eur.toLocaleString():'—'}</td>
            <td class="px-4 py-3 text-xs font-bold ${c.co2_saved_kg?'text-emerald-400':'text-slate-600'}">${c.co2_saved_kg?c.co2_saved_kg+' kg':'—'}</td>
        </tr>
        <tr class="component-detail hidden bg-black/20" data-detail-index="${i}"><td colspan="9" class="px-6 py-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">AI Reasoning</p><p class="text-slate-300">${c.ai_reasoning||'No AI analysis available.'}</p></div>
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">Lifecycle</p><p class="text-slate-300">Installed: ${c.installed_date||'—'} ${c.installed_km?`at ${c.installed_km.toLocaleString()} km`:''}</p>${c.removed_date?`<p class="text-slate-300">Removed: ${c.removed_date}</p>`:''}${c.destination_facility?`<p class="text-slate-300 mt-1">Facility: <span class="text-brand-400">${c.destination_facility}</span></p>`:''}</div>
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">Specs</p>${c.specs?Object.entries(c.specs).map(([k,v])=>`<p class="text-slate-300">${k}: <span class="text-white font-medium">${v}</span></p>`).join(''):'<p class="text-slate-500">—</p>'}</div>
            </div>
        </td></tr>`;
    }).join('');
    tbody.querySelectorAll('.component-row').forEach(r => r.addEventListener('click', () => {
        const d = tbody.querySelector(`[data-detail-index="${r.dataset.index}"]`);
        if(d) d.classList.toggle('hidden');
    }));
}

function updateFooter(d) {
    setText('comp-showing', `${(d.page-1)*d.per_page+1}–${Math.min(d.page*d.per_page, d.total)}`);
    setText('comp-total-count', d.total);
    fetch('/api/db/components/stats').then(r=>r.json()).then(s=>{
        setText('comp-total-value', '€'+s.total_recovery_value_eur.toLocaleString());
        setText('comp-total-co2', s.total_co2_saved_kg.toLocaleString()+' kg');
    }).catch(()=>{});
}

function updatePagination(d) {
    const tp = Math.ceil(d.total/d.per_page);
    const prev = document.getElementById('comp-prev-page'), next = document.getElementById('comp-next-page');
    setText('comp-page-info', `Page ${d.page} of ${tp}`);
    if(prev) prev.disabled = d.page<=1;
    if(next) next.disabled = d.page>=tp;
}

function setupPagination() {
    document.getElementById('comp-prev-page')?.addEventListener('click', () => { if(currentPage>1){currentPage--;loadComponentTable();} });
    document.getElementById('comp-next-page')?.addEventListener('click', () => { currentPage++; loadComponentTable(); });
}

function setupComponentFilters() {
    document.querySelectorAll('.component-filter').forEach(btn => btn.addEventListener('click', () => {
        document.querySelectorAll('.component-filter').forEach(b => { b.classList.remove('active','bg-brand-600','text-white'); b.classList.add('bg-slate-800','text-slate-400'); });
        btn.classList.add('active','bg-brand-600','text-white'); btn.classList.remove('bg-slate-800','text-slate-400');
        currentFilter = btn.dataset.filter; currentPage = 1; loadComponentTable();
    }));
}

function setupStatusToggle() {
    document.querySelectorAll('.esg-status-toggle').forEach(btn => btn.addEventListener('click', () => {
        document.querySelectorAll('.esg-status-toggle').forEach(b => { b.classList.remove('bg-brand-600','text-white'); b.classList.add('text-slate-400'); });
        btn.classList.add('bg-brand-600','text-white'); btn.classList.remove('text-slate-400');
        currentStatus = btn.dataset.status; currentPage = 1; loadComponentTable();
    }));
}

function setupComponentSort() {
    document.querySelectorAll('th[data-sort]').forEach(th => { let asc=true; th.addEventListener('click', () => { asc=!asc; }); });
}

function setText(id, val) { const el = document.getElementById(id); if(el) el.textContent = val; }
const getT = (key) => window.translations?.[localStorage.getItem('cyclesync_lang')||'en']?.[key] || key;

window.addEventListener('languageChanged', () => {
    if(tiresChart){tiresChart.destroy();tiresChart=null;}
    if(brakesChart){brakesChart.destroy();brakesChart=null;}
    if(batteriesChart){batteriesChart.destroy();batteriesChart=null;}
    if(cachedEsgData) renderESG(cachedEsgData);
});

// ── Reverse Logistics (AI Streaming) ─────────────────────────────────────
function setupReverseLogistics() {
    const btn = document.getElementById('btn-generate-manifest');
    const terminal = document.getElementById('logistics-terminal');
    const regionSelect = document.getElementById('logistics-region');
    if (!btn || !terminal || !regionSelect) return;
    btn.addEventListener('click', () => {
        const region = regionSelect.value;
        btn.disabled = true; const orig = btn.innerHTML; btn.innerHTML = getT('term-run')+'...';
        terminal.innerHTML = '';
        const spin = `<svg class="w-4 h-4 text-brand-500 animate-spin inline-block mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>`;
        const chk = `<svg class="w-4 h-4 text-emerald-400 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
        setTimeout(()=>{terminal.innerHTML+=`<div id="step1" class="text-slate-300 mb-2">${spin} Ingesting OEM Blueprints...</div>`;},0);
        setTimeout(()=>{document.getElementById('step1').innerHTML=`${chk} OEM Blueprints Ingested.`;terminal.innerHTML+=`<div id="step2" class="text-slate-300 mb-2">${spin} Analyzing VSI degradation...</div>`;},600);
        setTimeout(()=>{document.getElementById('step2').innerHTML=`${chk} Degradation Analyzed.`;terminal.innerHTML+=`<div id="step3" class="text-slate-300 mb-4">${spin} Cross-referencing recycling network...</div>`;},1200);
        setTimeout(async()=>{
            try{
                const lang=localStorage.getItem('cyclesync_lang')||'en';
                const res=await fetch(`/api/ai/circular-logistics/${encodeURIComponent(region)}?lang=${lang}`);
                if(!res.ok)throw new Error("HTTP "+res.status);
                const reader=res.body.getReader();const decoder=new TextDecoder();
                terminal.innerHTML='<div id="manifest-content"></div>';const cd=document.getElementById('manifest-content');let ft="";
                while(true){const{done,value}=await reader.read();if(done)break;ft+=decoder.decode(value,{stream:true});if(cd)cd.innerHTML=renderMd(ft);terminal.scrollTop=terminal.scrollHeight;}
            }catch(e){console.error(e);terminal.innerHTML='<div class="text-red-400 p-4 bg-red-400/10 rounded-lg border border-red-400/20">System Timeout</div>';}
            finally{btn.disabled=false;btn.innerHTML=orig;}
        },1800);
    });
}

// ── ESG Dashboard ────────────────────────────────────────────────────────
async function loadESGDashboard() {
    try {
        if(cachedEsgData){renderESG(cachedEsgData);return;}
        setText('esg-kpi-baseline','Loading...');setText('esg-kpi-real','Loading...');setText('esg-kpi-saved','Loading...');
        const res = await fetch('/api/actuarial/esg');
        if(!res.ok)throw new Error("HTTP "+res.status);
        cachedEsgData = await res.json();
        renderESG(cachedEsgData);
    }catch(e){console.error(e);setText('esg-kpi-baseline','Error');}
}

function renderESG(data) {
    const em=data.emissions, ci=data.circular_economy;
    setText('esg-kpi-baseline', em.baseline_co2_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
    setText('esg-kpi-real', em.real_telematics_co2_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
    setText('esg-kpi-saved', em.co2_saved_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
    setText('esg-kpi-tires-total', ci.recovered_tires.total_units.toLocaleString()+' Units');
    setText('esg-kpi-brakes-total', ci.recovered_brakes.total_units.toLocaleString()+' Units');
    setText('esg-kpi-batteries-total', ci.recovered_ev_batteries.total_units.toLocaleString()+' Units');
    const o={responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#cbd5e1',padding:20}}}};
    const c1=['#059669','#10b981','#34d399'],c2=['#d97706','#f59e0b','#fbbf24'],c3=['#2563eb','#3b82f6','#60a5fa'];
    const td=ci.recovered_tires.destinations;if(tiresChart)tiresChart.destroy();
    tiresChart=new window.Chart(document.getElementById('esgTiresChart'),{type:'doughnut',data:{labels:Object.keys(td).map(k=>getT('chart-'+k.split('_')[0])),datasets:[{data:Object.values(td),backgroundColor:c1,borderWidth:0}]},options:o});
    const bd=ci.recovered_brakes.destinations;if(brakesChart)brakesChart.destroy();
    brakesChart=new window.Chart(document.getElementById('esgBrakesChart'),{type:'doughnut',data:{labels:Object.keys(bd).map(k=>getT('chart-'+k.split('_')[0])),datasets:[{data:Object.values(bd),backgroundColor:c2,borderWidth:0}]},options:o});
    const ed=ci.recovered_ev_batteries.destinations;if(batteriesChart)batteriesChart.destroy();
    batteriesChart=new window.Chart(document.getElementById('esgBatteriesChart'),{type:'doughnut',data:{labels:Object.keys(ed).map(k=>getT('chart-'+k.split('_')[0])),datasets:[{data:Object.values(ed),backgroundColor:c3,borderWidth:0}]},options:o});
}