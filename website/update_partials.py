import os
import re

# Dictionary to hold mappings
en_dict = {}
it_dict = {}

def process_file(filepath):
    # This is a manual-like replacement definition
    # format: [(original_str, key, en_translation, it_translation)]
    replacements = []
    
    if "telemetry_tab" in filepath:
        replacements = [
            ("Live Fleet Telemetry", "tel-title", "Live Fleet Telemetry", "Telemetria Flotta in Tempo Reale"),
            ("Real-time geographical tracking and fleet metrics.", "tel-subtitle", "Real-time geographical tracking and fleet metrics.", "Tracciamento geografico in tempo reale e metriche della flotta."),
            ("Live\n            Monitored Fleet", "tel-btn-live", "Live Monitored Fleet", "Flotta Monitorata in Diretta"),
            ("Conventioned\n            Network", "tel-btn-network", "Conventioned Network", "Rete Convenzionata"),
        ]
    elif "executive_tab" in filepath:
        replacements = [
            ("Executive Risk Summary", "exec-title", "Executive Risk Summary", "Riepilogo Rischi Esecutivo"),
            ("Actuarial financial projections and demographic deep dives.", "exec-subtitle", "Actuarial financial projections and demographic deep dives.", "Proiezioni finanziarie attuariali e approfondimenti demografici."),
            ("Regional\n            Overview", "exec-btn-regional", "Regional Overview", "Panoramica Regionale"),
            ("Demographics", "exec-btn-demo", "Demographics", "Demografia"),
            ("Total Monitored Fleet", "exec-kpi-total", "Total Monitored Fleet", "Flotta Totale Monitorata"),
            ("Avg Premium (EUR)", "exec-kpi-avg", "Avg Premium (EUR)", "Premio Medio (EUR)"),
            ("Telematics Discount", "exec-kpi-disc", "Telematics Discount", "Sconto Telematica"),
            ("Claims Reduction", "exec-kpi-claims", "Claims Reduction", "Riduzione Sinistri"),
            ("Claims by Driver Age Group", "exec-chart-age", "Claims by Driver Age Group", "Sinistri per Fascia d'Età"),
            ("Claims by Gender", "exec-chart-gender", "Claims by Gender", "Sinistri per Genere"),
            ("Claims by Vehicle Category", "exec-chart-vehicle", "Claims by Vehicle Category", "Sinistri per Categoria Veicolo"),
            ("Claims by Behavioral Risk", "exec-chart-behavior", "Claims by Behavioral Risk", "Sinistri per Rischio Comportamentale"),
            ("Claims by Vehicle Age (Italian RCA)", "exec-chart-vehage", "Claims by Vehicle Age (Italian RCA)", "Sinistri per Età Veicolo (RCA Italiana)"),
        ]
    elif "asset_tab" in filepath:
        replacements = [
            ("Predictive Asset Risk", "asset-title", "Predictive Asset Risk", "Rischio Asset Predittivo"),
            ("Vehicle State Index (VSI) and component degradation analytics.", "asset-subtitle", "Vehicle State Index (VSI) and component degradation analytics.", "Indice di Stato del Veicolo (VSI) e analisi del degrado dei componenti."),
            ("Fleet Average VSI Score", "asset-kpi-vsi", "Fleet Average VSI Score", "Punteggio VSI Medio Flotta"),
            ("Vehicles in Critical State", "asset-kpi-crit", "Vehicles in Critical State", "Veicoli in Stato Critico"),
            ("Projected Hardware Claims", "asset-kpi-hw", "Projected Hardware Claims", "Sinistri Hardware Previsti"),
            ("Regional Fleet Safety Index (VSI) Breakdown", "asset-chart-vsi", "Regional Fleet Safety Index (VSI) Breakdown", "Ripartizione Regionale Indice Sicurezza Flotta (VSI)"),
            ("Regional Brake Pad Degradation Matrix", "asset-chart-brake", "Regional Brake Pad Degradation Matrix", "Matrice Regionale Degrado Pastiglie Freni"),
            ("Regional Tire Tread Wear Analytics", "asset-chart-tire", "Regional Tire Tread Wear Analytics", "Analisi Regionale Usura Battistrada Pneumatici"),
            ("Global VSI", "asset-chart-gvsi", "Global VSI", "VSI Globale"),
            ("Global Brakes", "asset-chart-gbrake", "Global Brakes", "Freni Globali"),
            ("Global Tires", "asset-chart-gtire", "Global Tires", "Pneumatici Globali"),
        ]
    elif "ai_tab" in filepath:
        replacements = [
            ("AI Routing Directive", "ai-title", "AI Routing Directive", "Direttiva di Routing IA"),
            ("LLM-powered strategic intelligence and policy recommendations.", "ai-subtitle", "LLM-powered strategic intelligence and policy recommendations.", "Intelligenza strategica basata su LLM e raccomandazioni di policy."),
            ("📍 Select Target\n            Region:", "ai-sel-region", "📍 Select Target Region:", "📍 Seleziona Regione Target:"),
            ("Generate Strategy", "ai-btn-gen", "Generate Strategy", "Genera Strategia"),
            ("Telematics AI", "ai-term-title", "Telematics AI", "IA Telematica"),
            ("Now", "ai-term-now", "Now", "Ora"),
            ("Awaiting actuarial input...", "ai-term-wait", "Awaiting actuarial input...", "In attesa di input attuariale..."),
            ("📈 Post-Dispatch\n                Conversion Funnel", "ai-funnel-title", "📈 Post-Dispatch Conversion Funnel", "📈 Imbuto di Conversione Post-Invio"),
            ("Total Devices Targeted", "ai-kpi-target", "Total Devices Targeted", "Dispositivi Totali Targettizzati"),
            ("Notification Open Rate", "ai-kpi-open", "Notification Open Rate", "Tasso di Apertura Notifiche"),
            ("Repairs Booked (Network)", "ai-kpi-booked", "Repairs Booked (Network)", "Riparazioni Prenotate (Rete)"),
            ("Est. Claims Prevented (ROI)", "ai-kpi-roi", "Est. Claims Prevented (ROI)", "Sinistri Evitati Stimati (ROI)"),
        ]
    elif "esg_tab" in filepath:
        replacements = [
            ("ESG & Circular Economy", "esg-title", "ESG & Circular Economy", "ESG & Economia Circolare"),
            ("Virtual emissions sensor and component second-life ledger.", "esg-subtitle", "Virtual emissions sensor and component second-life ledger.", "Sensore di emissioni virtuale e registro seconda vita componenti."),
            ("Virtual Emissions\n        Sensor", "esg-virt-sensor", "Virtual Emissions Sensor", "Sensore di Emissioni Virtuale"),
            ("Baseline CO2 (Tons)", "esg-base-co2", "Baseline CO2 (Tons)", "CO2 di Base (Tonnellate)"),
            ("Real Telematics CO2 (Tons)", "esg-real-co2", "Real Telematics CO2 (Tons)", "CO2 Telematica Reale (Tonnellate)"),
            ("Total CO2 Saved (Tons)", "esg-saved-co2", "Total CO2 Saved (Tons)", "Totale CO2 Risparmiata (Tonnellate)"),
            ("Equivalent Trees Planted", "esg-trees", "Equivalent Trees Planted", "Alberi Equivalenti Piantati"),
            ("The Second Life\n        Component Ledger", "esg-ledger", "The Second Life Component Ledger", "Il Registro dei Componenti Seconda Vita"),
            ("Tires Recovered", "esg-tires", "Tires Recovered", "Pneumatici Recuperati"),
            ("Brake Pads Recovered", "esg-brakes", "Brake Pads Recovered", "Pastiglie Freni Recuperate"),
            ("EV Batteries Recovered", "esg-batts", "EV Batteries Recovered", "Batterie EV Recuperate"),
            ("♻️ AI Component Triage &\n        Reverse Logistics", "esg-triage", "♻️ AI Component Triage & Reverse Logistics", "♻️ Triage Componenti IA & Logistica Inversa"),
            ("Bridging Birth, Life, and Second Life.", "esg-triage-sub", "Bridging Birth, Life, and Second Life.", "Colmare il divario tra Nascita, Vita e Seconda Vita."),
            ("Select\n                Region", "esg-sel-region", "Select Region", "Seleziona Regione"),
            ("Run Component Triage", "esg-btn-run", "Run Component Triage", "Esegui Triage Componenti"),
            ("1. OEM Blueprint Ingestion &rarr;", "esg-step-1", "1. OEM Blueprint Ingestion &rarr;", "1. Acquisizione Progetti OEM &rarr;"),
            ("2. Telemetry Wear Analysis &rarr;", "esg-step-2", "2. Telemetry Wear Analysis &rarr;", "2. Analisi Usura Telemetria &rarr;"),
            ("3. Second-Life Routing", "esg-step-3", "3. Second-Life Routing", "3. Routing Seconda Vita"),
            ("Awaiting regional selection to begin triage...", "esg-term-wait", "Awaiting regional selection to begin triage...", "In attesa di selezione regionale per iniziare il triage..."),
        ]

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for orig, key, en, it in replacements:
        en_dict[key] = en
        it_dict[key] = it
        
        # Replace in html with span or modify existing tag
        # The safest way is to find the exact text and add data-i18n to its container.
        # But for script we can just regex replace if it's within a tag.
        
        # simple heuristic: replace >text< with >text< and add data-i18n to the preceding tag if possible.
        # Actually, let's just do a string replace of `orig` to `<span data-i18n="key">orig</span>` if we can't do it cleanly.
        # But wait, some are inside button or h3. Let's do regex to add attribute.
        
        # Instead of parsing, I will just manually insert `data-i18n="key"` where appropriate or wrap with span.
        # It's easier:
        pattern = re.compile(rf'(>[^<]*?)({re.escape(orig)})([^>]*?<)', re.DOTALL)
        
        def rep(match):
            return f'{match.group(1)}<span data-i18n="{key}">{match.group(2)}</span>{match.group(3)}'
            
        content = pattern.sub(rep, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

base_dir = "c:/Users/pietr/OneDrive/Desktop/hackaton/website/static/partials"
files = ["telemetry_tab.html", "executive_tab.html", "asset_tab.html", "ai_tab.html", "esg_tab.html"]

for file in files:
    process_file(os.path.join(base_dir, file))

import json
with open('c:/Users/pietr/OneDrive/Desktop/hackaton/website/en.json', 'w', encoding='utf-8') as f:
    json.dump(en_dict, f, ensure_ascii=False)
with open('c:/Users/pietr/OneDrive/Desktop/hackaton/website/it.json', 'w', encoding='utf-8') as f:
    json.dump(it_dict, f, ensure_ascii=False)
