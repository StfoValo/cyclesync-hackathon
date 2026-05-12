"""
CycleSync Unified Database Layer
Connects to cyclesync.db — single source of truth for the entire app.
"""
import os
from seed_data import seed_demo_data
import sqlite3
import json
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cycle_sync_app", "models", "cyclesync.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

# ── Schema Migration ─────────────────────────────────────────────────────
MIGRATIONS = [
    # Base vehicle columns missing from original schema
    "ALTER TABLE vehicles ADD COLUMN plate_number TEXT",
    "ALTER TABLE vehicles ADD COLUMN driver_age INTEGER",
    "ALTER TABLE vehicles ADD COLUMN driver_gender TEXT",
    "ALTER TABLE vehicles ADD COLUMN vehicle_category TEXT",
    # Extend vehicles
    "ALTER TABLE vehicles ADD COLUMN color TEXT",
    "ALTER TABLE vehicles ADD COLUMN weight_kg REAL",
    "ALTER TABLE vehicles ADD COLUMN power_hp INTEGER",
    "ALTER TABLE vehicles ADD COLUMN displacement_cc INTEGER",
    "ALTER TABLE vehicles ADD COLUMN registration_date DATE",
    "ALTER TABLE vehicles ADD COLUMN status TEXT DEFAULT 'active'",
    "ALTER TABLE vehicles ADD COLUMN body_type TEXT",
    "ALTER TABLE vehicles ADD COLUMN country TEXT DEFAULT 'IT'",
    "ALTER TABLE vehicles ADD COLUMN city TEXT",
    "ALTER TABLE vehicles ADD COLUMN driver_name TEXT",
    "ALTER TABLE vehicles ADD COLUMN policy_number TEXT",
    "ALTER TABLE vehicles ADD COLUMN policy_type TEXT",
    "ALTER TABLE vehicles ADD COLUMN insurer TEXT",
    "ALTER TABLE vehicles ADD COLUMN premium_eur REAL",
    "ALTER TABLE vehicles ADD COLUMN policy_start DATE",
    "ALTER TABLE vehicles ADD COLUMN policy_expiry DATE",
    "ALTER TABLE vehicles ADD COLUMN policy_status TEXT DEFAULT 'active'",
    "ALTER TABLE vehicles ADD COLUMN telematics_discount REAL DEFAULT 0",
    "ALTER TABLE vehicles ADD COLUMN claims_count INTEGER DEFAULT 0",
    # Extend car_models
    "ALTER TABLE car_models ADD COLUMN manufacturer TEXT",
    "ALTER TABLE car_models ADD COLUMN displacement_cc INTEGER",
    "ALTER TABLE car_models ADD COLUMN power_hp INTEGER",
    "ALTER TABLE car_models ADD COLUMN weight_kg REAL",
    # Extend vehicle_telemetry — basic metrics
    "ALTER TABLE vehicle_telemetry ADD COLUMN avg_speed_kmh REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_avg INTEGER DEFAULT 0",
    "ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_heavy INTEGER DEFAULT 0",
    "ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_extreme INTEGER DEFAULT 0",
    "ALTER TABLE vehicle_telemetry ADD COLUMN green_speed_pct REAL",
    # Extend vehicle_telemetry — ECU sensors
    "ALTER TABLE vehicle_telemetry ADD COLUMN tpms_fl REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN tpms_fr REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN tpms_rl REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN tpms_rr REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN coolant_temp_c REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN coolant_pressure_bar REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN battery_soc REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN battery_soh REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN oil_temp_c REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN oil_pressure_bar REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN fuel_level_pct REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN engine_rpm REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN throttle_position_pct REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN brake_pressure_bar REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN steering_angle_deg REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN transmission_temp_c REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN dtc_codes_json TEXT",
    # Blackbox sensors
    "ALTER TABLE vehicle_telemetry ADD COLUMN gps_lat REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gps_lon REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gps_altitude_m REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gps_heading_deg REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN accel_x_g REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN accel_y_g REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN accel_z_g REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gyro_roll_deg REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gyro_pitch_deg REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN gyro_yaw_deg REAL",
    "ALTER TABLE vehicle_telemetry ADD COLUMN blackbox_event_type TEXT",
    "ALTER TABLE vehicle_telemetry ADD COLUMN has_blackbox INTEGER DEFAULT 1",
]

NEW_TABLES = [
    """CREATE TABLE IF NOT EXISTS components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT UNIQUE NOT NULL,
        vehicle_vin TEXT,
        category TEXT NOT NULL,
        position TEXT,
        brand TEXT,
        model_name TEXT,
        specs_json TEXT,
        wear_percent REAL,
        health_status TEXT,
        installed_date DATE,
        installed_km REAL,
        status TEXT DEFAULT 'installed',
        removed_date DATE,
        removed_km REAL,
        removal_reason TEXT,
        ai_recommendation TEXT,
        ai_reasoning TEXT,
        recovery_value_eur REAL,
        co2_saved_kg REAL,
        destination_facility TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
    )""",
    """CREATE TABLE IF NOT EXISTS investigations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_number TEXT UNIQUE NOT NULL,
        vehicle_vin TEXT NOT NULL,
        incident_date DATETIME,
        incident_type TEXT,
        incident_location TEXT,
        incident_lat REAL,
        incident_lng REAL,
        incident_description TEXT,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'medium',
        fraud_risk_score REAL,
        speed_at_impact REAL,
        g_force_max REAL,
        g_force_lateral REAL,
        abs_triggered INTEGER,
        airbag_deployed INTEGER,
        tpms_snapshot_json TEXT,
        coolant_temp REAL,
        coolant_pressure REAL,
        ai_damage_assessment_json TEXT,
        ai_repair_estimate_eur REAL,
        ai_fraud_analysis TEXT,
        ai_verdict TEXT,
        photos_json TEXT,
        reconstruction_video TEXT,
        assigned_adjuster TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
    )""",
    """CREATE TABLE IF NOT EXISTS maintenance_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_vin TEXT NOT NULL,
        event_date DATE,
        event_type TEXT,
        description TEXT,
        mileage_km REAL,
        cost_eur REAL,
        facility TEXT,
        severity TEXT,
        FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
    )""",
    """CREATE TABLE IF NOT EXISTS investigation_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_number TEXT NOT NULL,
        filename TEXT NOT NULL,
        caption TEXT,
        photo_type TEXT DEFAULT 'damage',
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_number) REFERENCES investigations(case_number)
    )""",
    """CREATE TABLE IF NOT EXISTS driver_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        phone TEXT,
        pinned_vin TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS driver_vehicles (
        driver_id INTEGER NOT NULL,
        vin TEXT NOT NULL,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (driver_id, vin),
        FOREIGN KEY (driver_id) REFERENCES driver_accounts(id),
        FOREIGN KEY (vin) REFERENCES vehicles(vin)
    )""",
]


def init_db():
    """Run migrations and seed data on app startup."""
    # Ensure base schema exists first
    from models.data_manager.database_manager import DatabaseManager
    DatabaseManager.initialize_database()

    conn = get_db()
    # Run column migrations (ignore 'duplicate column' errors)
    for sql in MIGRATIONS:
        try:
            conn.execute(sql)
        except sqlite3.OperationalError:
            pass  # Column already exists
    # Create new tables
    for sql in NEW_TABLES:
        conn.execute(sql)
    conn.commit()
    # Seed demo data if needed
    count = conn.execute("SELECT COUNT(*) FROM vehicles WHERE policy_number IS NOT NULL").fetchone()[0]
    if count < 5:
        seed_demo_data(conn)
    conn.close()
    print("✅ CycleSync Database initialized.")
