import math

class BEVModel:
    def estimate_battery_life(self, params: dict):
        chem = params.get('chem', 'NMC')
        cap_kWh = float(params.get('cap_kWh', 75.0))
        wltp_km = float(params.get('wltp_km', 500.0))
        age_yr = float(params.get('age_yr', 3.0))
        km_total = float(params.get('km_total', 45000.0))
        veh_price = float(params.get('veh_price', 50000.0))
        temp_C = float(params.get('temp_C', 15.0))
        
        driving_score = float(params.get('driving_score', 80.0))
        bad_habit_multiplier = (100.0 - driving_score) / 100.0
        
        fast_pct = 0.10 + (0.40 * bad_habit_multiplier)
        soc_max = 0.80 + (0.20 * bad_habit_multiplier)
        soc_min = 0.20 - (0.15 * bad_habit_multiplier)
        soc_avg = (soc_max + soc_min) / 2.0
        
        cycles = (km_total / max(wltp_km * 0.8, 1)) * (1.0 + (0.2 * bad_habit_multiplier))

        # --- CALIBRATED CHEMISTRY PARAMETERS ---
        # k_cal: Increased ~10x to match real-world 1-2% annual calendar aging
        # k_cyc: Increased ~8x to match real-world cycle wear over 200k km
        
        if 'LFP' in chem:
            k_cal, k_cyc, beta, Ea = 0.045, 0.009, 0.58, 0.54
            eol_soh, max_cycles, c_rate_max = 70, 3000, 3.0
        elif 'NCA' in chem:
            k_cal, k_cyc, beta, Ea = 0.095, 0.019, 0.60, 0.62
            eol_soh, max_cycles, c_rate_max = 80, 1500, 2.0
        else: # NMC (Default)
            k_cal, k_cyc, beta, Ea = 0.085, 0.016, 0.59, 0.58
            eol_soh, max_cycles, c_rate_max = 80, 1500, 2.5

        T_ref = 298.15
        T_K = temp_C + 273.15
        k_B = 8.617e-5
        
        arrhenius = math.exp((Ea / k_B) * (1 / T_ref - 1 / T_K))
        arrhenius = max(min(arrhenius, 4.0), 0.4)
        
        t_days = max(age_yr * 365, 1)
        delta_cal = k_cal * math.sqrt(t_days) * arrhenius

        kSOC_high = 1 + 2.5 * max(soc_max - 0.80, 0)**1.5
        kSOC_low  = 1 + 2.0 * max(0.20 - soc_min, 0)**1.5
        kSOC_avg  = 1 + 0.8 * (abs(soc_avg - 0.50) / 0.50)**2
        kSOC = kSOC_high * kSOC_low * kSOC_avg

        DOD = max(min(soc_max - soc_min, 1.0), 0.05)
        Ah_total = cycles * cap_kWh * (1000/400) * DOD
        delta_cyc = k_cyc * (Ah_total**beta) * kSOC

        kDC = 1.0 + (0.35 * fast_pct) 
        delta_fc = delta_cyc * (fast_pct * (kDC - 1.0))
        delta_cyc_total = delta_cyc + delta_fc

        total_loss = (delta_cal + delta_cyc_total) * arrhenius
        soh = max(100.0 - total_loss, 0.0)

        # --- ADVANCED KPIs & PROJECTION ---
        range_residual = wltp_km * (soh / 100.0) * 0.80 
        eol_range = wltp_km * (eol_soh / 100.0) * 0.80
        
        # Determine average annual usage to map time-degradation to distance
        ann_km = km_total / max(age_yr, 0.5)
        
        projection_data = []
        current_sim_loss = total_loss
        current_sim_km = km_total
        
        # Calculate the base degradation rate per 10,000 km driven
        loss_per_10k = (total_loss / max(km_total, 1000.0)) * 10000.0
        
        # Project forward for the next ~250,000 km in 10,000 km steps
        for step in range(26):
            future_soh = max(100.0 - current_sim_loss, 0.0)
            future_range = wltp_km * (future_soh / 100.0) * 0.80
            projection_data.append((current_sim_km, future_range))
            
            current_sim_km += 10000
            # Non-linear acceleration: as SEI layer thickens, capacity drop accelerates
            current_sim_loss += loss_per_10k * (1.0 + (step * 0.08))

        cycle_ratio = cycles / max_cycles
        sl_soh_score = max(min((soh - eol_soh) / (100 - eol_soh) * 100, 100), 0)
        sl_chem_score = 95 if 'LFP' in chem else (70 if 'NMC' in chem else 60)
        sl_cycle_score = max(100 - cycle_ratio * 100, 0)
        second_life_score = min(max(0.45 * sl_soh_score + 0.30 * sl_chem_score + 0.25 * sl_cycle_score, 0), 100)

        co2_new_battery = 90.0 * cap_kWh
        soh_fraction_left = max(soh - eol_soh, 0) / (100 - eol_soh)
        co2_saved = co2_new_battery * soh_fraction_left
        
        CB1 = sl_soh_score
        CB2 = second_life_score
        CB3 = soh_fraction_left * 100
        CB4 = 88 if 'LFP' in chem else 72
        circularity_score = min(max(0.35 * CB1 + 0.25 * CB2 + 0.25 * CB3 + 0.15 * CB4, 0), 100)

        kSoH_resale = (soh / 100.0)**1.8
        kAge_resale = max(1.0 - age_yr * 0.06, 0.30)
        resale_val = veh_price * kSoH_resale * kAge_resale * 0.40

        return {
            'soh': soh,
            'range_real': range_residual,
            'eol_range': eol_range,             
            'projection': projection_data,      
            'second_life_score': second_life_score,
            'circularity_score': circularity_score,
            'resale_value_eur': resale_val,
            'co2_saved': co2_saved,
            'cycles_used': cycles
        }