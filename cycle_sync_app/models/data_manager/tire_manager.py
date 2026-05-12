import sqlite3
from models.data_manager.database_manager import DatabaseManager

class TireManager:
    @staticmethod
    def inject_dummy_tires():
        """Creates the Tire Blueprints and mounts an initial set to Mario's car."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # --- THE FIX: Check if the catalog is already seeded! ---
        cursor.execute("SELECT COUNT(*) FROM tire_blueprints")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return # Exit silently, the tires are already in the DB!
        # --------------------------------------------------------
        
        try:
            # 1. The Blueprint Catalog (Tire OEM SSOT)
            catalogs = [
                ('Michelin', 'Pilot Sport 4S', 30000, 8.0),
                ('Michelin', 'Primacy 4', 45000, 8.0),
                ('Pirelli', 'P Zero', 25000, 7.5),
                ('Pirelli', 'Cinturato P7', 40000, 8.0),
                ('Goodyear', 'Eagle F1 Asymmetric 5', 30000, 8.0),
                ('Goodyear', 'EfficientGrip Performance', 45000, 8.5)
            ]
            
            for brand, model, life, tread in catalogs:
                cursor.execute('''
                    INSERT INTO tire_blueprints (brand, model_name, expected_lifespan_km, starting_tread_depth_mm)
                    VALUES (?, ?, ?, ?)
                ''', (brand, model, life, tread))
            
            # Grab the ID for the Michelin Pilot Sport 4S
            cursor.execute("SELECT id FROM tire_blueprints WHERE model_name = 'Pilot Sport 4S'")
            blueprint_id = cursor.fetchone()[0]
            
            # 2. The Mounting Event for Mario
            positions = ['FL', 'FR', 'RL', 'RR']
            for pos in positions:
                cursor.execute('''
                    INSERT INTO mounted_tires (vin, blueprint_id, position, mounting_odometer_km, current_tread_depth_mm)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('WBA00000000000001', blueprint_id, pos, 10000, 6.5))
                
            conn.commit()
            print("[TireManager] Tire Catalog created and initial set mounted.")
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()