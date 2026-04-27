import sqlite3
import random
from models.data_manager.database_manager import DatabaseManager

class TripSimulator:
    @staticmethod
    def simulate_trip(vin: str):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT current_odometer_km, driving_score FROM vehicle_telemetry WHERE vin = ?", (vin,))
        row = cursor.fetchone()
        
        if row:
            current_odometer_km, driving_score = row
            new_odometer = current_odometer_km + random.randint(12, 85)
            new_score = driving_score + random.randint(-4, 4)
            # Ensure score stays bounded between 0 and 100
            new_score = max(0, min(100, new_score))
            
            cursor.execute("""
                UPDATE vehicle_telemetry 
                SET current_odometer_km = ?, driving_score = ?, last_sync_timestamp = CURRENT_TIMESTAMP
                WHERE vin = ?
            """, (new_odometer, new_score, vin))
        else:
            new_odometer = random.randint(500, 1500)
            new_score = random.randint(70, 95)
            
            cursor.execute("""
                INSERT INTO vehicle_telemetry (vin, current_odometer_km, driving_score)
                VALUES (?, ?, ?)
            """, (vin, new_odometer, new_score))
            
        conn.commit()
        conn.close()
