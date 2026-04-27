from models.data_manager.database_manager import DatabaseManager

class MacroMarketModel:
    def __init__(self):
        pass

    def get_market_overview(self):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # We now calculate this dynamically from tracked vehicles and blueprints
        cursor.execute("""
            SELECT c.powertrain, c.model_name, COUNT(v.vin) 
            FROM vehicles v
            JOIN car_models c ON v.model_id = c.id
            GROUP BY c.powertrain, c.model_name
        """)
        vehicle_stats = cursor.fetchall()
        conn.close()
        
        market_data = []
        rubber_tons = 0.0
        lithium_tons = 0.0
        aluminum_tons = 0.0
        
        for p_train, m_name, count in vehicle_stats:
            # Assuming ~2 tons of aluminum per vehicle
            aluminum_tons += count * 2.0
            # Assuming ~0.05 tons of rubber (4 tires) per vehicle
            rubber_tons += count * 0.05
            if p_train == 'BEV':
                # Assuming ~0.5 tons of lithium/battery materials per BEV
                lithium_tons += count * 0.5
                
        if rubber_tons > 0:
            market_data.append({
                "id": 1,
                "material_sector": "Rubber",
                "component_name": "End-of-Life Tires",
                "origin_oem": "Global Aggregate",
                "quantity_tons": round(rubber_tons, 2),
                "estimated_salvage_value_eur": round(rubber_tons * 250, 2),
                "status": "Available for Bidding"
            })
            
        if lithium_tons > 0:
            market_data.append({
                "id": 2,
                "material_sector": "Lithium",
                "component_name": "Degraded EV Batteries",
                "origin_oem": "Motor Valley Aggregate",
                "quantity_tons": round(lithium_tons, 2),
                "estimated_salvage_value_eur": round(lithium_tons * 7000, 2),
                "status": "Processing"
            })
            
        if aluminum_tons > 0:
            market_data.append({
                "id": 3,
                "material_sector": "Aluminum",
                "component_name": "Chassis Scraps",
                "origin_oem": "Global Aggregate",
                "quantity_tons": round(aluminum_tons, 2),
                "estimated_salvage_value_eur": round(aluminum_tons * 500, 2),
                "status": "Available for Bidding"
            })
            
        return market_data
