"""
Vehicle Database API — CRUD endpoints backed by cyclesync.db
Replaces the old hardcoded FLEET_DB with real database queries.
"""
from fastapi import APIRouter, Query
from typing import Optional
from database import get_db
import json

router = APIRouter()

# ── LIST / SEARCH / FILTER (AutoScout24-style) ──────────────────────────
@router.get("/api/db/vehicles")
def list_vehicles(
    q: Optional[str] = "",
    country: Optional[str] = None,
    region: Optional[str] = None,
    city: Optional[str] = None,
    powertrain: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    displacement_min: Optional[int] = None,
    displacement_max: Optional[int] = None,
    power_min: Optional[int] = None,
    power_max: Optional[int] = None,
    body_type: Optional[str] = None,
    drivetrain: Optional[str] = None,
    policy_status: Optional[str] = None,
    has_blackbox: Optional[int] = None,
    sort: Optional[str] = "plate_number",
    order: Optional[str] = "asc",
    page: int = 1,
    per_page: int = 20,
):
    """List vehicles with AutoScout24-style filtering."""
    conn = get_db()
    where = ["v.policy_number IS NOT NULL"]
    params = []

    if q and len(q) >= 2:
        where.append("(v.plate_number LIKE ? OR v.vin LIKE ? OR v.driver_name LIKE ? OR cm.model_name LIKE ?)")
        qp = f"%{q}%"
        params.extend([qp, qp, qp, qp])
    if country:
        where.append("v.country = ?"); params.append(country)
    if region:
        where.append("v.region_name = ?"); params.append(region)
    if city:
        where.append("v.city = ?"); params.append(city)
    if powertrain:
        where.append("cm.powertrain = ?"); params.append(powertrain)
    if manufacturer:
        where.append("cm.manufacturer = ?"); params.append(manufacturer)
    if model:
        where.append("cm.model_name LIKE ?"); params.append(f"%{model}%")
    if year_min:
        where.append("CAST(strftime('%Y', v.production_date) AS INTEGER) >= ?"); params.append(year_min)
    if year_max:
        where.append("CAST(strftime('%Y', v.production_date) AS INTEGER) <= ?"); params.append(year_max)
    if displacement_min:
        where.append("v.displacement_cc >= ?"); params.append(displacement_min)
    if displacement_max:
        where.append("v.displacement_cc <= ?"); params.append(displacement_max)
    if power_min:
        where.append("v.power_hp >= ?"); params.append(power_min)
    if power_max:
        where.append("v.power_hp <= ?"); params.append(power_max)
    if body_type:
        where.append("v.body_type = ?"); params.append(body_type)
    if drivetrain:
        where.append("cm.drivetrain = ?"); params.append(drivetrain)
    if policy_status:
        where.append("v.policy_status = ?"); params.append(policy_status)
    if has_blackbox is not None:
        where.append("vt.has_blackbox = ?"); params.append(has_blackbox)

    where_sql = " AND ".join(where)

    # Allowed sort columns
    sort_map = {
        "plate_number": "v.plate_number", "model": "cm.model_name",
        "year": "v.production_date", "vsi_score": "vt.driving_score",
        "premium": "v.premium_eur", "region": "v.region_name",
        "driver": "v.driver_name", "odometer": "vt.current_odometer_km",
    }
    sort_col = sort_map.get(sort, "v.plate_number")
    order_sql = "DESC" if order == "desc" else "ASC"

    # Count
    count_sql = f"""SELECT COUNT(*) FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE {where_sql}"""
    total = conn.execute(count_sql, params).fetchone()[0]

    # Fetch page
    offset = (page - 1) * per_page
    sql = f"""SELECT v.vin, v.plate_number, cm.model_name, cm.manufacturer, cm.powertrain, cm.drivetrain,
        v.production_date, v.color, v.body_type, v.region_name, v.city, v.driver_name,
        v.policy_number, v.policy_status, v.insurer, v.premium_eur, v.power_hp, v.displacement_cc,
        v.telematics_discount, v.claims_count, v.weight_kg,
        vt.driving_score, vt.current_odometer_km, vt.has_blackbox,
        vt.battery_soc, vt.last_sync_timestamp
        FROM vehicles v
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE {where_sql}
        ORDER BY {sort_col} {order_sql}
        LIMIT ? OFFSET ?"""
    params.extend([per_page, offset])
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    vehicles = []
    for r in rows:
        year = r["production_date"][:4] if r["production_date"] else "N/A"
        vehicles.append({
            "vin": r["vin"], "plate": r["plate_number"],
            "model": r["model_name"], "manufacturer": r["manufacturer"],
            "year": int(year) if year != "N/A" else None,
            "powertrain": r["powertrain"], "drivetrain": r["drivetrain"],
            "color": r["color"], "body_type": r["body_type"],
            "region": r["region_name"], "city": r["city"],
            "driver": r["driver_name"],
            "policy_number": r["policy_number"],
            "policy_status": r["policy_status"],
            "insurer": r["insurer"], "premium": r["premium_eur"],
            "power_hp": r["power_hp"], "displacement_cc": r["displacement_cc"],
            "telematics_discount": r["telematics_discount"],
            "claims_count": r["claims_count"], "weight_kg": r["weight_kg"],
            "vsi_score": r["driving_score"],
            "odometer_km": r["current_odometer_km"],
            "has_blackbox": bool(r["has_blackbox"]) if r["has_blackbox"] is not None else False,
            "battery_soc": r["battery_soc"],
            "last_sync": r["last_sync_timestamp"],
        })

    return {"vehicles": vehicles, "total": total, "page": page, "per_page": per_page, "pages": max(1, (total + per_page - 1) // per_page)}


# ── FILTER VALUES (for cascading dropdowns) ──────────────────────────────
@router.get("/api/db/vehicles/filters")
def get_filter_values():
    """Return available filter options for the UI dropdowns."""
    conn = get_db()
    regions = [r[0] for r in conn.execute("SELECT DISTINCT region_name FROM vehicles WHERE policy_number IS NOT NULL AND region_name IS NOT NULL ORDER BY region_name").fetchall()]
    manufacturers = [r[0] for r in conn.execute("SELECT DISTINCT manufacturer FROM car_models WHERE manufacturer IS NOT NULL ORDER BY manufacturer").fetchall()]
    powertrains = [r[0] for r in conn.execute("SELECT DISTINCT powertrain FROM car_models WHERE powertrain IS NOT NULL ORDER BY powertrain").fetchall()]
    body_types = [r[0] for r in conn.execute("SELECT DISTINCT body_type FROM vehicles WHERE policy_number IS NOT NULL AND body_type IS NOT NULL ORDER BY body_type").fetchall()]
    drivetrains = [r[0] for r in conn.execute("SELECT DISTINCT drivetrain FROM car_models WHERE drivetrain IS NOT NULL ORDER BY drivetrain").fetchall()]
    insurers = [r[0] for r in conn.execute("SELECT DISTINCT insurer FROM vehicles WHERE insurer IS NOT NULL ORDER BY insurer").fetchall()]
    cities = [r[0] for r in conn.execute("SELECT DISTINCT city FROM vehicles WHERE policy_number IS NOT NULL AND city IS NOT NULL ORDER BY city").fetchall()]
    conn.close()
    return {"regions": regions, "manufacturers": manufacturers, "powertrains": powertrains, "body_types": body_types, "drivetrains": drivetrains, "insurers": insurers, "cities": cities}

# ── MODELS BY MANUFACTURER (cascading) ──────────────────────────────────
@router.get("/api/db/vehicles/models/{manufacturer}")
def get_models_by_manufacturer(manufacturer: str):
    conn = get_db()
    models = [r[0] for r in conn.execute("SELECT DISTINCT model_name FROM car_models WHERE manufacturer = ? ORDER BY model_name", (manufacturer,)).fetchall()]
    conn.close()
    return {"models": models}

# ── FULL PASSPORT ────────────────────────────────────────────────────────
@router.get("/api/db/vehicles/{vin}")
def get_vehicle(vin: str):
    """Full Digital Passport — vehicle + telemetry + components + maintenance."""
    conn = get_db()

    v = conn.execute("""SELECT v.*, cm.model_name, cm.manufacturer, cm.powertrain, cm.drivetrain,
        cm.displacement_cc as cm_disp, cm.power_hp as cm_hp, cm.weight_kg as cm_wt
        FROM vehicles v JOIN car_models cm ON v.model_id = cm.id WHERE v.vin = ?""", (vin,)).fetchone()
    if not v:
        conn.close()
        return {"error": f"Vehicle '{vin}' not found"}

    telem = conn.execute("SELECT * FROM vehicle_telemetry WHERE vin = ?", (vin,)).fetchone()
    components = conn.execute("SELECT * FROM components WHERE vehicle_vin = ? AND status = 'installed' ORDER BY category, position", (vin,)).fetchall()
    maintenance = conn.execute("SELECT * FROM maintenance_events WHERE vehicle_vin = ? ORDER BY event_date DESC LIMIT 20", (vin,)).fetchall()
    investigations = conn.execute("SELECT case_number, incident_date, incident_type, status, priority, fraud_risk_score FROM investigations WHERE vehicle_vin = ? ORDER BY incident_date DESC", (vin,)).fetchall()
    conn.close()

    year = v["production_date"][:4] if v["production_date"] else "N/A"

    return {
        "vin": v["vin"], "plate": v["plate_number"],
        "identity": {
            "model": v["model_name"], "manufacturer": v["manufacturer"],
            "year": int(year) if year != "N/A" else None,
            "color": v["color"], "drivetrain": v["drivetrain"],
            "powertrain": v["powertrain"], "body_type": v["body_type"],
            "power_hp": v["power_hp"] or v["cm_hp"],
            "displacement_cc": v["displacement_cc"] or v["cm_disp"],
            "weight_kg": v["weight_kg"] or v["cm_wt"],
            "driver": v["driver_name"],
            "registration_date": v["registration_date"],
            "region": v["region_name"], "city": v["city"], "country": v["country"],
        },
        "insurance": {
            "policy_number": v["policy_number"],
            "policy_type": v["policy_type"],
            "insurer": v["insurer"],
            "premium_eur": v["premium_eur"],
            "policy_start": v["policy_start"],
            "policy_expiry": v["policy_expiry"],
            "policy_status": v["policy_status"],
            "telematics_discount": v["telematics_discount"],
            "claims_count": v["claims_count"],
        },
        "telemetry": dict(telem) if telem else None,
        "components": [_comp_dict(c) for c in components],
        "maintenance": [dict(m) for m in maintenance],
        "investigations": [dict(i) for i in investigations],
    }

def _comp_dict(c):
    d = dict(c)
    if d.get("specs_json"):
        try: d["specs"] = json.loads(d["specs_json"])
        except: d["specs"] = {}
    return d


# ── REGISTER NEW VEHICLE ─────────────────────────────────────────────────
from fastapi import Body

@router.post("/api/db/vehicles")
def register_vehicle(data: dict = Body(...)):
    """Register a new vehicle in the fleet."""
    conn = get_db()
    # Ensure car_model exists
    model_name = f"{data.get('manufacturer','')} {data.get('model','')}"
    existing = conn.execute("SELECT id FROM car_models WHERE model_name=?", (model_name,)).fetchone()
    if existing:
        model_id = existing[0]
    else:
        cur = conn.execute("""INSERT INTO car_models (model_name, car_type, powertrain, drivetrain, manufacturer, displacement_cc, power_hp, weight_kg)
            VALUES (?,?,?,?,?,?,?,?)""",
            (model_name, data.get("body_type",""), data.get("powertrain",""), data.get("drivetrain",""),
             data.get("manufacturer",""), data.get("displacement_cc",0), data.get("power_hp",0), data.get("weight_kg",0)))
        model_id = cur.lastrowid

    import random
    vin = data.get("vin", f"NEW{random.randint(100000,999999):06d}VIN")
    conn.execute("""INSERT INTO vehicles (vin,plate_number,model_id,production_date,region_name,color,weight_kg,power_hp,displacement_cc,
        registration_date,status,body_type,country,city,driver_name,
        policy_number,policy_type,insurer,premium_eur,policy_start,policy_expiry,policy_status,telematics_discount,claims_count)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (vin, data.get("plate",""), model_id, f"{data.get('year',2024)}-01-01", data.get("region",""),
         data.get("color",""), data.get("weight_kg",0), data.get("power_hp",0), data.get("displacement_cc",0),
         data.get("registration_date",""), "active", data.get("body_type",""), data.get("country","IT"),
         data.get("city",""), data.get("driver_name",""),
         data.get("policy_number",""), data.get("policy_type",""), data.get("insurer",""),
         data.get("premium_eur",0), data.get("policy_start",""), data.get("policy_expiry",""),
         data.get("policy_status","active"), data.get("telematics_discount",0), 0))

    # Init empty telemetry
    conn.execute("INSERT OR IGNORE INTO vehicle_telemetry (vin, current_odometer_km, driving_score) VALUES (?,?,?)",
        (vin, data.get("odometer_km",0), 100))
    conn.commit()
    conn.close()
    return {"status": "ok", "vin": vin, "message": f"Vehicle {data.get('plate','')} registered successfully."}


# ── UPDATE VEHICLE ───────────────────────────────────────────────────────
@router.put("/api/db/vehicles/{vin}")
def update_vehicle(vin: str, data: dict = Body(...)):
    """Update editable vehicle fields."""
    conn = get_db()
    allowed = ["plate_number","color","driver_name","region_name","city","policy_number","policy_type",
               "insurer","premium_eur","policy_start","policy_expiry","policy_status","telematics_discount","status"]
    sets, vals = [], []
    for k, v in data.items():
        if k in allowed:
            sets.append(f"{k} = ?"); vals.append(v)
    if sets:
        vals.append(vin)
        conn.execute(f"UPDATE vehicles SET {', '.join(sets)} WHERE vin = ?", vals)
        conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Vehicle {vin} updated."}


# ── VEHICLE COMPONENTS ───────────────────────────────────────────────────
@router.get("/api/db/vehicles/{vin}/components")
def get_vehicle_components(vin: str, status: Optional[str] = None):
    """Get components for a specific vehicle."""
    conn = get_db()
    if status:
        rows = conn.execute("SELECT * FROM components WHERE vehicle_vin = ? AND status = ? ORDER BY category, position", (vin, status)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM components WHERE vehicle_vin = ? ORDER BY category, position", (vin,)).fetchall()
    conn.close()
    return [_comp_dict(r) for r in rows]





# ── LEGACY ENDPOINTS (backward compatibility) ────────────────────────────
@router.get("/api/vehicles/search")
def search_vehicles_legacy(q: Optional[str] = ""):
    """Legacy search endpoint — redirects to new DB-backed search."""
    result = list_vehicles(q=q, per_page=50)
    return [{"plate": v["plate"], "model": v["model"], "manufacturer": v["manufacturer"], "vsi": v["vsi_score"], "driver": v["driver"]} for v in result["vehicles"]]

@router.get("/api/vehicles/{plate}/passport")
def get_passport_legacy(plate: str):
    """Legacy passport endpoint — finds by plate and redirects to new endpoint."""
    conn = get_db()
    plate_clean = plate.upper().replace("-", " ").strip().replace(" ", "")
    row = conn.execute("SELECT vin FROM vehicles WHERE REPLACE(plate_number,' ','') = ? AND policy_number IS NOT NULL", (plate_clean,)).fetchone()
    conn.close()
    if row:
        return get_vehicle(row[0])
    return {"error": f"Vehicle '{plate}' not found"}


# ══════════════════════════════════════════════════════════════════════════
# DRIVER APP API
# ══════════════════════════════════════════════════════════════════════════

@router.get("/api/driver/{driver_id}")
def get_driver_profile(driver_id: int):
    """Get driver profile with linked vehicles summary."""
    conn = get_db()
    d = conn.execute("SELECT * FROM driver_accounts WHERE id=?", (driver_id,)).fetchone()
    if not d:
        conn.close()
        return {"error": "Driver not found"}
    vehicles = conn.execute("""
        SELECT v.vin, v.plate_number, cm.model_name, cm.manufacturer, v.production_date, v.color,
               cm.powertrain, v.body_type, vt.driving_score, vt.current_odometer_km, vt.has_blackbox
        FROM driver_vehicles dv
        JOIN vehicles v ON dv.vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
        WHERE dv.driver_id = ?
        ORDER BY dv.added_at
    """, (driver_id,)).fetchall()
    conn.close()
    return {
        "id": d["id"], "email": d["email"], "display_name": d["display_name"],
        "phone": d["phone"], "pinned_vin": d["pinned_vin"],
        "vehicles": [{
            "vin": v["vin"], "plate": v["plate_number"],
            "model": v["model_name"], "manufacturer": v["manufacturer"],
            "year": int(v["production_date"][:4]) if v["production_date"] else None,
            "color": v["color"], "powertrain": v["powertrain"], "body_type": v["body_type"],
            "vsi_score": v["driving_score"], "odometer_km": v["current_odometer_km"],
            "has_blackbox": bool(v["has_blackbox"]) if v["has_blackbox"] is not None else False,
            "is_pinned": v["vin"] == d["pinned_vin"],
        } for v in vehicles]
    }


@router.put("/api/driver/{driver_id}/pin/{vin}")
def pin_vehicle(driver_id: int, vin: str):
    """Set pinned/default vehicle for driver."""
    conn = get_db()
    conn.execute("UPDATE driver_accounts SET pinned_vin=? WHERE id=?", (vin, driver_id))
    conn.commit()
    conn.close()
    return {"status": "ok", "pinned_vin": vin}


@router.post("/api/driver/{driver_id}/vehicles")
def link_vehicle(driver_id: int, data: dict = Body(...)):
    """Link a vehicle to driver by plate, VIN, or passport number."""
    conn = get_db()
    search = data.get("search", "").strip()
    if not search:
        conn.close()
        return {"error": "Please provide plate number, VIN, or passport number."}
    clean = search.upper().replace("-", "").replace(" ", "")
    row = conn.execute("""SELECT vin FROM vehicles WHERE REPLACE(plate_number,' ','')=? OR vin=? OR policy_number=?""",
        (clean, search, search)).fetchone()
    if not row:
        conn.close()
        return {"error": f"No vehicle found for '{search}'."}
    try:
        conn.execute("INSERT INTO driver_vehicles (driver_id, vin) VALUES (?,?)", (driver_id, row["vin"]))
        conn.commit()
    except:
        conn.close()
        return {"error": "Vehicle already linked."}
    conn.close()
    return {"status": "ok", "vin": row["vin"]}


@router.delete("/api/driver/{driver_id}/vehicles/{vin}")
def unlink_vehicle(driver_id: int, vin: str):
    """Remove a vehicle from driver's garage."""
    conn = get_db()
    conn.execute("DELETE FROM driver_vehicles WHERE driver_id=? AND vin=?", (driver_id, vin))
    # If pinned vin was removed, clear it
    conn.execute("UPDATE driver_accounts SET pinned_vin=NULL WHERE id=? AND pinned_vin=?", (driver_id, vin))
    conn.commit()
    conn.close()
    return {"status": "ok"}


@router.post("/api/driver/{driver_id}/maintenance")
def log_maintenance(driver_id: int, data: dict = Body(...)):
    """Log a maintenance event for a vehicle."""
    conn = get_db()
    conn.execute("""INSERT INTO maintenance_events (vehicle_vin, event_date, event_type, description, mileage_km, cost_eur, facility)
        VALUES (?,?,?,?,?,?,?)""",
        (data["vin"], data.get("date", ""), data.get("type", "scheduled"),
         data.get("description", ""), data.get("mileage_km", 0),
         data.get("cost_eur", 0), data.get("facility", "")))
    conn.commit()
    conn.close()
    return {"status": "ok"}


@router.get("/api/driver/vehicle/{vin}/component-life")
def get_component_lifecycle(vin: str):
    """Estimate remaining life for each installed component based on telemetry."""
    conn = get_db()
    telem = conn.execute("SELECT * FROM vehicle_telemetry WHERE vin=?", (vin,)).fetchone()
    comps = conn.execute("SELECT * FROM components WHERE vehicle_vin=? AND status='installed' ORDER BY category, position", (vin,)).fetchall()
    vehicle = conn.execute("""SELECT v.*, cm.powertrain FROM vehicles v
        JOIN car_models cm ON v.model_id=cm.id WHERE v.vin=?""", (vin,)).fetchone()
    maint = conn.execute("SELECT * FROM maintenance_events WHERE vehicle_vin=? ORDER BY event_date DESC LIMIT 10", (vin,)).fetchall()
    conn.close()

    if not vehicle:
        return {"error": "Vehicle not found"}

    odometer = telem["current_odometer_km"] if telem else 0
    has_bb = bool(telem["has_blackbox"]) if telem else False
    vsi = telem["driving_score"] if telem else 50
    powertrain = vehicle["powertrain"] if vehicle else "petrol"

    # Determine telemetry depth
    if has_bb:
        telem_level = "full"  # TPMS, G-force, GPS, brake pressure etc.
    elif telem and telem["oil_temp_c"]:
        telem_level = "ecu"   # Basic ECU sensors
    else:
        telem_level = "minimal"  # Odometer + manual only

    results = []
    for c in comps:
        cd = _comp_dict(c)
        wear = cd.get("wear_percent", 0)
        installed_km = cd.get("installed_km", 0) or 0
        km_on_component = max(odometer - installed_km, 1)

        # Estimate remaining life based on component type
        cat = cd["category"]
        if cat == "tire":
            max_life_km = 45000 if vsi > 70 else 35000 if vsi > 40 else 25000
            wear_rate = wear / max(km_on_component, 1) * 1000  # per 1000km
            remaining_pct = max(100 - wear, 0)
            est_remaining_km = int(remaining_pct / max(wear_rate, 0.01) * 1000)
            urgency = "critical" if wear >= 80 else "warning" if wear >= 65 else "good"
            consequence = "Reduced grip, longer braking distance, risk of blowout" if wear > 75 else "Slightly reduced wet grip" if wear > 60 else "Normal operation"
        elif cat == "brake_pad":
            max_life_km = 50000 if vsi > 70 else 35000 if vsi > 40 else 20000
            wear_rate = wear / max(km_on_component, 1) * 1000
            remaining_pct = max(100 - wear, 0)
            est_remaining_km = int(remaining_pct / max(wear_rate, 0.01) * 1000)
            urgency = "critical" if wear >= 85 else "warning" if wear >= 70 else "good"
            consequence = "⚠️ SAFETY RISK: Metal-on-metal contact, disc damage, increased stopping distance" if wear > 85 else "Reduced braking efficiency, disc wear acceleration" if wear > 70 else "Normal operation"
        elif cat == "ev_battery":
            soh = cd.get("specs", {}).get("soh_percent", 100 - wear)
            est_remaining_km = int((soh - 70) / 0.005) if soh > 70 else 0  # ~0.5% degradation per 10,000km
            urgency = "critical" if soh < 75 else "warning" if soh < 85 else "good"
            consequence = "Significant range loss, potential warranty claim" if soh < 75 else "Minor range reduction" if soh < 85 else "Healthy battery"
            remaining_pct = max(soh - 70, 0) / 30 * 100  # 70% SoH = end of life
        else:
            est_remaining_km = 10000
            remaining_pct = max(100 - wear, 0)
            urgency = "good"
            consequence = ""

        # Daily km estimate for date projection
        days_since_install = max(1, (odometer - installed_km) / 35)  # rough ~35 km/day
        est_days_remaining = int(est_remaining_km / max(days_since_install, 1))

        results.append({
            **cd,
            "est_remaining_km": max(est_remaining_km, 0),
            "est_remaining_days": max(est_days_remaining, 0),
            "remaining_life_pct": round(remaining_pct, 1),
            "urgency": urgency,
            "consequence": consequence,
        })

    # VSI tips based on driving score
    tips = []
    if vsi < 50:
        tips = ["Reduce harsh braking — saves brake pads and improves score by ~5pts",
                "Maintain steady speed on highways — reduces tire wear by 20%",
                "Avoid rapid acceleration from stops — reduces fuel/energy consumption"]
    elif vsi < 75:
        tips = ["Anticipate traffic lights to coast more — improves score +3pts",
                "Check tire pressure monthly — under-inflated tires wear 25% faster"]
    else:
        tips = ["Excellent driving! Keep maintaining steady speeds",
                "Consider eco-mode for city driving — further reduces wear"]

    dtc_alerts = []
    if telem and telem["dtc_codes_json"]:
        import json as _json
        codes = _json.loads(telem["dtc_codes_json"])
        dtc_map = {"P0301":"Cylinder 1 misfire — check spark plug/ignition coil","P0420":"Catalytic converter efficiency below threshold",
                    "P0171":"System too lean — check for vacuum leaks","P0300":"Random misfires detected"}
        for code in codes:
            if code in dtc_map:
                dtc_alerts.append({"code": code, "description": dtc_map[code], "urgency": "warning"})

    return {
        "vin": vin,
        "telemetry_level": telem_level,
        "vsi_score": vsi,
        "odometer_km": odometer,
        "has_blackbox": has_bb,
        "powertrain": powertrain,
        "components": results,
        "vsi_tips": tips,
        "dtc_alerts": dtc_alerts,
        "maintenance_history": [dict(m) for m in maint],
    }

