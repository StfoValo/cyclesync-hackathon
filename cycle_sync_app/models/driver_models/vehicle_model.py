import sqlite3
from models.data_manager.database_manager import DatabaseManager

class VehicleModel:
    def __init__(self):
        pass

    def get_vehicles_by_owner(self, owner_id: str):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        # We now pull the powertrain, drivetrain, and price too!
        cursor.execute('''
            SELECT v.vin, c.model_name, c.car_type, c.image_path, 
                   t.current_odometer_km, t.driving_score,
                   c.powertrain, c.drivetrain, c.base_price
            FROM vehicles v
            JOIN car_models c ON v.model_id = c.id
            LEFT JOIN vehicle_telemetry t ON v.vin = t.vin
            WHERE v.owner_id = ?
        ''', (owner_id,))
        results = cursor.fetchall()
        conn.close()
        return results