import os
import json
import sqlite3
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from mcp_agent_server.ai_orchestrator import AIOrchestrator

router = APIRouter()
orchestrator = AIOrchestrator()

# --- THE FIX: A bulletproof local cache reader ---
def get_cache(key: str):
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui_cache.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # --- THE FIX: Correct table (api_cache) and columns (json_data, endpoint_key) ---
        cursor.execute("SELECT json_data FROM api_cache WHERE endpoint_key=?", (key,))
        
        row = cursor.fetchone()
        conn.close()
        return json.loads(row[0]) if row else {}
    except Exception as e:
        print(f"⚠️ Cache read error: {e}")
        return {}
        
@router.get("/api/ai/orchestrate/{region}")
async def orchestrate_ai(request: Request, region: str, lang: str = "en"): 
    client_ip = request.client.host
    print(f"🧠 USER {client_ip} triggered AI Strategy for region: {region} (Lang: {lang})")
    
    portfolio = get_cache('asset_risk_portfolio')
    region_data = next((r for r in portfolio.get("regional", []) if r["region"] == region), None)
    
    payload = json.dumps(region_data) if region_data else f'{{"region": "{region}", "status": "no data"}}'
    
    def generate():
        for chunk in orchestrator.run_actuarial_strategy_analysis(payload, region, lang):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/api/ai/circular-logistics/{region}")
async def orchestrate_circular_logistics(region: str, lang: str = 'en'):
    payload = build_reverse_logistics_payload(region)
    def generate():
        # Pass lang into the orchestrator
        for chunk in orchestrator.run_circular_logistics_analysis(payload, region, lang):
            yield chunk
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/api/ai/chat")
async def ai_chat(message: str, context: str = "risk_summary", lang: str = "en"):
    """Streaming chat endpoint for context-aware AI chatbots."""
    # Fetch context data based on the chat context
    context_data = ""
    if context == "risk_summary":
        portfolio = get_cache('asset_risk_portfolio')
        summary = get_cache('actuarial_summary')
        context_data = json.dumps({"portfolio": portfolio, "summary": summary}, indent=2)
    
    def generate():
        for chunk in orchestrator.run_risk_chat(message, context_data, lang):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/event-stream")


def build_reverse_logistics_payload(target_region: str) -> str:
    """
    Creates a hyper-local ESG routing payload for the AI using cached data.
    Gracefully handles regions that might not have BEV telemetry.
    """
    # 1. Fetch Actuarial Risk Portfolio (Tires & Brakes) from Cache
    portfolio = get_cache('asset_risk_portfolio')
    region_actuarial = next((r for r in portfolio.get("regional", []) if r["region"] == target_region), None)

    # 2. Fetch BEV Telemetry from Cache
    bev_analytics = get_cache('bev_regional_analytics')
    region_bev = next((r for r in bev_analytics if r["region_name"] == target_region), None)

    # 3. Check for core Actuarial data
    if not region_actuarial:
        return json.dumps({"error": f"Insufficient actuarial data to run logistics for {target_region}"})

    # --- FIX: Gracefully default BEV volumes to 0 if the region has no electric cars! ---
    bev_volumes = region_bev['cohorts']['0-3_months'] if region_bev else 0

    # 4. Define Regional Recycling Hubs
    recycling_hubs = [
        {"Name": f"Cobat Battery Extraction Center ({target_region})", "Specialty": "Black Mass Recycling"},
        {"Name": f"Enel X 2nd-Life Hub ({target_region})", "Specialty": "Grid Storage Repurposing"},
        {"Name": f"Ecopneus Rubber Granulate Plant", "Specialty": "Asphalt Recycling"},
        {"Name": f"Fonderie Metallurgiche Nord", "Specialty": "Scrap Metal Smelting"}
    ]

    # 5. Construct the Payload
    payload = {
        "Target_Region": target_region,
        "End_Of_Life_Volumes": {
            "Brake_Pads": region_actuarial['brakes'][2], 
            "Tires": region_actuarial['tires'][2],       
            "EV_Batteries": bev_volumes 
        },
        "Available_Recycling_Hubs": recycling_hubs
    }

    return json.dumps(payload, indent=2)


# ── Investigation AI Analysis ─────────────────────────────────────────────

@router.get("/api/ai/investigation/{case_number}")
async def ai_investigation_analysis(case_number: str, lang: str = "en"):
    """Streaming AI fraud & damage analysis for an investigation."""
    from database import get_db
    conn = get_db()

    # Get investigation details
    inv = conn.execute("""SELECT i.*, v.plate_number, cm.model_name, cm.manufacturer
        FROM investigations i
        JOIN vehicles v ON i.vehicle_vin = v.vin
        JOIN car_models cm ON v.model_id = cm.id
        WHERE i.case_number = ?""", (case_number,)).fetchone()

    if not inv:
        conn.close()
        return {"error": "Investigation not found"}

    # Get vehicle telemetry
    tel = conn.execute("SELECT * FROM vehicle_telemetry WHERE vin = ?", (inv["vehicle_vin"],)).fetchone()

    # Get vehicle components
    components = conn.execute("SELECT * FROM components WHERE vehicle_vin = ?", (inv["vehicle_vin"],)).fetchall()

    # Get photos
    photos = conn.execute("SELECT * FROM investigation_photos WHERE case_number = ?", (case_number,)).fetchall()
    conn.close()

    inv_data = dict(inv)
    tel_data = dict(tel) if tel else {}
    comp_data = [dict(c) for c in components]

    # Build comprehensive context for AI
    context = json.dumps({
        "case_number": inv_data["case_number"],
        "vehicle": f"{inv_data['manufacturer']} {inv_data['model_name']}",
        "plate": inv_data["plate_number"],
        "incident_type": inv_data["incident_type"],
        "incident_date": inv_data["incident_date"],
        "incident_location": inv_data["incident_location"],
        "incident_description": inv_data["incident_description"],
        "speed_at_impact_kmh": inv_data["speed_at_impact"],
        "g_force_max": inv_data["g_force_max"],
        "g_force_lateral": inv_data["g_force_lateral"],
        "abs_triggered": bool(inv_data["abs_triggered"]),
        "airbag_deployed": bool(inv_data["airbag_deployed"]),
        "coolant_temp_c": inv_data["coolant_temp"],
        "fraud_risk_score": inv_data["fraud_risk_score"],
        "tpms_snapshot": inv_data.get("tpms_snapshot_json"),
        "telemetry": {
            "driving_score": tel_data.get("driving_score"),
            "odometer_km": tel_data.get("current_odometer_km"),
            "brake_pressure_bar": tel_data.get("brake_pressure_bar"),
            "has_blackbox": bool(tel_data.get("has_blackbox")),
        },
        "components_at_risk": [
            {"category": c["category"], "position": c.get("position"), "wear_percent": c["wear_percent"], "health": c["health_status"]}
            for c in comp_data if c.get("wear_percent", 0) > 50
        ],
        "photos_count": len(photos),
    }, indent=2)

    language = "Italian" if lang == "it" else "English"
    system_prompt = f"""You are the CycleSync AI Insurance Adjuster, an expert anti-fraud and damage assessment AI embedded in a fleet insurance platform.

You perform TWO critical analyses on every investigation:

## SECTION 1: FRAUD ANALYSIS
Analyze the telemetry data, driving patterns, and incident circumstances for fraud indicators. Consider:
- Inconsistencies between reported incident and telemetry data (speed, G-forces, brake data)
- Component wear patterns that suggest negligence or pre-existing damage
- Blackbox data anomalies (if available)
- Driving score history vs incident severity
- TPMS readings at impact vs normal ranges
- Whether ABS/airbag deployment is consistent with reported speed and impact type

Score the fraud risk and explain your reasoning with specific data points.

## SECTION 2: DAMAGE ASSESSMENT & REPAIR ESTIMATE
Based on the incident data, provide:
- Detailed damage assessment for each affected area
- Component replacement recommendations (which parts need replacement vs repair)
- Estimated repair cost breakdown (labor, parts, paint)
- Total estimated repair cost in EUR
- Recommendation: APPROVE, PARTIALLY APPROVE, or DENY the claim

## SECTION 3: VERDICT
Provide your final verdict with:
- Claim recommendation (approve/partial/deny)
- Justification citing specific telemetry values
- Any flags for human adjuster review

Format your response with clear markdown headers, bullet points, and **bold** key values.
RESPOND ENTIRELY IN {language}."""

    def generate():
        if lang == "it":
            yield "### 🔄 Inizializzazione CycleSync Anti-Frode AI...\n"
            yield f"Analisi del caso **{case_number}** — Acquisizione telemetria, dati componenti e foto incidente...\n\n"
        else:
            yield "### 🔄 CycleSync Anti-Fraud AI Initialization...\n"
            yield f"Analyzing case **{case_number}** — Ingesting telemetry, component data, and incident photos...\n\n"

        import time
        time.sleep(0.3)

        for chunk in orchestrator.llm_client.stream_inference(system_prompt, context, f"inv_{case_number}", lang):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── Investigation Photos ──────────────────────────────────────────────────

@router.get("/api/db/investigations/{case_number}/photos")
def get_investigation_photos(case_number: str):
    """List all photos for an investigation."""
    from database import get_db
    conn = get_db()
    photos = conn.execute(
        "SELECT id, case_number, filename, caption, photo_type, uploaded_at FROM investigation_photos WHERE case_number = ? ORDER BY uploaded_at",
        (case_number,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in photos]


@router.post("/api/db/investigations/{case_number}/photos")
async def upload_investigation_photo(case_number: str, request: Request):
    """Upload a photo for an investigation (base64 or multipart)."""
    import base64
    import uuid
    from database import get_db

    content_type = request.headers.get("content-type", "")

    if "multipart" in content_type:
        form = await request.form()
        file = form.get("file")
        caption = form.get("caption", "Uploaded damage photo")
        photo_type = form.get("photo_type", "damage")
        if not file:
            return {"error": "No file provided"}

        ext = file.filename.split(".")[-1] if "." in file.filename else "png"
        filename = f"{case_number}_{uuid.uuid4().hex[:8]}.{ext}"
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "website", "static", "img", "investigations", filename)

        # Try saving to correct path
        img_dir = os.path.join(os.path.dirname(__file__), "..", "static", "img", "investigations")
        os.makedirs(img_dir, exist_ok=True)
        save_path = os.path.join(img_dir, filename)

        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
    else:
        body = await request.json()
        caption = body.get("caption", "Uploaded damage photo")
        photo_type = body.get("photo_type", "damage")
        image_data = body.get("image_data")
        if not image_data:
            return {"error": "No image_data provided"}

        ext = "png"
        filename = f"{case_number}_{uuid.uuid4().hex[:8]}.{ext}"
        img_dir = os.path.join(os.path.dirname(__file__), "..", "static", "img", "investigations")
        os.makedirs(img_dir, exist_ok=True)
        save_path = os.path.join(img_dir, filename)

        # Remove data:image prefix if present
        if "," in image_data:
            image_data = image_data.split(",")[1]
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(image_data))

    conn = get_db()
    conn.execute("INSERT INTO investigation_photos (case_number, filename, caption, photo_type) VALUES (?,?,?,?)",
        (case_number, filename, caption, photo_type))
    conn.commit()
    conn.close()

    return {"success": True, "filename": filename, "caption": caption}


# ── Batch Recycling AI Analysis ───────────────────────────────────────────

@router.get("/api/ai/batch-recycling/{category}")
async def ai_batch_recycling(category: str, lang: str = "en"):
    """
    Streaming AI analysis for batch recycling of all stocked components of a category.
    Category: 'tire', 'brake_pad', 'ev_battery', or 'all'.
    """
    from database import get_db
    conn = get_db()

    # Fetch all stocked components (with vehicle plate)
    if category == "all":
        rows = conn.execute("""
            SELECT c.*, v.plate_number FROM components c
            LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
            WHERE c.status = 'stocked'
            ORDER BY c.category, c.wear_percent DESC
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT c.*, v.plate_number FROM components c
            LEFT JOIN vehicles v ON c.vehicle_vin = v.vin
            WHERE c.status = 'stocked' AND c.category = ?
            ORDER BY c.wear_percent DESC
        """, (category,)).fetchall()
    conn.close()

    components = [dict(r) for r in rows]

    if not components:
        def empty():
            yield "⚠️ No stocked components found for this category."
        return StreamingResponse(empty(), media_type="text/event-stream")

    # Build summary stats
    total_count = len(components)
    total_recovery_value = sum(c.get("recovery_value_eur") or 0 for c in components)
    total_co2_saved = sum(c.get("co2_saved_kg") or 0 for c in components)
    avg_wear = sum(c.get("wear_percent") or 0 for c in components) / total_count if total_count else 0

    # Group by category
    by_category = {}
    for c in components:
        cat = c["category"]
        if cat not in by_category:
            by_category[cat] = {"count": 0, "items": [], "total_value": 0, "total_co2": 0}
        by_category[cat]["count"] += 1
        by_category[cat]["total_value"] += c.get("recovery_value_eur") or 0
        by_category[cat]["total_co2"] += c.get("co2_saved_kg") or 0
        by_category[cat]["items"].append({
            "serial": c["serial_number"],
            "brand": c.get("brand", "Unknown"),
            "model": c.get("model_name", ""),
            "wear_pct": c.get("wear_percent", 0),
            "current_recommendation": c.get("ai_recommendation", "None"),
            "current_value_eur": c.get("recovery_value_eur"),
            "co2_saved_kg": c.get("co2_saved_kg"),
            "facility": c.get("destination_facility"),
            "specs": json.loads(c["specs_json"]) if c.get("specs_json") else {},
            "from_vehicle": c.get("plate_number", "Unknown"),
        })

    payload = json.dumps({
        "batch_summary": {
            "total_components": total_count,
            "categories": {k: v["count"] for k, v in by_category.items()},
            "average_wear_pct": round(avg_wear, 1),
            "current_total_recovery_value_eur": round(total_recovery_value, 2),
            "current_total_co2_saved_kg": round(total_co2_saved, 1),
        },
        "components_by_category": by_category,
    }, indent=2)

    category_label = {"tire": "Tires", "brake_pad": "Brake Pads", "ev_battery": "EV Batteries", "all": "All Categories"}
    cat_name = category_label.get(category, category)
    language = "Italian" if lang == "it" else "English"

    system_prompt = f"""You are the CycleSync Circular Economy AI, an expert in automotive component recycling, second-life allocation, and ESG revenue optimization.

You are analyzing a BATCH of {total_count} stocked components ({cat_name}) for optimal recycling/reuse strategy.

## SECTION 1: BATCH OVERVIEW & CONDITION ASSESSMENT
Analyze the overall condition of the batch based on wear percentages, brands, and specifications.
Group components by condition tier (low wear = resell/reuse, medium = retread/refurbish, high = recycle/extract).

## SECTION 2: OPTIMAL RECYCLING & REUSE STRATEGY
For each condition tier, recommend the best pathway:
- **Resell / Second-Life**: Components with <50% wear → estimate market resale price
- **Retread / Refurbish**: Components with 50-75% wear → estimate refurbishment cost and revenue
- **Recycle / Extract**: Components with >75% wear → estimate material extraction revenue (rubber granulate, scrap metal, black mass, etc.)

## SECTION 3: REVENUE PROJECTION
Provide a detailed revenue breakdown:
- Revenue per pathway (Resale, Refurbishment, Recycling)
- Total projected revenue in EUR
- Compare with current individual recovery estimates (€{round(total_recovery_value, 2)} total)
- Highlight if batch processing increases efficiency / revenue vs individual processing
- Include recycling facility recommendations

## SECTION 4: ENVIRONMENTAL IMPACT
- Total CO₂ saved by processing this batch (current estimate: {round(total_co2_saved, 1)} kg)
- Equivalent environmental metrics (trees planted, km driven offset, etc.)
- ESG reporting summary for sustainability disclosures

## SECTION 5: ACTIONABLE NEXT STEPS
Provide a concrete 3-step action plan with timelines and facility assignments.

Use tables and bold numbers for key metrics. Be specific with EUR amounts.
RESPOND ENTIRELY IN {language}."""

    def generate():
        if lang == "it":
            yield f"### 🔄 CycleSync Circular Economy AI — Analisi Batch\n"
            yield f"Analisi di **{total_count}** componenti ({cat_name}) in stock per strategia ottimale di riciclo/riutilizzo...\n\n"
        else:
            yield f"### 🔄 CycleSync Circular Economy AI — Batch Analysis\n"
            yield f"Analyzing **{total_count}** stocked components ({cat_name}) for optimal recycling/reuse strategy...\n\n"

        import time
        time.sleep(0.3)

        for chunk in orchestrator.llm_client.stream_inference(system_prompt, payload, f"batch_{category}", lang):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── SOS Emergency AI Analysis ─────────────────────────────────────────────

@router.get("/api/ai/sos/{vin}")
async def ai_sos_analysis(vin: str, lang: str = "en"):
    """Streaming SOS analysis — determines intervention type based on vehicle telemetry."""
    from database import get_db
    import json, time
    conn = get_db()
    v = conn.execute("""SELECT v.*, cm.model_name, cm.manufacturer FROM vehicles v
        JOIN car_models cm ON v.model_id=cm.id WHERE v.vin=?""", (vin,)).fetchone()
    t = conn.execute("SELECT * FROM vehicle_telemetry WHERE vin=?", (vin,)).fetchone()
    comps = conn.execute("SELECT category,position,wear_percent,health_status FROM components WHERE vehicle_vin=? AND status='installed'", (vin,)).fetchall()
    conn.close()
    if not v:
        def err(): yield "Vehicle not found."
        return StreamingResponse(err(), media_type="text/event-stream")

    context = json.dumps({
        "vehicle": f"{dict(v).get('manufacturer','')} {dict(v).get('model_name','')}",
        "plate": v["plate_number"], "driver": v["driver_name"],
        "odometer_km": t["current_odometer_km"] if t else 0,
        "driving_score": t["driving_score"] if t else None,
        "has_blackbox": bool(t["has_blackbox"]) if t else False,
        "gps": {"lat": t["gps_lat"], "lon": t["gps_lon"]} if t and t["gps_lat"] else None,
        "last_accel_g": {"x": t["accel_x_g"], "y": t["accel_y_g"], "z": t["accel_z_g"]} if t and t["accel_x_g"] else None,
        "brake_pressure_bar": t["brake_pressure_bar"] if t else None,
        "coolant_temp_c": t["coolant_temp_c"] if t else None,
        "battery_soc": t["battery_soc"] if t else None,
        "dtc_codes": json.loads(t["dtc_codes_json"]) if t and t["dtc_codes_json"] else [],
        "critical_components": [{"cat":c["category"],"pos":c["position"],"wear":c["wear_percent"]} for c in comps if c["wear_percent"] and c["wear_percent"]>75],
        "policy_number": v["policy_number"], "insurer": v["insurer"],
    }, indent=2)

    language = "Italian" if lang == "it" else "English"
    system_prompt = f"""You are the CycleSync Emergency Response AI. A driver has pressed the SOS button.

Analyze the vehicle's current state and determine the appropriate emergency response:

## 1. SITUATION ASSESSMENT
Evaluate severity based on telemetry (G-forces, brake pressure, speed, component health).
Classify as: MINOR (roadside assist), MODERATE (tow truck needed), or SEVERE (emergency services).

## 2. INTERVENTION DISPATCH
Based on severity:
- MINOR: 🔧 Roadside assistance — flat tire, minor mechanical, DTC codes
- MODERATE: 🚗 Tow truck + mechanic — immobilized vehicle, critical component failure  
- SEVERE: 🚑 Ambulance + 🚔 Police + 🚗 Tow — suspected crash, airbag indicators, extreme G-forces

## 3. INSURANCE NOTIFICATION
Compose the alert sent to the insurer with: policy number, location, severity, estimated cost.

## 4. DRIVER INSTRUCTIONS
Clear, calm instructions for the driver while help is en route.

Use emoji for visual urgency. Be decisive and specific.
RESPOND ENTIRELY IN {language}."""

    def generate():
        if lang == "it":
            yield "### 🆘 CycleSync Emergency AI — Attivato\\n"
            yield f"Analisi veicolo **{v['plate_number']}** in corso...\\n\\n"
        else:
            yield "### 🆘 CycleSync Emergency AI — Activated\\n"
            yield f"Analyzing vehicle **{v['plate_number']}**...\\n\\n"
        time.sleep(0.3)
        for chunk in orchestrator.llm_client.stream_inference(system_prompt, context, f"sos_{vin}", lang):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")
