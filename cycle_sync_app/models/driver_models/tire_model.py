import sqlite3
import math
from models.data_manager.database_manager import DatabaseManager

class TireModel:
    def get_tires_for_vehicle(self, vin: str):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT m.position, m.mounting_odometer_km, m.current_tread_depth_mm,
                   b.brand, b.model_name, b.expected_lifespan_km, b.starting_tread_depth_mm
            FROM mounted_tires m
            JOIN tire_blueprints b ON m.blueprint_id = b.id
            WHERE m.vin = ?
        """
        cursor.execute(query, (vin,))
        tire_results = cursor.fetchall()

        cursor.execute("SELECT current_odometer_km FROM vehicle_telemetry WHERE vin = ?", (vin,))
        telemetry = cursor.fetchone()
        current_odo = telemetry[0] if telemetry else 0

        conn.close()
        return tire_results, current_odo

    def get_all_tire_blueprints(self):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(id), brand, model_name FROM tire_blueprints GROUP BY brand, model_name ORDER BY brand, model_name")
        results = cursor.fetchall()
        conn.close()
        return results

    def mount_new_tires(self, vin: str, blueprint_id: int, current_odometer: int):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mounted_tires 
            SET blueprint_id = ?, mounting_odometer_km = ?
            WHERE vin = ?
        """, (blueprint_id, current_odometer, vin))
        
        conn.commit()
        conn.close()

    def initialize_vehicle_tires(self, vin: str):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # Check if we have at least one blueprint
        cursor.execute("SELECT id FROM tire_blueprints LIMIT 1")
        bp = cursor.fetchone()
        if not bp:
            cursor.execute("INSERT INTO tire_blueprints (brand, model_name, expected_lifespan_km, starting_tread_depth_mm) VALUES ('Pirelli', 'P Zero Sport', 35000, 8.0)")
            bp_id = cursor.lastrowid
        else:
            bp_id = bp[0]
            
        tires = []
        for pos in ['FL', 'FR', 'RL', 'RR']:
            tires.append((vin, bp_id, pos, 0, 8.0))
        cursor.executemany("INSERT INTO mounted_tires (vin, blueprint_id, position, mounting_odometer_km, current_tread_depth_mm) VALUES (?, ?, ?, ?, ?)", tires)
        conn.commit()
        conn.close()

    def wearModel(self, x_arr, tN, tL, alp):
        tRange = tN - tL
        t = []
        for x in x_arr:
            xi = min(max(x, 0.0), 1.0)
            if xi <= 0.08:
                ti = tN - tRange * 0.12 * (xi / 0.08)**0.55
            elif xi <= 0.82:
                p1end = tN - tRange * 0.12
                frac = (xi - 0.08) / (0.82 - 0.08)
                ti = p1end - (p1end - (tL + tRange * 0.15)) * (frac**alp)
            else:
                p2end = tL + tRange * 0.15
                frac = (xi - 0.82) / (1.0 - 0.82)
                decay = (math.exp(2.8 * frac) - 1.0) / (math.exp(2.8) - 1.0)
                ti = p2end - (p2end - tL) * min(decay, 1.0)
            t.append(ti)
        return t

    def estimate_tire_life(self, p: dict):
        width = float(p.get('width', 205))
        aspect = float(p.get('aspect', 55))
        rim = float(p.get('rim', 17))
        brand = p.get('brand', 'Premium')
        compound = p.get('compound', 'Medium')
        km = float(p.get('km', 35000))
        age = float(p.get('age', 3))
        is_new = p.get('is_new', True)
        tread0inp = float(p.get('tread0inp', 8.0))
        powertrain = p.get('powertrain', 'Combustione (ICE)')
        mass = float(p.get('mass', 1400))
        drive = p.get('drive', 'FWD')
        style = p.get('style', 'Medio')
        usage = p.get('usage', 'Misto')
        temp = float(p.get('temp', 15))
        pressure = float(p.get('pressure', 2.3))
        annKm = float(p.get('annKm', 15000))

        sectionH = width * aspect / 100.0
        contactCoef = (width / 205.0) * (aspect / 55.0)

        compoundLife = {'Soft': 38000, 'Medium': 58000, 'Hard': 78000, 'Winter': 48000, 'All Season': 63000}
        baseLife = compoundLife.get(compound, 58000)

        alphaMap = {'Soft': 0.78, 'Medium': 0.82, 'Hard': 0.86, 'Winter': 0.80, 'All Season': 0.83}
        alpha_base = alphaMap.get(compound, 0.82)
        alpha = max(alpha_base - 0.02 * max(temp - 25.0, 0.0) / 10.0, 0.72)

        kBrand = 1.18 if 'Premium' in brand else (1.08 if 'Sport' in brand else 0.88)
        kStyle = {'Conservativo': 1.15, 'Medio': 1.00, 'Aggressivo': 0.72}.get(style, 1.00)
        kUsage = {'Autostrada': 1.12, 'Città': 0.86, 'Misto': 1.00, 'Montagna': 0.80, 'Circuito': 0.58}.get(usage, 1.00)

        kTemp = max(1.0 - 0.003 * abs(temp - 15.0), 0.70)
        kPres = max(1.0 - 0.09 * abs(pressure - 2.3) / 2.3, 0.78)
        kMass = min(max(1400.0 / mass, 0.74), 1.22)
        kAge = max(1.0 - max(0.0, age - 3.0) * 0.04, 0.58)
        kContact = min(max(1.0 / max(contactCoef, 0.5), 0.85), 1.15)
        kDrive = {'FWD': 0.91, 'RWD': 0.94, 'AWD': 1.00}.get(drive, 0.91)

        kMismatch = 1.0
        if compound == 'Winter' and temp > 10: kMismatch = 0.76
        if compound == 'Soft' and temp < 5: kMismatch = 0.83

        kPT = 0.84 if 'Elettrico' in powertrain else (0.92 if 'Ibrido' in powertrain else 1.00)
        treadAtStart = 8.0 if is_new else tread0inp
        kSH = 1.00 if is_new else 0.88

        effectiveLife = baseLife * kBrand * kStyle * kUsage * kTemp * kPres * kMass * kDrive * kContact * kMismatch * kAge * kPT * kSH
        residualKm = max(effectiveLife - km, 0.0)
        residualPct = (residualKm / effectiveLife) * 100.0 if effectiveLife > 0 else 0.0

        tNew = treadAtStart
        tLegal = 1.6
        xCurr = km / effectiveLife if effectiveLife > 0 else 1.0
        treadCurr = self.wearModel([xCurr], tNew, tLegal, alpha)[0]

        sPct = residualPct
        sTread = min((treadCurr - tLegal) / (tNew - tLegal) * 100.0, 100.0) if tNew > tLegal else 0.0
        sAge = max(100.0 - age * 8.0, 0.0)
        sPress = max(100.0 - abs(pressure - 2.3) * 80.0, 0.0)
        safetyIdx = min(max(0.40 * sPct + 0.30 * sTread + 0.20 * sAge + 0.10 * sPress, 0.0), 100.0)

        if drive == 'FWD':
            wF, wR = 1.28, 0.82
        elif drive == 'RWD':
            wF, wR = 0.88, 1.22
        else:
            wF, wR = 1.06, 1.00
        
        if 'Elettrico' in powertrain:
            wR *= 0.92
        
        wearRange = treadCurr - tLegal
        tFront = max(treadCurr - wearRange * (wF - 1.0) * 0.5, tLegal)
        tRear = max(treadCurr - wearRange * (wR - 1.0) * 0.5, tLegal)
        tFront = min(tFront, tNew)
        tRear = min(tRear, tNew)

        rFront = max((tFront - tLegal) / (tNew - tLegal) * 100.0, 0.0)
        rRear = max((tRear - tLegal) / (tNew - tLegal) * 100.0, 0.0)

        co2New = 27.0
        co2Saved = co2New * (residualPct / 100.0)

        C1 = residualPct
        C2 = max(100.0 - age * 7.0 - (1.0 - kSH) * 40.0 - (1.0 - min(kUsage, 1.0)) * 20.0, 0.0)
        C3 = (co2Saved / co2New) * 100.0
        c4_brand = 100.0 if 'Premium' in brand else (65.0 if 'Sport' in brand else 30.0)
        c4_comp = {'Soft': 30.0, 'Medium': 65.0, 'Hard': 90.0, 'Winter': 50.0, 'All Season': 70.0}.get(compound, 65.0)
        C4 = min(max(0.5 * c4_brand + 0.5 * c4_comp - max(0.0, (age - 4.0) * 8.0), 0.0), 100.0)
        circScore = min(max(0.40 * C1 + 0.25 * C2 + 0.20 * C3 + 0.15 * C4, 0.0), 100.0)

        newPrice = float(p.get('newPrice', 250))
        resaleValue = max(0.0, newPrice * (circScore / 100.0) * 0.15)

        return {
            'effective_life_km': effectiveLife,
            'residual_pct': residualPct,
            'safety_index': safetyIdx,
            'circularity_score': circScore,
            'resale_value_eur': resaleValue,
            't_front': tFront,
            't_rear': tRear,
            'r_front': rFront,
            'r_rear': rRear
        }