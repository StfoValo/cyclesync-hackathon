/**
 * Adjuster Portal — Investigation list → detail workflow
 * Backed by /api/db/investigations endpoints
 */

let currentInvestigation = null;

export function initAdjuster() {
    loadInvestigationList();
    setupFilterPills();
    setupBackButton();
    setupDetailTabs();
    setupVerdictButtons();
    setupAIAnalysis();
    setupPhotoUpload();
}

// ── LIST VIEW ────────────────────────────────────────────────────────────
async function loadInvestigationList(statusFilter = '') {
    const container = document.getElementById('investigation-list');
    if (!container) return;
    container.innerHTML = '<div class="text-center py-8 text-slate-500">Loading investigations...</div>';

    try {
        const params = statusFilter ? `?status=${statusFilter}` : '';
        const resp = await fetch(`/api/db/investigations${params}`);
        const investigations = await resp.json();
        renderInvestigationList(investigations);
    } catch (e) {
        container.innerHTML = '<div class="text-center py-8 text-rose-400">Failed to load investigations</div>';
    }
}

function renderInvestigationList(investigations) {
    const container = document.getElementById('investigation-list');
    if (!investigations?.length) {
        container.innerHTML = '<div class="text-center py-8 text-slate-500">No investigations found</div>';
        return;
    }

    container.innerHTML = investigations.map(inv => {
        const statusColors = {
            open: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
            under_review: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            resolved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
        };
        const priorityColors = {
            critical: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
            high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
            medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            low: 'bg-slate-500/20 text-slate-400 border-slate-500/30'
        };
        const typeLabels = {
            collision: '💥 Collision', rear_end: '🚗 Rear-End', side_impact: '🚙 Side Impact',
            rollover: '🔄 Rollover', pedestrian: '🚶 Pedestrian'
        };
        const fraudColor = inv.fraud_risk_score >= 70 ? 'text-rose-400' : inv.fraud_risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400';
        const statusBadge = statusColors[inv.status] || statusColors.open;
        const priorityBadge = priorityColors[inv.priority] || priorityColors.medium;

        return `
        <div class="investigation-card glass-panel rounded-xl p-4 md:p-5 border border-white/5 hover:border-white/15 cursor-pointer transition-all hover:shadow-lg group" data-case="${inv.case_number}">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                        <span class="font-bold text-white text-sm">${inv.case_number}</span>
                        <span class="text-xs px-2 py-0.5 rounded-full border font-medium ${statusBadge}">${inv.status?.replace('_',' ')}</span>
                        <span class="text-xs px-2 py-0.5 rounded-full border font-medium ${priorityBadge}">${inv.priority}</span>
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                        <span class="font-mono font-bold text-white text-xs bg-black/40 px-2 py-1 rounded border border-slate-700">${inv.plate_number}</span>
                        <span class="text-sm text-slate-300">${inv.manufacturer} ${inv.model_name}</span>
                        <span class="text-xs text-slate-500">${typeLabels[inv.incident_type] || inv.incident_type}</span>
                        <span class="text-xs text-slate-500">📅 ${inv.incident_date}</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-2 line-clamp-1">${inv.incident_description || ''}</p>
                </div>
                <div class="flex items-center gap-5 shrink-0">
                    <div class="text-center">
                        <div class="text-xl font-black ${fraudColor}">${inv.fraud_risk_score}%</div>
                        <div class="text-[10px] text-slate-500 uppercase">Fraud Risk</div>
                    </div>
                    <div class="text-center">
                        <div class="text-lg font-bold text-white">${inv.speed_at_impact || '—'}<span class="text-xs text-slate-400 ml-1">km/h</span></div>
                        <div class="text-[10px] text-slate-500 uppercase">Speed</div>
                    </div>
                    <div class="text-center">
                        <div class="text-lg font-bold text-white">${inv.g_force_max || '—'}<span class="text-xs text-slate-400 ml-1">G</span></div>
                        <div class="text-[10px] text-slate-500 uppercase">G-Force</div>
                    </div>
                    <svg class="w-5 h-5 text-slate-600 group-hover:text-brand-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
            </div>
        </div>`;
    }).join('');

    // Wire card clicks
    container.querySelectorAll('.investigation-card').forEach(card => {
        card.addEventListener('click', () => openInvestigation(card.getAttribute('data-case')));
    });
}

function setupFilterPills() {
    document.querySelectorAll('.adj-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.adj-filter-btn').forEach(b => {
                b.classList.remove('bg-brand-600', 'text-white', 'border-brand-500/50');
                b.classList.add('text-slate-400', 'border-slate-700');
            });
            btn.classList.add('bg-brand-600', 'text-white', 'border-brand-500/50');
            btn.classList.remove('text-slate-400', 'border-slate-700');
            loadInvestigationList(btn.getAttribute('data-status'));
        });
    });
}

// ── DETAIL VIEW ──────────────────────────────────────────────────────────
async function openInvestigation(caseNumber) {
    try {
        const resp = await fetch(`/api/db/investigations/${encodeURIComponent(caseNumber)}`);
        const data = await resp.json();
        if (data.error) return;
        currentInvestigation = data;
        renderInvestigationDetail(data);
        document.getElementById('adjuster-list-view')?.classList.add('hidden');
        document.getElementById('adjuster-detail-view')?.classList.remove('hidden');
    } catch (e) { console.error('Failed to load investigation:', e); }
}

function renderInvestigationDetail(inv) {
    // Header
    document.getElementById('detail-case-number').textContent = inv.case_number;

    const statusColors = {open:'bg-rose-500/20 text-rose-400 border border-rose-500/30', under_review:'bg-amber-500/20 text-amber-400 border border-amber-500/30', resolved:'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'};
    const sb = document.getElementById('detail-status-badge');
    sb.textContent = inv.status?.replace('_',' ');
    sb.className = `text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[inv.status] || ''}`;

    const prioColors = {critical:'bg-rose-500/20 text-rose-400 border border-rose-500/30', high:'bg-orange-500/20 text-orange-400 border border-orange-500/30', medium:'bg-amber-500/20 text-amber-400 border border-amber-500/30'};
    const pb = document.getElementById('detail-priority-badge');
    pb.textContent = `⚡ ${inv.priority}`;
    pb.className = `text-xs px-2 py-0.5 rounded-full font-medium ${prioColors[inv.priority] || ''}`;

    document.getElementById('detail-vehicle').textContent = inv.plate_number;
    document.getElementById('detail-model').textContent = `${inv.manufacturer} ${inv.model_name} · ${inv.driver_name || ''}`;
    document.getElementById('detail-date').textContent = `📅 ${inv.incident_date}`;

    const fraudColor = inv.fraud_risk_score >= 70 ? 'text-rose-400 animate-pulse' : inv.fraud_risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400';
    document.getElementById('detail-fraud-score').className = `text-3xl font-black ${fraudColor}`;
    document.getElementById('detail-fraud-score').textContent = `${inv.fraud_risk_score}%`;
    document.getElementById('detail-speed').textContent = `${inv.speed_at_impact || '—'} km/h`;
    document.getElementById('detail-gforce').textContent = `${inv.g_force_max || '—'} G`;

    // Summary tab
    const typeLabels = {collision:'💥 Collision', rear_end:'🚗 Rear-End Collision', side_impact:'🚙 Side Impact'};
    document.getElementById('detail-incident-type').textContent = typeLabels[inv.incident_type] || inv.incident_type;
    document.getElementById('detail-location').textContent = inv.incident_location || '—';
    document.getElementById('detail-description').textContent = inv.incident_description || '—';

    document.getElementById('detail-abs').innerHTML = inv.abs_triggered ? '<span class="text-rose-400">⚠️ YES</span>' : '<span class="text-emerald-400">✅ No</span>';
    document.getElementById('detail-airbag').innerHTML = inv.airbag_deployed ? '<span class="text-rose-400">⚠️ DEPLOYED</span>' : '<span class="text-emerald-400">✅ Not deployed</span>';
    document.getElementById('detail-glateral').textContent = `${inv.g_force_lateral || '—'} G`;
    const ct = inv.coolant_temp;
    document.getElementById('detail-coolant').innerHTML = ct ? `<span class="${ct > 95 ? 'text-rose-400' : 'text-emerald-400'}">${ct}°C</span>` : '—';

    // TPMS
    const tpms = inv.tpms_snapshot || {};
    document.getElementById('detail-tpms').innerHTML = ['fl','fr','rl','rr'].map(p => {
        const v = tpms[p];
        const c = v == null ? 'text-slate-500' : v < 2.0 ? 'text-rose-400' : v < 2.2 ? 'text-amber-400' : 'text-emerald-400';
        return `<div class="bg-slate-800/50 rounded-lg p-3 border border-white/5 text-center"><div class="text-xs text-slate-500 mb-1">${p.toUpperCase()}</div><div class="font-bold ${c}">${v?.toFixed(2) ?? '—'}</div></div>`;
    }).join('');

    // Telemetry tab
    renderDetailTelemetry(inv.telemetry);

    // Components tab
    renderDetailComponents(inv.components || []);

    // AI Analysis
    const repairCost = inv.ai_repair_estimate_eur;
    document.getElementById('detail-repair-cost').textContent = repairCost ? `€${repairCost.toLocaleString()}` : '—';
    if (inv.ai_fraud_analysis) document.getElementById('detail-ai-fraud').innerHTML = `<p class="text-slate-300 text-sm leading-relaxed">${inv.ai_fraud_analysis}</p>`;
    if (inv.ai_verdict) document.getElementById('detail-verdict-content').innerHTML = `<p class="text-xl font-bold text-white mb-2">${inv.ai_verdict}</p>`;

    // Load photos
    loadPhotos(inv.case_number);

    // Show first tab
    showTab('summary');
}

function renderDetailTelemetry(tel) {
    const grid = document.getElementById('detail-telemetry-grid');
    if (!tel) { grid.innerHTML = '<div class="text-slate-500 col-span-4">No telemetry data</div>'; return; }
    const cell = (l, v) => `<div class="bg-slate-800/50 rounded-lg p-3 border border-white/5"><p class="text-xs text-slate-400 mb-1">${l}</p><p class="text-white font-medium text-sm">${v || '—'}</p></div>`;

    let html = cell('Odometer', tel.current_odometer_km ? `${tel.current_odometer_km.toLocaleString()} km` : '—') +
        cell('Driving Score', tel.driving_score != null ? `${tel.driving_score}/100` : '—') +
        cell('Avg Speed', tel.avg_speed_kmh ? `${tel.avg_speed_kmh} km/h` : '—') +
        cell('Coolant', tel.coolant_temp_c ? `${tel.coolant_temp_c}°C` : 'N/A') +
        cell('Oil Temp', tel.oil_temp_c ? `${tel.oil_temp_c}°C` : 'N/A') +
        cell('Engine RPM', tel.engine_rpm ? `${Math.round(tel.engine_rpm)}` : 'N/A') +
        cell('Brake Pressure', tel.brake_pressure_bar ? `${tel.brake_pressure_bar} bar` : '—') +
        cell('Throttle', tel.throttle_position_pct ? `${tel.throttle_position_pct}%` : '—');

    if (tel.has_blackbox) {
        html += cell('Accel X (G)', tel.accel_x_g?.toFixed(3)) +
            cell('Accel Y (G)', tel.accel_y_g?.toFixed(3)) +
            cell('Accel Z (G)', tel.accel_z_g?.toFixed(3)) +
            cell('GPS', tel.gps_lat ? `${tel.gps_lat.toFixed(4)}, ${tel.gps_lon.toFixed(4)}` : '—') +
            cell('Heading', tel.gps_heading_deg ? `${tel.gps_heading_deg}°` : '—') +
            cell('Gyro Roll', tel.gyro_roll_deg ? `${tel.gyro_roll_deg}°` : '—') +
            cell('Gyro Yaw', tel.gyro_yaw_deg ? `${tel.gyro_yaw_deg}°` : '—') +
            cell('Event Type', `<span class="text-rose-400 font-bold uppercase">${tel.blackbox_event_type || 'normal'}</span>`);
    }
    grid.innerHTML = html;
}

function renderDetailComponents(components) {
    const grid = document.getElementById('detail-components-grid');
    if (!components?.length) { grid.innerHTML = '<div class="text-slate-500">No component data</div>'; return; }

    grid.innerHTML = components.map(c => {
        const wear = c.wear_percent || 0;
        const health = 100 - wear;
        const status = c.health_status || (wear > 80 ? 'critical' : wear > 60 ? 'warning' : 'healthy');
        const color = status === 'critical' ? 'text-rose-400' : status === 'warning' ? 'text-amber-400' : 'text-emerald-400';
        const barColor = status === 'critical' ? 'bg-rose-500' : status === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
        const borderColor = status === 'critical' ? 'border-rose-500/30' : status === 'warning' ? 'border-amber-500/30' : 'border-emerald-500/30';
        const catIcons = {tire:'🛞', brake_pad:'🛑', ev_battery:'🔋', brake_disc:'💿'};

        return `<div class="bg-slate-800/50 rounded-lg p-4 border ${borderColor}">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-white">${catIcons[c.category] || '⚙️'} ${c.category} ${c.position ? `(${c.position})` : ''}</span>
                <span class="text-xs font-bold ${color} uppercase">${status}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-1.5 mb-2"><div class="${barColor} rounded-full h-1.5" style="width:${health}%"></div></div>
            <div class="text-xs text-slate-400">${c.brand || ''} ${c.model_name || ''} · ${health}% health</div>
        </div>`;
    }).join('');
}

function setupBackButton() {
    document.getElementById('btn-back-to-list')?.addEventListener('click', () => {
        document.getElementById('adjuster-detail-view')?.classList.add('hidden');
        document.getElementById('adjuster-list-view')?.classList.remove('hidden');
        currentInvestigation = null;
    });
}

function setupDetailTabs() {
    document.querySelectorAll('.detail-tab').forEach(tab => {
        tab.addEventListener('click', () => showTab(tab.getAttribute('data-tab')));
    });
}

function showTab(tabName) {
    document.querySelectorAll('.detail-tab').forEach(t => {
        t.classList.remove('text-white', 'border-brand-500');
        t.classList.add('text-slate-400', 'border-transparent');
    });
    document.querySelectorAll('.detail-tab-content').forEach(c => c.classList.add('hidden'));

    const activeTab = document.querySelector(`.detail-tab[data-tab="${tabName}"]`);
    if (activeTab) { activeTab.classList.add('text-white', 'border-brand-500'); activeTab.classList.remove('text-slate-400', 'border-transparent'); }
    document.getElementById(`tab-${tabName}`)?.classList.remove('hidden');
}

function setupVerdictButtons() {
    document.querySelectorAll('.verdict-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const verdict = btn.getAttribute('data-verdict');
            const verdictLabels = {approved:'✅ Claim Approved', partial:'⚠️ Partially Approved', denied:'❌ Claim Denied'};
            const verdictColors = {approved:'text-emerald-400', partial:'text-amber-400', denied:'text-rose-400'};
            const container = document.getElementById('detail-verdict-content');
            container.innerHTML = `<div class="text-5xl mb-4">${verdict === 'approved' ? '✅' : verdict === 'denied' ? '❌' : '⚠️'}</div>
                <p class="text-2xl font-bold ${verdictColors[verdict]} mb-2">${verdictLabels[verdict]}</p>
                <p class="text-sm text-slate-400 mt-2">Verdict issued on ${new Date().toLocaleDateString()} for case ${currentInvestigation?.case_number || '—'}</p>`;
        });
    });
}

// ── PHOTOS ────────────────────────────────────────────────────────────────

async function loadPhotos(caseNumber) {
    const grid = document.getElementById('detail-photos-grid');
    if (!grid) return;
    try {
        const resp = await fetch(`/api/db/investigations/${encodeURIComponent(caseNumber)}/photos`);
        const photos = await resp.json();
        if (!photos?.length) {
            grid.innerHTML = '<div class="text-slate-500 text-sm col-span-3">No photos uploaded yet. Use the Upload button to add damage documentation.</div>';
            return;
        }
        grid.innerHTML = photos.map(p => `
            <div class="group relative rounded-xl overflow-hidden border border-white/10 hover:border-brand-500/50 transition-all cursor-pointer">
                <img src="/static/img/investigations/${p.filename}" alt="${p.caption || 'Damage photo'}"
                    class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                    onerror="this.src='data:image/svg+xml,<svg xmlns=&quot;http://www.w3.org/2000/svg&quot; viewBox=&quot;0 0 400 300&quot;><rect fill=&quot;%231e293b&quot; width=&quot;400&quot; height=&quot;300&quot;/><text x=&quot;200&quot; y=&quot;150&quot; fill=&quot;%2364748b&quot; text-anchor=&quot;middle&quot; font-size=&quot;14&quot;>Photo not found</text></svg>'">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="absolute bottom-0 left-0 right-0 p-3 transform translate-y-full group-hover:translate-y-0 transition-transform">
                    <p class="text-white text-xs font-medium">${p.caption || 'Damage photo'}</p>
                    <p class="text-slate-400 text-[10px] mt-0.5">${p.photo_type} · ${new Date(p.uploaded_at).toLocaleDateString()}</p>
                </div>
                <div class="absolute top-2 right-2 bg-black/60 rounded-full px-2 py-0.5 text-[10px] text-slate-300 uppercase">${p.photo_type}</div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = '<div class="text-rose-400 text-sm col-span-3">Failed to load photos</div>';
    }
}

function setupPhotoUpload() {
    document.getElementById('photo-upload-input')?.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (!files?.length || !currentInvestigation) return;

        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('caption', `Uploaded: ${file.name}`);
            formData.append('photo_type', 'damage');
            try {
                await fetch(`/api/db/investigations/${encodeURIComponent(currentInvestigation.case_number)}/photos`, {
                    method: 'POST', body: formData
                });
            } catch (err) { console.error('Upload failed:', err); }
        }
        // Reload photos
        loadPhotos(currentInvestigation.case_number);
        e.target.value = ''; // Reset input
    });
}

// ── AI ANALYSIS ───────────────────────────────────────────────────────────

function setupAIAnalysis() {
    document.getElementById('btn-run-ai-analysis')?.addEventListener('click', runAIAnalysis);
}

async function runAIAnalysis() {
    if (!currentInvestigation) return;
    const caseNumber = currentInvestigation.case_number;
    const lang = localStorage.getItem('cyclesync_lang') || 'en';
    const btn = document.getElementById('btn-run-ai-analysis');
    const fraudContainer = document.getElementById('detail-ai-fraud');
    const damageContainer = document.getElementById('detail-ai-damage');

    // Disable button during analysis
    btn.disabled = true;
    btn.innerHTML = '<div class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div> <span>Analyzing...</span>';

    // Reset containers
    fraudContainer.innerHTML = '<p class="text-slate-300 text-sm italic animate-pulse">🔄 AI is analyzing telemetry, components, and incident data...</p>';
    damageContainer.innerHTML = '';

    try {
        const resp = await fetch(`/api/ai/investigation/${encodeURIComponent(caseNumber)}?lang=${lang}`);
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        // Stream into the fraud container
        fraudContainer.innerHTML = '';

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, {stream: true});
            fullText += chunk;

            // Render markdown-ish content
            fraudContainer.innerHTML = renderMarkdown(fullText);
            fraudContainer.scrollTop = fraudContainer.scrollHeight;
        }

        // Final render with full markdown
        fraudContainer.innerHTML = renderMarkdown(fullText);
        fraudContainer.style.maxHeight = '600px';
        fraudContainer.style.overflowY = 'auto';

    } catch (err) {
        fraudContainer.innerHTML = `<p class="text-rose-400 text-sm">❌ AI analysis failed: ${err.message}</p>`;
    }

    // Re-enable button
    btn.disabled = false;
    btn.innerHTML = '🤖 <span>Re-run AI Analysis</span>';
}

function renderMarkdown(text) {
    // Basic markdown → HTML conversion
    let html = text
        .replace(/### (.*)/g, '<h3 class="text-lg font-bold text-white mt-4 mb-2">$1</h3>')
        .replace(/## (.*)/g, '<h2 class="text-xl font-bold text-white mt-5 mb-2">$1</h2>')
        .replace(/# (.*)/g, '<h1 class="text-2xl font-bold text-white mt-6 mb-3">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
        .replace(/^\- (.*)/gm, '<li class="text-slate-300 text-sm ml-4">$1</li>')
        .replace(/^\* (.*)/gm, '<li class="text-slate-300 text-sm ml-4">$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');

    // Wrap consecutive <li> in <ul>
    html = html.replace(/(<li.*?<\/li>(<br>)?)+/g, (match) => {
        return '<ul class="list-disc space-y-1 my-2">' + match.replace(/<br>/g, '') + '</ul>';
    });

    return `<div class="text-slate-300 text-sm leading-relaxed prose-sm">${html}</div>`;
}