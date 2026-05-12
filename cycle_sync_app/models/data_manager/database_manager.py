import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cyclesync.db')

class DatabaseManager:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def initialize_database():
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, role TEXT NOT NULL)''')

        # --- UPGRADED CAR BLUEPRINT ---
        cursor.execute('''CREATE TABLE IF NOT EXISTS car_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT, model_name TEXT NOT NULL UNIQUE,
            base_price REAL, manufacture_cost REAL, car_type TEXT, 
            powertrain TEXT, drivetrain TEXT, -- NEW COLUMNS
            owner_account_id INTEGER, image_path TEXT,
            FOREIGN KEY (owner_account_id) REFERENCES accounts(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            vin TEXT PRIMARY KEY, model_id INTEGER, owner_id TEXT,
            production_date DATE, region_name TEXT, lat REAL, lon REAL,
            FOREIGN KEY (model_id) REFERENCES car_models(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS vehicle_telemetry (
            vin TEXT PRIMARY KEY, current_odometer_km INTEGER DEFAULT 0,
            driving_score INTEGER DEFAULT 100, last_sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vin) REFERENCES vehicles(vin))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS tire_blueprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT, model_name TEXT, 
            expected_lifespan_km INTEGER, starting_tread_depth_mm REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS mounted_tires (
            id INTEGER PRIMARY KEY AUTOINCREMENT, vin TEXT, blueprint_id INTEGER, position TEXT, 
            mounting_odometer_km INTEGER, current_tread_depth_mm REAL,
            FOREIGN KEY (vin) REFERENCES vehicles(vin), FOREIGN KEY (blueprint_id) REFERENCES tire_blueprints(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS global_salvage_pool (
            id INTEGER PRIMARY KEY, material_sector TEXT, component_name TEXT, 
            origin_oem TEXT, quantity_tons REAL, estimated_salvage_value_eur REAL, status TEXT)''')

        conn.commit()
        DatabaseManager.inject_core_dummy_data(conn)
        DatabaseManager.inject_macro_market_data(conn)
        conn.close()

    @staticmethod
    def inject_core_dummy_data(conn):
        cursor = conn.cursor()
        
        dummy_accounts = [('mario_driver', 'hash', 'DRIVER'), ('maserati_oem', 'hash', 'OEM'), ('eco_recycler', 'hash', 'RECYCLER')]
        for user, pwd, role in dummy_accounts:
            try:
                cursor.execute('INSERT INTO accounts (username, password_hash, role) VALUES (?, ?, ?)', (user, pwd, role))
            except sqlite3.IntegrityError:
                pass
        conn.commit()

    @staticmethod
    def inject_macro_market_data(conn):
        # We now calculate this dynamically via MacroMarketModel, no static injection needed.
        pass