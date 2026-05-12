"""Demo vehicle fleet seed data — 18 vehicles across all categories."""
import json, random
from datetime import datetime, timedelta

DEMO_VEHICLES = [
    # (vin, plate, model_name, manufacturer, year, color, powertrain, drivetrain, body_type, displacement_cc, power_hp, weight_kg, region, city, driver_name, policy_number, policy_type, insurer, premium, policy_start, policy_expiry, policy_status, telematics_discount, claims_count, has_blackbox, driving_score, odometer)
    ("WAUZZZ8V9NA123456","AB 123 CD","A4 Avant","Audi",2021,"Glacier White","diesel","AWD","wagon",1968,190,1685,"Lazio","Roma","Marco Rossi","POL-2023-00142","CASKO","UnipolSai",1420,"2023-03-15","2025-03-14","active",-8.5,1,1,42,47820),
    ("YV1XZ91234567890A","EF 456 GH","XC40 Recharge","Volvo",2022,"Fjord Blue","plug_in_hybrid","FWD","SUV",1477,211,1890,"Lombardia","Milano","Giulia Bianchi","POL-2023-00287","CASKO","Generali",1180,"2023-06-20","2025-06-19","active",-14.2,0,1,85,31200),
    ("5YJYGDEE3NF345678","XY 789 ZZ","Model Y Long Range","Tesla",2023,"Midnight Cherry Red","electric","AWD","SUV",0,346,1979,"Piemonte","Torino","Luca Romano","POL-2023-00391","RCA","Allianz",890,"2023-01-10","2025-01-09","active",-3.1,2,1,12,62400),
    ("ZFAEN4000P0012345","RM 001 AA","500e","Fiat",2024,"Glacier Blue","electric","FWD","hatchback",0,118,1365,"Lazio","Roma","Sofia Conti","POL-2024-00055","CASKO","UnipolSai",720,"2024-02-14","2026-02-13","active",-18.5,0,1,91,8400),
    ("WBAXH5C55DDW12345","MI 222 BB","X3 xDrive30e","BMW",2020,"Phytonic Blue","plug_in_hybrid","AWD","SUV",1998,292,2065,"Lombardia","Milano","Andrea Moretti","POL-2022-00198","CASKO","Zurich",1650,"2022-09-05","2025-09-04","active",-6.2,1,1,67,78600),
    ("ZAR94000007654321","NA 333 CC","Giulia 2.2 Turbodiesel","Alfa Romeo",2019,"Rosso Competizione","diesel","RWD","sedan",2143,190,1524,"Campania","Napoli","Francesco Esposito","POL-2021-00412","RCA","Sara",1320,"2021-11-20","2025-11-19","active",-4.8,3,1,55,112000),
    ("WVWZZZ3CZWE123456","TO 444 DD","ID.4 Pro","Volkswagen",2023,"Moonstone Grey","electric","RWD","SUV",0,204,2124,"Piemonte","Torino","Elena Ricci","POL-2023-00510","CASKO","Generali",980,"2023-04-01","2025-03-31","expired",-12.0,0,1,78,42100),
    ("WMEEJ9AA1EK012345","FI 555 EE","#1 Brabus","Smart",2024,"Digital White","electric","AWD","hatchback",0,428,1820,"Toscana","Firenze","Chiara De Luca","POL-2024-00078","CASKO","AXA",850,"2024-05-10","2026-05-09","active",-16.3,0,1,88,12800),
    ("WBAPH5C55BA654321","BO 666 FF","320d","BMW",2018,"Black Sapphire","diesel","RWD","sedan",1995,190,1540,"Emilia-Romagna","Bologna","Roberto Ferrara","POL-2021-00299","RCA","Cattolica",780,"2021-07-15","2025-07-14","active",-2.1,4,0,38,185000),
    ("ZFADD000GP1234567","VR 777 GG","Grecale Folgore","Maserati",2024,"Grigio Incognito","electric","AWD","SUV",0,557,2480,"Veneto","Verona","Alessandro Ferrari","POL-2024-00621","CASKO","Lloyd Italico",3200,"2024-08-01","2026-07-31","active",-5.5,0,1,72,6200),
    ("ZFAYN000GP9876543","PA 888 HH","Panda 1.0 Hybrid","Fiat",2022,"Bianco Gelato","hybrid","FWD","hatchback",999,70,1065,"Sicilia","Palermo","Giuseppe Ferraro","POL-2022-00744","RCA","UnipolSai",520,"2022-10-01","2025-09-30","active",-9.0,0,0,82,35200),
    ("UU1HSDCNG7654321A","CT 999 II","Sandero Stepway GPL","Dacia",2021,"Grigio Cometa","gpl","FWD","hatchback",999,101,1120,"Sicilia","Catania","Maria Greco","POL-2021-00856","RCA","Sara",450,"2021-04-15","2025-04-14","active",-5.0,1,0,73,67800),
    ("W1N2532XXNR123456","GE 010 LL","GLC 300e 4MATIC","Mercedes-Benz",2023,"Obsidian Black","plug_in_hybrid","AWD","SUV",1999,313,2150,"Liguria","Genova","Valentina Parodi","POL-2023-00933","CASKO","Allianz",2100,"2023-07-20","2025-07-19","active",-11.0,0,1,80,28700),
    ("JTMW43FV50D123456","BA 011 MM","RAV4 Hybrid","Toyota",2022,"Dark Blue Mica","hybrid","AWD","SUV",2487,222,1690,"Puglia","Bari","Antonio Russo","POL-2022-01001","CASKO","Generali",1050,"2022-11-10","2025-11-09","active",-13.5,0,1,86,41300),
    ("WF0XXXGCDXNY12345","CA 012 NN","Transit Custom 2.0 EcoBlue","Ford",2021,"Frozen White","diesel","FWD","van",1996,130,2050,"Sardegna","Cagliari","Salvatore Melis","POL-2021-01122","RCA","Cattolica",680,"2021-08-01","2025-07-31","active",-3.0,2,0,60,98500),
    ("W0SVA2E17NT123456","PE 013 OO","Corsa-e","Opel",2023,"Volt Yellow","electric","FWD","hatchback",0,136,1530,"Umbria","Perugia","Laura Bianchi","POL-2023-01234","CASKO","UnipolSai",750,"2023-09-01","2025-08-31","active",-15.0,0,1,90,15600),
    ("ZFAAB000JP5432109","AO 014 PP","595 Turismo","Abarth",2020,"Grigio Record","petrol","FWD","hatchback",1368,165,1110,"Valle d'Aosta","Aosta","Pietro Gallo","POL-2020-01345","RCA","Sara",920,"2020-06-15","2025-06-14","active",-1.5,1,0,45,56700),
    ("TMBAG9NP4N0123456","TN 015 QQ","Octavia Wagon 2.0 TDI","Skoda",2022,"Quartz Grey","diesel","FWD","wagon",1968,150,1450,"Trentino-Alto Adige","Trento","Hans Gruber","POL-2022-01456","CASKO","Zurich",880,"2022-03-01","2025-02-28","expired",-7.5,0,1,76,52400),
]

def _telem(v):
    """Generate realistic telemetry for a vehicle tuple."""
    vin,_,_,_,_,_,pwt,_,_,_,_,_,region,_,_,_,_,_,_,_,_,ps,_,_,bb,ds,odo = v
    is_ev = pwt == "electric"
    is_diesel = pwt == "diesel"
    return {
        "vin": vin, "current_odometer_km": odo, "driving_score": ds,
        "avg_speed_kmh": round(random.uniform(40,95),1),
        "harsh_events_avg": random.randint(0,5),
        "harsh_events_heavy": random.randint(0,2),
        "harsh_events_extreme": random.randint(0,1),
        "green_speed_pct": round(random.uniform(60,95),1),
        "tpms_fl": round(random.uniform(2.1,2.5),2),
        "tpms_fr": round(random.uniform(2.1,2.5),2),
        "tpms_rl": round(random.uniform(2.1,2.5),2),
        "tpms_rr": round(random.uniform(2.1,2.5),2),
        "coolant_temp_c": round(random.uniform(82,98),1) if not is_ev else None,
        "coolant_pressure_bar": round(random.uniform(1.0,1.5),2) if not is_ev else None,
        "battery_soc": round(random.uniform(30,95),1) if is_ev or pwt in ("hybrid","plug_in_hybrid") else None,
        "battery_soh": round(random.uniform(85,100),1) if is_ev or pwt in ("hybrid","plug_in_hybrid") else None,
        "oil_temp_c": round(random.uniform(90,110),1) if not is_ev else None,
        "oil_pressure_bar": round(random.uniform(2.5,4.0),2) if not is_ev else None,
        "fuel_level_pct": round(random.uniform(15,85),1) if not is_ev else None,
        "engine_rpm": round(random.uniform(700,2500),0) if not is_ev else 0,
        "throttle_position_pct": round(random.uniform(5,40),1),
        "brake_pressure_bar": round(random.uniform(0,5),2),
        "steering_angle_deg": round(random.uniform(-15,15),1),
        "transmission_temp_c": round(random.uniform(60,90),1),
        "dtc_codes_json": "[]",
        "gps_lat": round(random.uniform(37.5,46.5),6) if bb else None,
        "gps_lon": round(random.uniform(7.0,18.5),6) if bb else None,
        "gps_altitude_m": round(random.uniform(10,500),1) if bb else None,
        "gps_heading_deg": round(random.uniform(0,360),1) if bb else None,
        "accel_x_g": round(random.uniform(-0.3,0.3),3) if bb else None,
        "accel_y_g": round(random.uniform(-0.2,0.2),3) if bb else None,
        "accel_z_g": round(random.uniform(0.95,1.05),3) if bb else None,
        "gyro_roll_deg": round(random.uniform(-2,2),2) if bb else None,
        "gyro_pitch_deg": round(random.uniform(-3,3),2) if bb else None,
        "gyro_yaw_deg": round(random.uniform(-5,5),2) if bb else None,
        "blackbox_event_type": "normal" if bb else None,
        "has_blackbox": bb,
        "last_sync_timestamp": datetime.now().isoformat(),
    }

TIRE_SPECS = [
    ("Continental","EcoContact 6","225/50R17",{"width":225,"aspect_ratio":50,"rim":17,"speed_index":"Y","load_index":98}),
    ("Michelin","Pilot Sport 4","245/45R18",{"width":245,"aspect_ratio":45,"rim":18,"speed_index":"Y","load_index":100}),
    ("Pirelli","P Zero","255/40R20",{"width":255,"aspect_ratio":40,"rim":20,"speed_index":"Y","load_index":101}),
    ("Hankook","Ventus S1 evo3","225/45R17",{"width":225,"aspect_ratio":45,"rim":17,"speed_index":"W","load_index":94}),
    ("Goodyear","EfficientGrip","205/55R16",{"width":205,"aspect_ratio":55,"rim":16,"speed_index":"V","load_index":91}),
    ("Bridgestone","Turanza T005","195/65R15",{"width":195,"aspect_ratio":65,"rim":15,"speed_index":"H","load_index":91}),
]

DEMO_COMPONENTS = []  # Built dynamically in seed

DEMO_INVESTIGATIONS = [
    {"case":"CASE-2024-00142","vin":"WAUZZZ8V9NA123456","date":"2024-11-02","type":"collision","loc":"Via Appia Nuova, Roma","lat":41.87,"lng":12.51,
     "desc":"Front collision at intersection. Driver ran red light at 55 km/h. Airbags deployed.","status":"open","priority":"high","fraud":72,
     "speed":55,"gforce":4.2,"glat":1.1,"abs":1,"airbag":1,"coolant":102,"adjuster":"Dr. Verdi"},
    {"case":"CASE-2024-00287","vin":"YV1XZ91234567890A","date":"2024-11-15","type":"rear_end","loc":"A1 Milano-Roma, km 342","lat":44.72,"lng":11.35,
     "desc":"Low-speed rear-end collision in highway traffic. Bumper and tailgate damage.","status":"under_review","priority":"medium","fraud":15,
     "speed":25,"gforce":1.8,"glat":0.3,"abs":0,"airbag":0,"coolant":88,"adjuster":"Dr. Neri"},
    {"case":"CASE-2024-00391","vin":"5YJYGDEE3NF345678","date":"2024-12-22","type":"rear_end","loc":"Corso Francia, Torino","lat":45.08,"lng":7.66,
     "desc":"Severe rear-end collision. Driver ignored multiple brake warnings. Brake pads critically worn.","status":"open","priority":"critical","fraud":89,
     "speed":78,"gforce":6.1,"glat":2.4,"abs":1,"airbag":1,"coolant":95,"adjuster":"Dr. Verdi"},
    {"case":"CASE-2025-00012","vin":"WBAPH5C55BA654321","date":"2025-03-10","type":"side_impact","loc":"Via Indipendenza, Bologna","lat":44.49,"lng":11.34,
     "desc":"Side impact at T-junction. Third party vehicle failed to yield. Moderate door/panel damage.","status":"resolved","priority":"medium","fraud":8,
     "speed":35,"gforce":3.0,"glat":3.5,"abs":1,"airbag":0,"coolant":96,"adjuster":"Dr. Bianchi"},
    {"case":"CASE-2025-00045","vin":"UU1HSDCNG7654321A","date":"2025-04-18","type":"collision","loc":"SS114, Catania","lat":37.50,"lng":15.09,
     "desc":"Head-on collision on provincial road. Other driver crossed center line. Significant front damage.","status":"under_review","priority":"high","fraud":42,
     "speed":62,"gforce":5.5,"glat":0.8,"abs":1,"airbag":1,"coolant":91,"adjuster":"Dr. Neri"},
]


def seed_demo_data(conn):
    """Populate fresh demo fleet of 18 vehicles with full data."""
    print("🌱 Seeding demo data...")

    for v in DEMO_VEHICLES:
        vin,plate,model,mfr,year,color,pwt,dt,bt,disp,hp,wt,region,city,driver,pol,pt,ins,prem,ps,pe,pst,td,cc,bb,ds,odo = v

        # Ensure car_model exists
        existing = conn.execute("SELECT id FROM car_models WHERE model_name=?", (f"{mfr} {model}",)).fetchone()
        if existing:
            model_id = existing[0]
        else:
            cur = conn.execute("INSERT INTO car_models (model_name, car_type, powertrain, drivetrain, manufacturer, displacement_cc, power_hp, weight_kg) VALUES (?,?,?,?,?,?,?,?)",
                (f"{mfr} {model}", bt, pwt, dt, mfr, disp, hp, wt))
            model_id = cur.lastrowid

        # Insert or update vehicle
        existing_v = conn.execute("SELECT vin FROM vehicles WHERE vin=?", (vin,)).fetchone()
        if existing_v:
            conn.execute("""UPDATE vehicles SET plate_number=?,model_id=?,production_date=?,region_name=?,color=?,weight_kg=?,power_hp=?,displacement_cc=?,
                registration_date=?,status=?,body_type=?,country=?,city=?,driver_name=?,driver_gender=?,
                policy_number=?,policy_type=?,insurer=?,premium_eur=?,policy_start=?,policy_expiry=?,policy_status=?,telematics_discount=?,claims_count=?
                WHERE vin=?""",
                (plate,model_id,f"{year}-01-01",region,color,wt,hp,disp,f"{year}-01-15","active",bt,"IT",city,driver,
                 random.choice(["M","F"]),pol,pt,ins,prem,ps,pe,pst,td,cc,vin))
        else:
            conn.execute("""INSERT INTO vehicles (vin,plate_number,model_id,production_date,region_name,lat,lon,color,weight_kg,power_hp,displacement_cc,
                registration_date,status,body_type,country,city,driver_name,driver_age,driver_gender,vehicle_category,
                policy_number,policy_type,insurer,premium_eur,policy_start,policy_expiry,policy_status,telematics_discount,claims_count)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (vin,plate,model_id,f"{year}-01-01",region,
                 round(random.uniform(37.5,46.5),4),round(random.uniform(7.0,18.5),4),
                 color,wt,hp,disp,f"{year}-01-15","active",bt,"IT",city,driver,
                 random.randint(25,60),random.choice(["M","F"]),bt,
                 pol,pt,ins,prem,ps,pe,pst,td,cc))

        # Telemetry
        t = _telem(v)
        existing_t = conn.execute("SELECT vin FROM vehicle_telemetry WHERE vin=?", (vin,)).fetchone()
        cols = list(t.keys())
        if existing_t:
            sets = ", ".join(f"{c}=?" for c in cols if c != "vin")
            vals = [t[c] for c in cols if c != "vin"]
            vals.append(vin)
            conn.execute(f"UPDATE vehicle_telemetry SET {sets} WHERE vin=?", vals)
        else:
            placeholders = ",".join("?" * len(cols))
            conn.execute(f"INSERT INTO vehicle_telemetry ({','.join(cols)}) VALUES ({placeholders})", [t[c] for c in cols])

        # Components — 4 tires + brakes + battery per vehicle
        tire_spec = random.choice(TIRE_SPECS)
        for pos in ["FL","FR","RL","RR"]:
            sn = f"TIR-{year}-{vin[-5:]}-{pos}"
            wear = round(random.uniform(10,95),1)
            status_comp = "installed"
            health = "healthy" if wear < 60 else ("warning" if wear < 80 else "critical")
            specs = {**tire_spec[3], "model": tire_spec[1], "size": tire_spec[2]}
            try:
                conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,position,brand,model_name,specs_json,wear_percent,health_status,installed_date,installed_km,status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sn,vin,"tire",pos,tire_spec[0],tire_spec[1],json.dumps(specs),wear,health,f"{year}-01-15",odo*0.1,status_comp))
            except Exception:
                pass

        # Brake pads
        for pos in ["front","rear"]:
            sn = f"BRK-{year}-{vin[-5:]}-{pos}"
            wear = round(random.uniform(10,90),1)
            health = "healthy" if wear < 50 else ("warning" if wear < 75 else "critical")
            specs = {"type":"disc","material":"semi-metallic" if pwt!="electric" else "low-dust ceramic","position":pos}
            try:
                conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,position,brand,model_name,specs_json,wear_percent,health_status,installed_date,installed_km,status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sn,vin,"brake_pad",pos,"Brembo","OE Replacement",json.dumps(specs),wear,health,f"{year}-01-15",odo*0.05,"installed"))
            except Exception:
                pass

        # EV/Hybrid battery
        if pwt in ("electric","hybrid","plug_in_hybrid"):
            sn = f"BAT-{year}-{vin[-5:]}"
            soh = round(random.uniform(82,100),1)
            health = "healthy" if soh > 90 else ("warning" if soh > 80 else "critical")
            cap = random.choice([42,54,62,77,82,100])
            specs = {"capacity_kwh":cap,"soh_percent":soh,"cycles":random.randint(50,800),"chemistry":"NMC","charge_rate_kw":random.choice([50,100,150,250])}
            try:
                conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,position,brand,model_name,specs_json,wear_percent,health_status,installed_date,installed_km,status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sn,vin,"ev_battery","main","OEM","Integrated Pack",json.dumps(specs),round(100-soh,1),health,f"{year}-01-15",0,"installed"))
            except Exception:
                pass

    # Stocked (recovered) components — 15 items
    for i in range(15):
        cat = random.choice(["tire","brake_pad","ev_battery"])
        src_v = random.choice(DEMO_VEHICLES)
        sn = f"STK-{cat[:3].upper()}-2025-{i+1:04d}"
        if cat == "tire":
            ts = random.choice(TIRE_SPECS)
            wear = round(random.uniform(55,92),1)
            rec = random.choice(["Retread","Recycle (Granulate)","Resell (Used)"])
            specs = {**ts[3], "model": ts[1], "size": ts[2]}
            brand, model_n = ts[0], ts[1]
        elif cat == "brake_pad":
            wear = round(random.uniform(60,88),1)
            rec = random.choice(["Friction Material Recovery","Scrap Metal Smelting"])
            specs = {"type":"disc","material":"semi-metallic"}
            brand, model_n = "Brembo", "OE Replacement"
        else:
            wear = round(random.uniform(15,40),1)
            soh = round(100-wear,1)
            rec = random.choice(["Grid Storage","Second-Life ESS","Black Mass Recycling"])
            specs = {"capacity_kwh":random.choice([42,62,77]),"soh_percent":soh,"cycles":random.randint(400,900),"chemistry":"NMC"}
            brand, model_n = "OEM", "Recovered Module"
        try:
            conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,brand,model_name,specs_json,wear_percent,health_status,
                status,removed_date,removal_reason,ai_recommendation,ai_reasoning,recovery_value_eur,co2_saved_kg,destination_facility)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (sn,src_v[0],cat,brand,model_n,json.dumps(specs),wear,"stocked","stocked",
                 f"2025-0{random.randint(1,5):d}-{random.randint(1,28):02d}","scheduled_replacement",
                 rec,f"AI analysis: {rec} recommended based on {wear}% wear.",
                 round(random.uniform(5,200),2),round(random.uniform(10,60),1),
                 random.choice(["Marangoni Retreading S.p.A.","ELT Italia","Cobat","Enel X Storage","RecyBEM"])))
        except Exception:
            pass

    # Investigations
    for inv in DEMO_INVESTIGATIONS:
        tpms = json.dumps({"fl":round(random.uniform(1.5,2.5),2),"fr":round(random.uniform(1.5,2.5),2),"rl":round(random.uniform(1.5,2.5),2),"rr":round(random.uniform(1.5,2.5),2)})
        try:
            conn.execute("""INSERT INTO investigations (case_number,vehicle_vin,incident_date,incident_type,incident_location,incident_lat,incident_lng,
                incident_description,status,priority,fraud_risk_score,speed_at_impact,g_force_max,g_force_lateral,abs_triggered,airbag_deployed,
                tpms_snapshot_json,coolant_temp,assigned_adjuster) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (inv["case"],inv["vin"],inv["date"],inv["type"],inv["loc"],inv["lat"],inv["lng"],
                 inv["desc"],inv["status"],inv["priority"],inv["fraud"],inv["speed"],inv["gforce"],inv["glat"],
                 inv["abs"],inv["airbag"],tpms,inv["coolant"],inv["adjuster"]))
        except Exception:
            pass

    # Investigation photos
    DEMO_PHOTOS = [
        ("CASE-2024-00142", "case_00142_1.png", "Front collision damage — hood, headlights, bumper", "damage"),
        ("CASE-2024-00287", "case_00287_1.png", "Rear-end impact — bumper and tailgate damage", "damage"),
        ("CASE-2024-00391", "case_00391_1.png", "Severe rear collision — trunk destroyed, structural damage", "damage"),
        ("CASE-2025-00012", "case_00012_1.png", "Side impact — driver door caved in, window shattered", "damage"),
        ("CASE-2025-00045", "case_00045_1.png", "Head-on collision — front end destroyed, radiator exposed", "damage"),
    ]
    for case, filename, caption, ptype in DEMO_PHOTOS:
        try:
            conn.execute("INSERT INTO investigation_photos (case_number, filename, caption, photo_type) VALUES (?,?,?,?)",
                (case, filename, caption, ptype))
        except Exception:
            pass

    # Maintenance events
    for v in DEMO_VEHICLES:
        vin = v[0]
        events = [
            (f"{v[4]}-06-15","scheduled","Routine VSI diagnostic completed","info"),
            (f"{v[4]+1}-01-10","scheduled","Annual service at authorized dealer","info"),
        ]
        if v[23] > 0:  # claims_count
            events.append((f"{v[4]+1}-03-15","alert","Collision reported. Telemetry locked.","critical"))
        if v[25] < 50:  # driving_score
            events.append((f"{v[4]+1}-02-01","warning","VSI critical: aggressive driving pattern detected","warning"))
        for ev in events:
            try:
                conn.execute("INSERT INTO maintenance_events (vehicle_vin,event_date,event_type,description,severity) VALUES (?,?,?,?,?)",
                    (vin,ev[0],ev[1],ev[2],ev[3]))
            except Exception:
                pass

    conn.commit()

    # ── Driver Accounts & Vehicle Linking ─────────────────────────────────
    # Andrea Moretti's second car — 2008 Fiat Panda (no blackbox, old ECU)
    panda_vin = "ZFA16900001234567"
    panda_exists = conn.execute("SELECT vin FROM vehicles WHERE vin=?", (panda_vin,)).fetchone()
    if not panda_exists:
        # Car model
        panda_model = conn.execute("SELECT id FROM car_models WHERE model_name=?", ("Fiat Panda 1.2 Active",)).fetchone()
        if panda_model:
            pm_id = panda_model[0]
        else:
            cur = conn.execute("INSERT INTO car_models (model_name,car_type,powertrain,drivetrain,manufacturer,displacement_cc,power_hp,weight_kg) VALUES (?,?,?,?,?,?,?,?)",
                ("Fiat Panda 1.2 Active","hatchback","petrol","FWD","Fiat",1242,69,975))
            pm_id = cur.lastrowid

        conn.execute("""INSERT INTO vehicles (vin,plate_number,model_id,production_date,region_name,lat,lon,color,weight_kg,power_hp,displacement_cc,
            registration_date,status,body_type,country,city,driver_name,driver_age,driver_gender,vehicle_category,
            policy_number,policy_type,insurer,premium_eur,policy_start,policy_expiry,policy_status,telematics_discount,claims_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (panda_vin,"MI 500 AM",pm_id,"2008-03-01","Lombardia",45.4642,9.1900,"Grigio Maestro",975,69,1242,
             "2008-04-10","active","hatchback","IT","Milano","Andrea Moretti",34,"M","hatchback",
             "POL-2020-00399","RCA","UnipolSai",380,"2024-01-01","2026-12-31","active",-2.0,2))

        # Limited telemetry (no blackbox, basic ECU only)
        conn.execute("""INSERT INTO vehicle_telemetry (vin,current_odometer_km,driving_score,avg_speed_kmh,
            oil_temp_c,oil_pressure_bar,fuel_level_pct,engine_rpm,coolant_temp_c,coolant_pressure_bar,
            brake_pressure_bar,throttle_position_pct,dtc_codes_json,has_blackbox,last_sync_timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (panda_vin,187400,71,38.5,98.2,3.1,42.0,850,94.5,1.2,0.8,12.3,
             json.dumps(["P0301","P0420"]),0,datetime.now().isoformat()))

        # Old components with high wear
        for pos in ["FL","FR","RL","RR"]:
            sn = f"TIR-2023-PANDA-{pos}"
            wear = round(random.uniform(55,88),1)
            health = "warning" if wear < 80 else "critical"
            specs = {"width":175,"aspect_ratio":65,"rim":14,"model":"Cinturato P1","size":"175/65R14"}
            try:
                conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,position,brand,model_name,specs_json,wear_percent,health_status,installed_date,installed_km,status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sn,panda_vin,"tire",pos,"Pirelli","Cinturato P1",json.dumps(specs),wear,health,"2023-03-15",165000,"installed"))
            except: pass

        for pos in ["front","rear"]:
            sn = f"BRK-2022-PANDA-{pos}"
            wear = round(random.uniform(70,95),1)
            health = "critical" if wear > 85 else "warning"
            specs = {"type":"disc","material":"semi-metallic","position":pos}
            try:
                conn.execute("""INSERT INTO components (serial_number,vehicle_vin,category,position,brand,model_name,specs_json,wear_percent,health_status,installed_date,installed_km,status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sn,panda_vin,"brake_pad",pos,"TRW","Standard OE",json.dumps(specs),wear,health,"2022-06-20",142000,"installed"))
            except: pass

        # Maintenance history for old car
        maint_events = [
            ("2024-11-15","oil_change","Engine oil change + filter (10W-40)",185200,85,"Autofficina Rossi"),
            ("2024-06-10","tire_rotation","Tire rotation + alignment check",181000,40,"Gomme Express"),
            ("2023-03-15","tire_change","All 4 tires replaced (Pirelli Cinturato P1 175/65R14)",165000,320,"Gomme Express"),
            ("2023-09-20","brake_service","Front brake pads + disc inspection",172000,180,"Autofficina Rossi"),
            ("2022-06-20","brake_service","Rear brake pads replaced (TRW Standard OE)",142000,120,"Autofficina Rossi"),
            ("2024-03-01","scheduled","Annual inspection (Revisione) — PASSED",178000,80,"MCTC Centro Revisioni"),
        ]
        for ev in maint_events:
            try:
                conn.execute("INSERT INTO maintenance_events (vehicle_vin,event_date,event_type,description,mileage_km,cost_eur,facility) VALUES (?,?,?,?,?,?,?)",
                    (panda_vin,ev[0],ev[1],ev[2],ev[3],ev[4],ev[5]))
            except: pass

    # Seed driver account
    driver_exists = conn.execute("SELECT id FROM driver_accounts WHERE email=?", ("andrea.moretti@cyclesync.io",)).fetchone()
    if not driver_exists:
        conn.execute("INSERT INTO driver_accounts (email,display_name,phone,pinned_vin) VALUES (?,?,?,?)",
            ("andrea.moretti@cyclesync.io","Andrea Moretti","+39 338 1234567","WBAXH5C55DDW12345"))
        driver_id = conn.execute("SELECT id FROM driver_accounts WHERE email=?", ("andrea.moretti@cyclesync.io",)).fetchone()[0]
        # Link both vehicles
        conn.execute("INSERT OR IGNORE INTO driver_vehicles (driver_id,vin) VALUES (?,?)", (driver_id,"WBAXH5C55DDW12345"))
        conn.execute("INSERT OR IGNORE INTO driver_vehicles (driver_id,vin) VALUES (?,?)", (driver_id,panda_vin))

    conn.commit()
    print(f"✅ Seeded {len(DEMO_VEHICLES)} vehicles + driver accounts with components, telemetry, investigations.")
