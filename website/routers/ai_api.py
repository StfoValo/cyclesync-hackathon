from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from cache_manager import get_cache
from mcp_agent_server.ai_orchestrator import AIOrchestrator
import json

router = APIRouter()
orchestrator = AIOrchestrator()

@router.get("/api/ai/orchestrate/{region}")
async def orchestrate_ai(request: Request, region: str): # <-- Inject request
    client_ip = request.client.host
    print(f"🧠 USER {client_ip} triggered AI Strategy for region: {region}")
    # Fetch portfolio to feed into prompt
    portfolio = get_cache('asset_risk_portfolio')
    region_data = next((r for r in portfolio.get("regional", []) if r["region"] == region), None)
    
    payload = json.dumps(region_data) if region_data else f'{{"region": "{region}", "status": "no data"}}'
    
    def generate():
        for chunk in orchestrator.run_actuarial_strategy_analysis(payload):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/api/ai/circular-logistics/{region}")
async def orchestrate_circular_logistics(region: str):
    payload = build_reverse_logistics_payload(region)
    
    def generate():
        for chunk in orchestrator.run_circular_logistics_analysis(payload):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")

def build_reverse_logistics_payload(target_region: str) -> str:
    """
    Merges data from ActuarialModel (Brakes/Tires) and FleetModel (Batteries) 
    to create a hyper-local ESG routing payload for the AI.
    """
    # 1. Fetch Actuarial Risk Portfolio (Tires & Brakes)
    portfolio = get_cache('asset_risk_portfolio')
    region_actuarial = next((r for r in portfolio.get("regional", []) if r["region"] == target_region), None)

    # 2. Fetch BEV Telemetry (Batteries 0-3 months from End-of-Life)
    bev_analytics = get_cache('bev_regional_analytics')
    region_bev = next((r for r in bev_analytics if r["region_name"] == target_region), None)

    # 3. Handle missing data gracefully
    if not region_actuarial or not region_bev:
        return json.dumps({"error": f"Insufficient data to run logistics for {target_region}"})

    # 4. Define Regional Recycling Hubs (Mock supply chain data to ground the LLM)
    # In a real app, this would be a database query: SELECT * FROM recycling_partners WHERE region = target_region
    recycling_hubs = [
        {"Name": f"Cobat Battery Extraction Center ({target_region})", "Specialty": "Black Mass Recycling"},
        {"Name": f"Enel X 2nd-Life Hub ({target_region})", "Specialty": "Grid Storage Repurposing"},
        {"Name": f"Ecopneus Rubber Granulate Plant", "Specialty": "Asphalt Recycling"},
        {"Name": f"Fonderie Metallurgiche Nord", "Specialty": "Scrap Metal Smelting"}
    ]

    # 5. Construct the highly optimized JSON Payload
    payload = {
        "Target_Region": target_region,
        "End_Of_Life_Volumes": {
            # Brakes < 3mm (Critical Need Replacement)
            "Brake_Pads": region_actuarial['brakes'][2], 
            # Tires < 2mm (Critical Blowout Risk)
            "Tires": region_actuarial['tires'][2],       
            # Batteries failing in the next 0-3 months
            "EV_Batteries": region_bev['cohorts']['0-3_months'] 
        },
        "Available_Recycling_Hubs": recycling_hubs
    }

    return json.dumps(payload, indent=2)