import json
from PyQt6.QtCore import QObject
from mcp_agent_server.ai_orchestrator import AIOrchestrator

class FleetController(QObject):

    SUPPLIERS = [
        {"name": "Mirafiori Battery Hub", "type": "Pack Assembly & Second Life", "lat": 45.0315, "lon": 7.6254, "region": "Southern Europe"},
        {"name": "ACC Gigafactory (Termoli)", "type": "Cell Manufacturing", "lat": 41.9880, "lon": 15.0160, "region": "Southern Europe"},
        {"name": "LG Energy Solution (Wrocław)", "type": "Cell Manufacturing", "lat": 51.0438, "lon": 16.9410, "region": "Central Europe"},
        {"name": "CATL (Erfurt)", "type": "Cell Manufacturing", "lat": 50.8932, "lon": 11.0374, "region": "DACH Region"},
        {"name": "Samsung SDI (Kokomo)", "type": "Cell Manufacturing", "lat": 40.4864, "lon": -86.1336, "region": "North America"}
    ]

    def __init__(self, map_view, ai_dashboard_view, model, account_id):
        super().__init__()
        self.map_view = map_view            
        self.ai_view = ai_dashboard_view    
        self.model = model
        self.account_id = account_id
        
        self.agent = AIOrchestrator()
        
        # Wire the trigger button on the NEW AI view
        self.ai_view.btn_request_ai_analysis.clicked.connect(self.trigger_ai_agent)
        
        # Listen for the signal from the Map View (Simulation)
        self.map_view.simulate_requested.connect(self.run_simulation)
        
        # --- 🚀 THE MISSING LINK: WIRE THE TOGGLE SWITCH ---
        self.map_view.view_toggle.currentItemChanged.connect(self.load_fleet_data)
        # ---------------------------------------------------
        
        self.load_fleet_data()
        self.refresh_ai_dashboard_visuals()

    def run_simulation(self):
        """Triggers the Monte Carlo simulation and refreshes both UIs."""
        # 1. Tell the model to generate the new cars
        self.model.simulate_regional_fleet(self.account_id)
        
        # 2. Refresh the Map View
        self.load_fleet_data()
        
        # 3. Refresh the AI Dashboard Histogram
        self.refresh_ai_dashboard_visuals()

    def load_fleet_data(self, *args):
        """Passes both the fleet data and the supplier data to the map."""
        fleet_data = self.model.get_regional_kpis(self.account_id)
        
        # --- FIX: Robust active view detection ---
        active_view = 'fleet' # Default
        
        # 1. If triggered by a user click, the signal passes the routeKey directly
        if args and isinstance(args[0], str):
            active_view = args[0]
            
        # 2. If triggered during startup, safely check the readable text of the button
        else:
            current_item = self.map_view.view_toggle.currentItem()
            if current_item and 'Supplier' in current_item.text():
                active_view = 'suppliers'
        # ------------------------------------------
        
        if hasattr(self.map_view, 'render_map'):
            self.map_view.render_map(fleet_data, self.SUPPLIERS, active_view)

    def refresh_ai_dashboard_visuals(self):
        """Extracts data from the model to draw the histogram and top stats."""
        raw_analytics = self.model.get_bev_regional_analytics(self.account_id)
        
        total_bevs = 0
        total_lithium = 0.0
        total_critical = 0
        regions = []
        
        # We need TWO separate arrays for the grouped histogram
        eol_0_3_counts = []
        eol_3_6_counts = []
        
        for r in raw_analytics:
            total_bevs += r['total_bevs']
            total_lithium += r['lithium_tons_at_risk']
            
            count_0_3 = r['cohorts']['0-3_months']
            count_3_6 = r['cohorts']['3-6_months']
            critical = count_0_3 + count_3_6
            total_critical += critical
            
            # Only add to graph if they have critical batteries to avoid clutter
            # Only add to graph if they have critical batteries to avoid clutter
            if critical > 0:
                raw_name = r['region_name'].split('(')[0].strip()
                
                # --- FIX: STACK THE WORDS TO PREVENT HORIZONTAL OVERLAP ---
                words = raw_name.split()
                if len(words) > 1:
                    # Turns "Northern Italy" into "Northern\nItaly"
                    short_name = f"{words[0]}\n{' '.join(words[1:])}"
                else:
                    short_name = raw_name
                # -----------------------------------------------------------
                
                regions.append(short_name)
                eol_0_3_counts.append(count_0_3)
                eol_3_6_counts.append(count_3_6)
                
        self.ai_view.populate_dashboard(total_bevs, total_lithium, total_critical, regions, eol_0_3_counts, eol_3_6_counts)

    def trigger_ai_agent(self):
        """Packages the data and streams the Gemini response to the UI."""
        payload = self.get_ai_ingestion_payload()
        self.ai_view.prepare_ai_stream()
        stream = self.agent.run_oem_battery_analysis(payload)
        self.ai_view.stream_ai_response(stream)

    def get_ai_ingestion_payload(self) -> str:
        """Structures the JSON payload with BOTH Fleet and Supplier data."""
        regional_analytics = self.model.get_bev_regional_analytics(self.account_id)
        
        payload = {
            "task": "predictive_supply_chain_analysis", 
            "global_suppliers": self.SUPPLIERS, # <--- Added Suppliers to the AI Brain!
            "regions": []
        }
        
        for r in regional_analytics:
            payload["regions"].append({
                "Region": r['region_name'],
                "Total Active BEVs": r['total_bevs'],
                "Average Fleet SoH (%)": round(r['avg_soh'], 1),
                "Critical EOL Cohorts": {
                    "0-3 Months to EOL": r['cohorts']['0-3_months'],
                    "3-6 Months to EOL": r['cohorts']['3-6_months']
                },
                "Estimated Material Yield (Tons)": round(r['lithium_tons_at_risk'], 2)
            })
 
        return json.dumps(payload, indent=4)