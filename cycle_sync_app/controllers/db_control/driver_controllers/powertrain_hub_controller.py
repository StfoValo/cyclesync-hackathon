from PyQt6.QtCore import QObject
from models.driver_models.powertrain_models.bev_model import BEVModel
# We will import the ICE model later when we build it!
# from models.driver_models.powertrain_models.ice_model import ICEModel 
from datetime import datetime

class PowertrainHubController(QObject):
    def __init__(self, view, vehicle_model, username):
        super().__init__()
        self.view = view  # This will be the PowertrainHubWidget (the QStackedWidget container)
        self.vehicle_model = vehicle_model
        self.username = username
        self.active_vin = None
        
        # Initialize our mathematical physics engines
        self.bev_model = BEVModel()
        # self.ice_model = ICEModel()
        
        # Wire up simulation buttons from the sub-views
        self.view.bev_widget.simulate_requested.connect(self.simulate_wear)
        # self.view.ice_widget.simulate_requested.connect(self.simulate_wear)

    def set_active_vin(self, vin):
        """Triggered globally when the driver changes vehicles in the top menu."""
        self.active_vin = vin
        self.refresh_hub()

    def refresh_hub(self):
        if not self.active_vin:
            return

        # Fetch the vehicle data to determine the powertrain type
        vehicles = self.vehicle_model.get_vehicles_by_owner(self.username)
        active_vehicle = next((v for v in vehicles if v[0] == self.active_vin), None)
        
        if not active_vehicle:
            return
            
        # Unpack indices based on our vehicle_model SQL query
        vin_str, model_name, car_type, image_path, odo, score, powertrain, drivetrain, price = active_vehicle
        
        # Calculate roughly how old the car is based on odometer (assuming 15k km/year)
        age_yr = max(odo / 15000.0, 0.5)

        if powertrain == 'BEV':
            # 1. Flip the UI to the Battery Dashboard
            self.view.stacked_widget.setCurrentIndex(0) 
            
            # 2. Package parameters for the BEV Model
            params = {
                'chem': 'NMC' if 'SUV' in car_type.upper() else 'LFP', # Dynamic chemistry assumption
                'cap_kWh': 100.0 if 'SUV' in car_type.upper() else 60.0,
                'wltp_km': 600.0 if 'SUV' in car_type.upper() else 400.0,
                'age_yr': age_yr,
                'km_total': odo,
                'veh_price': price,
                'temp_C': 18.0,
                'driving_score': score
            }
            
            # 3. Run the MATLAB-derived math
            kpis = self.bev_model.estimate_battery_life(params)
            
            # 4. Update the BEV View
            self.view.bev_widget.update_dashboard(
                model_name=model_name,
                odo=odo,
                soh=kpis['soh'],
                range_real=kpis['range_real'],
                sl_score=kpis['second_life_score'],
                circ_score=kpis['circularity_score'],
                resale=kpis['resale_value_eur'],
                eol_range=kpis['eol_range'],      
                projection=kpis['projection']     
            )
        
            
        elif powertrain == 'ICE':
            # 1. Flip the UI to the Engine Dashboard
            self.view.stacked_widget.setCurrentIndex(1)
            
            # TODO: We will build out the ice_model parameters and update_dashboard here next!
            pass 

    def simulate_wear(self):
        from models.telemetry_simulation.trip_simulator import TripSimulator
        if self.active_vin:
            for _ in range(25): # Simulate a month of driving
                TripSimulator.simulate_trip(self.active_vin)
            self.refresh_hub()