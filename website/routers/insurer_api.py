from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import folium
from models.insurer_models.actuarial_model import ActuarialModel
from models.insurer_models.fleet_model import FleetModel

SERVICE_PROVIDERS = [
    {"name": "Autofficina Sprint", "type": "Officina", "lat": 45.5421, "lon": 9.2014, "region": "Lombardia"},
    {"name": "Pneus Master", "type": "Gommista", "lat": 41.8905, "lon": 12.4942, "region": "Lazio"},
    {"name": "Meccanica Elite", "type": "Officina", "lat": 37.5013, "lon": 15.0742, "region": "Sicilia"},
    {"name": "Garage Centrale", "type": "Officina", "lat": 40.8522, "lon": 14.2681, "region": "Campania"},
    {"name": "Tutto Gomme Nord", "type": "Gommista", "lat": 45.4381, "lon": 12.3185, "region": "Veneto"},
    {"name": "RiparaAuto 24h", "type": "Officina", "lat": 44.4949, "lon": 11.3426, "region": "Emilia-Romagna"},
    {"name": "Wheel Center Advanced", "type": "Gommista", "lat": 45.0703, "lon": 7.6869, "region": "Piemonte"},
    {"name": "Officina del Sole", "type": "Officina", "lat": 41.1171, "lon": 16.8719, "region": "Puglia"},
    {"name": "Pneus Express", "type": "Gommista", "lat": 43.7696, "lon": 11.2558, "region": "Toscana"},
    {"name": "Carrozzeria Sud", "type": "Officina", "lat": 38.9054, "lon": 16.5873, "region": "Calabria"},
    {"name": "Battistrada Sicuro", "type": "Gommista", "lat": 39.2238, "lon": 9.1217, "region": "Sardegna"},
    {"name": "Service Rossi", "type": "Officina", "lat": 43.6158, "lon": 13.5189, "region": "Marche"},
    {"name": "Officina Adriatica", "type": "Officina", "lat": 42.4618, "lon": 14.2161, "region": "Abruzzo"},
    {"name": "Gomme & Co. Elite", "type": "Gommista", "lat": 46.0711, "lon": 13.2373, "region": "Friuli-Venezia Giulia"},
    {"name": "Meccanica Ligure", "type": "Officina", "lat": 44.4056, "lon": 8.9463, "region": "Liguria"},
    {"name": "Alpina Service", "type": "Officina", "lat": 46.0679, "lon": 11.1211, "region": "Trentino-Alto Adige"},
    {"name": "Pneus Umbria", "type": "Gommista", "lat": 43.1107, "lon": 12.3908, "region": "Umbria"},
    {"name": "Lucania Motors", "type": "Officina", "lat": 40.6333, "lon": 15.8000, "region": "Basilicata"},
    {"name": "Molise Gomme", "type": "Gommista", "lat": 41.5603, "lon": 14.6599, "region": "Molise"},
    {"name": "Garage Monte Bianco", "type": "Officina", "lat": 45.7373, "lon": 7.3201, "region": "Valle d'Aosta"}
]

router = APIRouter()
actuarial_model = ActuarialModel()
fleet_model = FleetModel()

@router.get("/api/actuarial/summary")
def get_actuarial_summary():
    return actuarial_model.generate_executive_summary(account_id=0)

@router.get("/api/actuarial/deep-dive")
def get_demographic_deep_dive():
    return actuarial_model.get_demographic_deep_dive()

@router.get("/api/actuarial/vsi")
def get_asset_risk_portfolio():
    return actuarial_model.get_asset_risk_portfolio()

@router.get("/api/fleet/map", response_class=HTMLResponse)
def get_fleet_map(view: str = 'fleet'):
    regional_kpis = fleet_model.get_regional_kpis(0)
    
    # FIX 1: Lock the map perfectly onto the center of Italy
    fleet_map = folium.Map(
        location=[41.8719, 12.5674], 
        zoom_start=6, 
        tiles='CartoDB dark_matter', 
        zoom_control=False
    )
    
    css = "<style>.leaflet-tile-pane { filter: brightness(1.2) contrast(0.9); }</style>"
    fleet_map.get_root().header.add_child(folium.Element(css))
    
    if view == 'fleet':
        for r in regional_kpis:
            if r['center_lat'] is None or r['center_lon'] is None:
                continue
            
            html_popup = f"""
            <div style="width: 270px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 12px; border-radius: 8px;">
                <h3 style="margin: 0 0 10px 0; color: white; border-bottom: 1px solid #555; padding-bottom: 5px;">📍 {r['region_name']}</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>Tracked Vehicles:</span><span style="color: white; font-weight: bold;">{r['total_cars']:,}</span>
                </div>
                
                <div style="background-color: #1a1a1a; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="font-size: 11px; color: #888; margin-bottom: 5px; text-transform: uppercase;">Behavioral Risk Clustering</div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; color: #ccc;">
                        <span>↳ Critical (High-G):</span><span style="color: #FF5A5A; font-weight: bold;">{r['risk_high']:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; color: #ccc;">
                        <span>↳ Moderate:</span><span style="color: #E2B93B; font-weight: bold;">{r['risk_moderate']:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #ccc;">
                        <span>↳ Safe (Eco):</span><span style="color: #00A67E; font-weight: bold;">{r['risk_safe']:,}</span>
                    </div>
                </div>
            </div>
            """
            
            # FIX 2: Use sharp, intuitive map pointers instead of overlapping bubbles
            marker_color = "green" 
            if r['risk_high'] > r['risk_safe']:
                marker_color = "red" 
            elif r['risk_moderate'] > r['risk_safe']:
                marker_color = "orange" 
            
            folium.Marker(
                location=[r['center_lat'], r['center_lon']],
                popup=folium.Popup(html_popup, max_width=320),
                icon=folium.Icon(color=marker_color, icon='car', prefix='fa')
            ).add_to(fleet_map)
            
    elif view == 'suppliers':
        for sup in SERVICE_PROVIDERS:
            icon_color = "blue" if "Officina" in sup['type'] else "orange"
            icon_type = "wrench" if "Officina" in sup['type'] else "life-ring"
            
            html_popup = f"""
            <div style="width: 220px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 10px; border-radius: 8px; border: 1px solid {icon_color};">
                <h3 style="margin: 0 0 5px 0; color: white;">🛡️ {sup['name']}</h3>
                <div style="color: {icon_color}; font-weight: bold; margin-bottom: 10px;">{sup['type']} Convenzionata</div>
                <div style="font-size: 12px; color: #bbb;">Region: {sup['region']}</div>
            </div>
            """
            
            folium.Marker(
                location=[sup['lat'], sup['lon']],
                popup=folium.Popup(html_popup, max_width=250),
                icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
            ).add_to(fleet_map)

    return HTMLResponse(fleet_map.get_root().render())

@router.get("/api/actuarial/esg")
async def get_esg_dashboard():
    """Fetches the precomputed ESG and Circular Economy metrics."""
    try:
        import sqlite3, json, os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui_cache.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # --- THE FIX: Correct table, correct columns, and correct key ('esg_metrics') ---
        cursor.execute("SELECT json_data FROM api_cache WHERE endpoint_key='esg_metrics'")
        
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return {"error": "ESG cache not found"}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


@router.get("/api/esg/components")
def get_esg_components():
    """Returns the full second-life component inventory from the database."""
    from database import get_db
    import json
    conn = get_db()
    rows = conn.execute("""SELECT c.*, v.plate_number FROM components c
        LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
        WHERE c.status != 'installed'
        ORDER BY c.category, c.updated_at DESC""").fetchall()
    conn.close()
    result = []
    for r in rows:
        specs = {}
        if r["specs_json"]:
            try: specs = json.loads(r["specs_json"])
            except: pass
        subtype_str = f"{r['brand']} {r['model_name']}"
        if specs.get("size"): subtype_str += f" {specs['size']}"
        type_map = {"tire": "Tire", "brake_pad": "Brake Pad", "brake_disc": "Brake Disc", "ev_battery": "EV Battery"}
        result.append({
            "serial": r["serial_number"], "type": type_map.get(r["category"], r["category"]),
            "subtype": subtype_str, "wear_pct": r["wear_percent"],
            "vehicle": r["plate_number"] or "N/A", "replaced": r["removed_date"] or r["created_at"],
            "recommendation": r["ai_recommendation"] or "Pending AI Analysis",
            "facility": r["destination_facility"] or "TBD",
            "value_eur": r["recovery_value_eur"] or 0, "co2_saved_kg": r["co2_saved_kg"] or 0,
            "reason": r["ai_reasoning"] or "Analysis pending.",
        })
    return result


# ── INVESTIGATION / CLAIMS ENDPOINTS ─────────────────────────────────────
@router.get("/api/db/investigations")
def list_investigations(status: str = None, priority: str = None):
    """List all investigations with optional status/priority filters."""
    from database import get_db
    import json
    conn = get_db()
    where = ["1=1"]
    params = []
    if status:
        where.append("i.status = ?"); params.append(status)
    if priority:
        where.append("i.priority = ?"); params.append(priority)
    rows = conn.execute(f"""SELECT i.*, v.plate_number, cm.model_name, cm.manufacturer
        FROM investigations i
        JOIN vehicles v ON i.vehicle_vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        WHERE {' AND '.join(where)}
        ORDER BY i.created_at DESC""", params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/api/db/investigations/{case_id}")
def get_investigation(case_id: str):
    """Get full investigation detail with linked vehicle and components."""
    from database import get_db
    import json
    conn = get_db()
    inv = conn.execute("""SELECT i.*, v.plate_number, v.driver_name, v.color, v.weight_kg, v.power_hp,
        cm.model_name, cm.manufacturer, cm.powertrain, cm.drivetrain
        FROM investigations i
        JOIN vehicles v ON i.vehicle_vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        WHERE i.case_number = ? OR CAST(i.id AS TEXT) = ?""", (case_id, case_id)).fetchone()
    if not inv:
        conn.close()
        return {"error": f"Investigation '{case_id}' not found"}

    # Get vehicle telemetry
    telem = conn.execute("SELECT * FROM vehicle_telemetry WHERE vin = ?", (inv["vehicle_vin"],)).fetchone()
    # Get vehicle components
    components = conn.execute("SELECT * FROM components WHERE vehicle_vin = ? ORDER BY category, position", (inv["vehicle_vin"],)).fetchall()
    # Get maintenance history
    maintenance = conn.execute("SELECT * FROM maintenance_events WHERE vehicle_vin = ? ORDER BY event_date DESC LIMIT 10", (inv["vehicle_vin"],)).fetchall()
    conn.close()

    result = dict(inv)
    result["telemetry"] = dict(telem) if telem else None
    result["components"] = [dict(c) for c in components]
    result["maintenance"] = [dict(m) for m in maintenance]
    if result.get("tpms_snapshot_json"):
        try: result["tpms_snapshot"] = json.loads(result["tpms_snapshot_json"])
        except: result["tpms_snapshot"] = {}
    return result


@router.get("/api/db/components")
def list_all_components(
    category: str = None, status: str = None, brand: str = None,
    vehicle_vin: str = None, min_wear: float = None, max_wear: float = None,
    page: int = 1, per_page: int = 50
):
    """Browse all components with filters — for ESG enhanced browsing."""
    from database import get_db
    import json
    conn = get_db()
    where = ["1=1"]
    params = []
    if category:
        where.append("c.category = ?"); params.append(category)
    if status:
        where.append("c.status = ?"); params.append(status)
    if brand:
        where.append("c.brand = ?"); params.append(brand)
    if vehicle_vin:
        where.append("c.vehicle_vin = ?"); params.append(vehicle_vin)
    if min_wear is not None:
        where.append("c.wear_percent >= ?"); params.append(min_wear)
    if max_wear is not None:
        where.append("c.wear_percent <= ?"); params.append(max_wear)

    total = conn.execute(f"SELECT COUNT(*) FROM components c WHERE {' AND '.join(where)}", params).fetchone()[0]
    offset = (page - 1) * per_page
    rows = conn.execute(f"""SELECT c.*, v.plate_number FROM components c
        LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
        WHERE {' AND '.join(where)}
        ORDER BY c.category, c.wear_percent DESC
        LIMIT ? OFFSET ?""", params + [per_page, offset]).fetchall()
    conn.close()

    components = []
    for r in rows:
        d = dict(r)
        if d.get("specs_json"):
            try: d["specs"] = json.loads(d["specs_json"])
            except: d["specs"] = {}
        components.append(d)
    return {"components": components, "total": total, "page": page, "per_page": per_page}


@router.get("/api/db/components/stats")
def get_component_stats():
    """Aggregate ESG stats for dashboard KPIs."""
    from database import get_db
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    stocked = conn.execute("SELECT COUNT(*) FROM components WHERE status = 'stocked'").fetchone()[0]
    installed = conn.execute("SELECT COUNT(*) FROM components WHERE status = 'installed'").fetchone()[0]
    total_co2 = conn.execute("SELECT COALESCE(SUM(co2_saved_kg), 0) FROM components WHERE status != 'installed'").fetchone()[0]
    total_value = conn.execute("SELECT COALESCE(SUM(recovery_value_eur), 0) FROM components WHERE status != 'installed'").fetchone()[0]
    by_category = conn.execute("SELECT category, COUNT(*) as cnt FROM components GROUP BY category").fetchall()
    conn.close()
    return {
        "total_components": total, "stocked": stocked, "installed": installed,
        "total_co2_saved_kg": round(total_co2, 1), "total_recovery_value_eur": round(total_value, 2),
        "by_category": {r[0]: r[1] for r in by_category},
    }