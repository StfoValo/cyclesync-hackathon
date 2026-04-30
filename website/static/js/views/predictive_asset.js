let vsiRegChart, brkRegChart, tirRegChart, vsiGlbChart, brkGlbChart, tirGlbChart;

export function initPredictiveAsset() {
    loadVSIDashboard();
}

async function loadVSIDashboard() {
    try {
        const res = await fetch('/api/actuarial/vsi');
        if (!res.ok) throw new Error("HTTP error " + res.status);
        const p = await res.json();
        
        const metrics = p.metrics;
        const vsiVal = metrics.avg_vsi_score;
        const kpiVsi = document.getElementById('kpi-vsi');
        if (kpiVsi) {
            kpiVsi.innerText = `${vsiVal.toFixed(1)}/100`;
            kpiVsi.className = `text-3xl font-bold ${vsiVal > 75 ? 'text-emerald-400' : vsiVal > 60 ? 'text-amber-400' : 'text-red-500'}`;
        }
        
        const kpiCritical = document.getElementById('kpi-critical');
        if (kpiCritical) kpiCritical.innerText = parseInt(metrics.total_critical_assets).toLocaleString();
        
        const kpiHardware = document.getElementById('kpi-hardware-cost');
        if (kpiHardware) kpiHardware.innerText = '€' + metrics.projected_hardware_claims_eur.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

        const cleanRegional = p.regional.filter(r => !r.region.includes("Unipol") && r.region.trim() !== "");
        const regions = cleanRegional.map(r => r.region);
        
        const vsiS = cleanRegional.map(r => r.vsi[0]);
        const vsiW = cleanRegional.map(r => r.vsi[1]);
        const vsiC = cleanRegional.map(r => r.vsi[2]);
        
        const brkS = cleanRegional.map(r => r.brakes[0]);
        const brkW = cleanRegional.map(r => r.brakes[1]);
        const brkC = cleanRegional.map(r => r.brakes[2]);
        
        const tirS = cleanRegional.map(r => r.tires[0]);
        const tirW = cleanRegional.map(r => r.tires[1]);
        const tirC = cleanRegional.map(r => r.tires[2]);

        const gVsi = Object.values(p.global.overall_vsi);
        const gBrk = Object.values(p.global.brakes);
        const gTir = Object.values(p.global.tires);

        Chart.register(ChartDataLabels);
        Chart.defaults.color = '#aaa';
        Chart.defaults.borderColor = '#333'; 

        const commonStackOptions = {
            responsive: true, maintainAspectRatio: false, indexAxis: 'y',
            plugins: { 
                legend: { position: 'bottom', labels: { color: '#fff' } },
                datalabels: { display: false } 
            },
            scales: { x: { stacked: true, grid: { color: '#333' } }, y: { stacked: true, grid: { display: false } } }
        };

        if (vsiRegChart) vsiRegChart.destroy();
        vsiRegChart = new Chart(document.getElementById('vsiRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
            { label: 'Safe', data: vsiS, backgroundColor: '#00A67E' },
            { label: 'Warning', data: vsiW, backgroundColor: '#E2B93B' },
            { label: 'Critical', data: vsiC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

        if (brkRegChart) brkRegChart.destroy();
        brkRegChart = new Chart(document.getElementById('brakeRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
            { label: 'Safe (>6mm)', data: brkS, backgroundColor: '#00A67E' },
            { label: 'Warning (3-6mm)', data: brkW, backgroundColor: '#E2B93B' },
            { label: 'Critical (<3mm)', data: brkC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

        if (tirRegChart) tirRegChart.destroy();
        tirRegChart = new Chart(document.getElementById('tireRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
            { label: 'Safe (>4mm)', data: tirS, backgroundColor: '#00A67E' },
            { label: 'Warning (2-4mm)', data: tirW, backgroundColor: '#E2B93B' },
            { label: 'Critical (<2mm)', data: tirC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

        const dOptions = { 
            responsive: true, 
            maintainAspectRatio: false, 
            cutout: '65%', 
            plugins: { 
                legend: { position: 'bottom' },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value, ctx) => {
                        let sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        if (sum === 0) return '';
                        let pct = (value * 100 / sum).toFixed(1) + '%';
                        return (value * 100 / sum) > 5 ? pct : '';
                    }
                }
            } 
        };

        if (vsiGlbChart) vsiGlbChart.destroy();
        vsiGlbChart = new Chart(document.getElementById('vsiGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gVsi, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
        
        if (brkGlbChart) brkGlbChart.destroy();
        brkGlbChart = new Chart(document.getElementById('brakeGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gBrk, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
        
        if (tirGlbChart) tirGlbChart.destroy();
        tirGlbChart = new Chart(document.getElementById('tireGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gTir, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
        
    } catch (error) {
        console.error("Failed to load VSI dashboard:", error);
    }
}
