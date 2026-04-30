let cachedSummaryData = null;
let cachedDemographicsData = null;
let riskChart, ageChart, genderChart, vehicleChart, behaviorChart, vehicleAgeChart;

export function initActuarial() {
    const btnViewRegional = document.getElementById('btn-view-regional');
    const btnViewDemographic = document.getElementById('btn-view-demographic');
    const regionalCharts = document.getElementById('regional-charts');
    const demographicCharts = document.getElementById('demographic-charts');

    if (btnViewRegional && btnViewDemographic && regionalCharts && demographicCharts) {
        btnViewRegional.addEventListener('click', () => {
            btnViewRegional.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.remove('text-slate-400', 'hover:text-white');

            btnViewDemographic.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.add('text-slate-400', 'hover:text-white');

            regionalCharts.classList.remove('hidden');
            demographicCharts.classList.add('hidden');
            setTimeout(() => {
                if (typeof window.Chart !== 'undefined') {
                    for (let id in window.Chart.instances) {
                        window.Chart.instances[id].resize();
                    }
                }
            }, 50);
        });

        btnViewDemographic.addEventListener('click', () => {
            btnViewDemographic.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.remove('text-slate-400', 'hover:text-white');

            btnViewRegional.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.add('text-slate-400', 'hover:text-white');

            demographicCharts.classList.remove('hidden');
            regionalCharts.classList.add('hidden');
            setTimeout(() => {
                if (typeof window.Chart !== 'undefined') {
                    for (let id in window.Chart.instances) {
                        window.Chart.instances[id].resize();
                    }
                }
            }, 50);
        });
    }

    loadExecutiveSummary();
    loadDemographics();
}

async function loadExecutiveSummary() {
    try {
        if (cachedSummaryData) {
            renderExecutiveSummary(cachedSummaryData);
            return;
        }

        document.getElementById('kpi-total-fleet').innerText = 'Loading...';
        document.getElementById('kpi-avg-premium').innerText = 'Loading...';
        document.getElementById('kpi-discount').innerText = 'Loading...';
        document.getElementById('kpi-claims-reduction').innerText = 'Loading...';

        const res = await fetch('/api/actuarial/summary');
        if (!res.ok) throw new Error("HTTP error " + res.status);
        const data = await res.json();

        cachedSummaryData = data;
        renderExecutiveSummary(data);
    } catch (error) {
        console.error("Failed to load executive summary:", error);
    }
}

function renderExecutiveSummary(data) {
    const kpis = data.kpis;
    const regional = data.regional_breakdown;

    document.getElementById('kpi-total-fleet').innerText = kpis.total_monitored_fleet.toLocaleString();
    document.getElementById('kpi-avg-premium').innerText = '€' + kpis.average_premium_eur.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    const discountElem = document.getElementById('kpi-discount');
    discountElem.innerText = kpis.average_discount_pct.toFixed(1) + '%';
    if (kpis.average_discount_pct < 0) {
        discountElem.classList.replace('text-emerald-400', 'text-emerald-500');
    } else {
        discountElem.classList.replace('text-emerald-400', 'text-red-500');
    }

    document.getElementById('kpi-claims-reduction').innerText = kpis.claims_reduction_pct.toFixed(1) + '%';

    // Render Regional Chart
    const regions = regional.map(r => r.region);
    const projected = regional.map(r => r.projected_accidents);
    const registered = regional.map(r => r.registered_claims);

    Chart.defaults.color = '#aaa';
    Chart.defaults.borderColor = '#333';

    if (riskChart) riskChart.destroy();
    riskChart = new Chart(document.getElementById('riskChart'), {
        type: 'bar',
        data: {
            labels: regions,
            datasets: [
                { label: 'Registered Claims (Baseline)', data: registered, backgroundColor: 'rgba(120, 120, 120, 0.6)' },
                { label: 'Projected Claims (Telematics)', data: projected, backgroundColor: 'rgba(226, 185, 59, 0.9)' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#fff' } },
                datalabels: { display: false }
            },
            scales: {
                y: { grid: { color: '#333' }, ticks: { color: '#aaa' } },
                x: { grid: { display: false }, ticks: { color: '#aaa' } }
            }
        }
    });
}

async function loadDemographics() {
    try {
        if (cachedDemographicsData) {
            renderDemographics(cachedDemographicsData);
            return;
        }

        const res = await fetch('/api/actuarial/deep-dive');
        const d = await res.json();

        cachedDemographicsData = d;
        renderDemographics(d);
    } catch (error) {
        console.error("Failed to load demographics:", error);
    }
}

function renderDemographics(d) {
    Chart.defaults.color = '#aaa';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

    if (ageChart) ageChart.destroy();
    ageChart = new Chart(document.getElementById('ageChart'), {
        type: 'bar',
        data: { labels: Object.keys(d.age_groups), datasets: [{ label: 'Projected Claims', data: Object.values(d.age_groups), backgroundColor: '#4CAF50' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    if (genderChart) genderChart.destroy();
    genderChart = new Chart(document.getElementById('genderChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(d.genders), datasets: [{ data: Object.values(d.genders), backgroundColor: ['#2196F3', '#E91E63'], borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
    });

    if (vehicleChart) vehicleChart.destroy();
    vehicleChart = new Chart(document.getElementById('vehicleChart'), {
        type: 'bar',
        data: { labels: Object.keys(d.vehicle_types), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_types), backgroundColor: '#FF9800' }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    if (behaviorChart) behaviorChart.destroy();
    behaviorChart = new Chart(document.getElementById('behaviorChart'), {
        type: 'bar',
        data: { labels: Object.keys(d.behaviors), datasets: [{ label: 'Projected Claims', data: Object.values(d.behaviors), backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    if (vehicleAgeChart) vehicleAgeChart.destroy();
    vehicleAgeChart = new Chart(document.getElementById('vehicleAgeChart'), {
        type: 'bar',
        data: { labels: Object.keys(d.vehicle_ages), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_ages), backgroundColor: '#9C27B0' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}
