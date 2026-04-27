import sqlite3
import random
from models.data_manager.database_manager import DatabaseManager

class TripSimulator:

    @classmethod
    def _ensure_telemetry_columns(cls):
        """Safely injects the new GNSS/IMU telemetry columns for the Eco Coach."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE vehicle_telemetry ADD COLUMN avg_speed_kmh REAL DEFAULT 60.0")
            cursor.execute("ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_avg INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_heavy INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE vehicle_telemetry ADD COLUMN harsh_events_extreme INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE vehicle_telemetry ADD COLUMN green_speed_pct REAL DEFAULT 80.0")
            conn.commit()
        except sqlite3.OperationalError:
            pass # Columns already exist
        finally:
            conn.close()

    @classmethod
    def simulate_trip(cls, vin: str):
        # 1. Ensure DB is ready
        cls._ensure_telemetry_columns()
        
        # 2. Simulate Trip Core Metrics
        trip_distance = random.randint(12, 85)
        
        # Hidden Aggression Index (0.0 = Grandma, 1.0 = Racecar Driver)
        aggression_index = random.random()
        
        # 3. Simulate GNSS Average Speed & "Green Speed" adherence
        # A calm driver stays near 60 km/h. Aggressive goes faster or stops/starts wildly.
        avg_speed = 60 + (aggression_index * random.uniform(10, 50)) * random.choice([1, -1])
        
        # Green Speed (50-75 km/h as defined by Strada et al.)
        if 50 <= avg_speed <= 75:
            green_pct = random.uniform(70.0, 95.0)
        else:
            green_pct = max(10.0, 90.0 - (abs(avg_speed - 60) * 1.5))
            
        # 4. Simulate IMU Harsh Events (Accelerations > |0.3|g)
        # Using a Poisson-like scaling based on aggression and distance
        event_multiplier = aggression_index * (trip_distance / 10.0)
        h_avg = int(random.uniform(0, 3) * event_multiplier)     # 0.3g - 0.5g
        h_hvy = int(random.uniform(0, 1.5) * event_multiplier)   # 0.5g - 0.8g
        h_ext = int(random.uniform(0, 0.5) * event_multiplier)   # 0.8g - 1.0g

        # 5. Calculate the Strada et al. "DS" (Driving Style) Penalty
        # Weights: Average=0.1, Heavy=0.3, Very Heavy/Extreme=0.8
        weighted_events = (h_avg * 0.1) + (h_hvy * 0.3) + (h_ext * 0.8)
        HR = min(weighted_events / trip_distance, 1.0) # Harsh Ratio
        
        # DS ranges from 1.0 (perfect) to 1.30 (30% penalty)
        DS_penalty = 1.0 + (HR * 0.30)
        
        # Map the DS penalty to our 0-100 Driving Score scale
        # 1.0 DS = 100 Score. 1.3 DS = 40 Score.
        trip_score = max(0, min(100, 100 - ((DS_penalty - 1.0) / 0.30) * 60))

        # 6. Database Operations
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT current_odometer_km, driving_score FROM vehicle_telemetry WHERE vin = ?", (vin,))
        row = cursor.fetchone()
        
        if row:
            current_odometer_km, old_score = row
            new_odometer = current_odometer_km + trip_distance
            
            # Smooth the score using an Exponential Moving Average (80% old history, 20% this trip)
            new_score = (old_score * 0.8) + (trip_score * 0.2)
            
            cursor.execute("""
                UPDATE vehicle_telemetry 
                SET current_odometer_km = ?, 
                    driving_score = ?, 
                    avg_speed_kmh = ?, 
                    harsh_events_avg = ?, 
                    harsh_events_heavy = ?, 
                    harsh_events_extreme = ?, 
                    green_speed_pct = ?,
                    last_sync_timestamp = CURRENT_TIMESTAMP
                WHERE vin = ?
            """, (new_odometer, new_score, avg_speed, h_avg, h_hvy, h_ext, green_pct, vin))
        else:
            new_odometer = random.randint(500, 1500) + trip_distance
            
            cursor.execute("""
                INSERT INTO vehicle_telemetry 
                (vin, current_odometer_km, driving_score, avg_speed_kmh, harsh_events_avg, harsh_events_heavy, harsh_events_extreme, green_speed_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (vin, new_odometer, trip_score, avg_speed, h_avg, h_hvy, h_ext, green_pct))
            
        conn.commit()
        conn.close()