from PyQt6.QtCore import QObject
from models.telemetry_simulation.trip_simulator import TripSimulator
from views.Driver_widgets.tire_change_dialog import TireChangeDialog

class TireController(QObject):
    def __init__(self, view, tire_model, vehicle_model, username):
        super().__init__()
        self.view = view
        self.tire_model = tire_model
        self.vehicle_model = vehicle_model
        self.username = username
        self.active_vin = None

        self.view.btn_simulate.clicked.connect(self.simulate_wear)
        self.view.btn_change_tires.clicked.connect(self.show_change_tires_dialog)

    # --- THE MISSING METHOD ---
    def set_active_vin(self, vin):
        self.active_vin = vin
        self.refresh_ui()

    def show_change_tires_dialog(self):
        if not self.active_vin: return
        blueprints = self.tire_model.get_all_tire_blueprints()
        dialog = TireChangeDialog(self.view, blueprints)
        if dialog.exec():
            selected_id = dialog.get_selected_blueprint_id()
            if selected_id:
                _, current_odo = self.tire_model.get_tires_for_vehicle(self.active_vin)
                self.tire_model.mount_new_tires(self.active_vin, selected_id, current_odo)
                self.refresh_ui()

    def refresh_ui(self):
        if not self.active_vin: return
            
        tires, current_odo = self.tire_model.get_tires_for_vehicle(self.active_vin)
        if not tires: return

        # Get the dynamic vehicle specs based on the active VIN!
        vehicles = self.vehicle_model.get_vehicles_by_owner(self.username)
        active_vehicle = next((v for v in vehicles if v[0] == self.active_vin), None)
        if not active_vehicle: return
        
        # Unpack the new expanded tuple (indices 6, 7, 8 are our new fields)
        powertrain = active_vehicle[6]
        drivetrain = active_vehicle[7]
        base_price = active_vehicle[8]

        pos, mount_odo, db_tread, brand, model_name, lifespan, start_tread = tires[0]
        self.view.tire_brand_label.setText(brand.upper())
        self.view.tire_model_label.setText(model_name)
        km_driven = current_odo - mount_odo
        self.view.mounting_info_label.setText(f"Mounted at: {mount_odo:,} km | Distance Driven on Tires: {km_driven:,} km")

        # --- DYNAMIC ALGORITHM PARAMS ---
        algo_params = {
            'brand': 'Premium' if 'Premium' in brand else ('Sport' if 'Sport' in brand else 'Standard'),
            'compound': 'Medium',
            'km': km_driven,
            'is_new': True,
            'powertrain': powertrain, # Automatically handles BEV vs ICE!
            'mass': 1500 if powertrain == 'ICE' else 2100, # Simulated weight difference
            'drive': drivetrain,      # Automatically handles RWD vs AWD!
            'newPrice': 250
        }
        
        kpi = self.tire_model.estimate_tire_life(algo_params)
        
        self.view.update_safety_index(kpi['safety_index'])
        self.view.update_circularity_score(kpi['circularity_score'])
        self.view.update_resale_value(kpi['resale_value_eur'])

        for tire in tires:
            pos, mount_odo, db_tread, brand, model_name, lifespan, start_tread = tire
            actual_tread = kpi['t_front'] if 'F' in pos else kpi['t_rear']
            
            percentage = int((actual_tread / start_tread) * 100)
            self.view.tread_bars[pos].setValue(percentage)
            self.view.tread_labels[pos].setText(f"{actual_tread:.2f} mm")

            if actual_tread < 3.0:
                self.view.pressure_labels[pos].setText("Warning: Low Tread")
                self.view.pressure_labels[pos].setStyleSheet("color: #FF5A5A;")
            else:
                self.view.pressure_labels[pos].setText("34 PSI - Optimal")
                self.view.pressure_labels[pos].setStyleSheet("color: #00A67E;")

        min_tread = min(kpi['t_front'], kpi['t_rear'])
        if min_tread > 5.0:
            self.view.status_title.setText("System Status: Optimal")
            self.view.status_title.setStyleSheet("color: #00A67E;")
            self.view.ai_analysis_label.setText("Tires are in excellent condition. High safety margin.")
            self.view.btn_sync.setEnabled(False)
        elif min_tread > 3.0:
            self.view.status_title.setText("System Status: Monitor Wear")
            self.view.status_title.setStyleSheet("color: #E2B93B;")
            self.view.ai_analysis_label.setText(f"Tires wearing down. Estimated life remaining: {kpi['residual_pct']:.1f}%")
            self.view.btn_sync.setEnabled(False)
        else:
            self.view.status_title.setText("System Status: Critical Wear")
            self.view.status_title.setStyleSheet("color: #FF5A5A;")
            self.view.ai_analysis_label.setText(f"CRITICAL: AI matchmaker estimates €{kpi['resale_value_eur']:.2f} material salvage value.")
            self.view.btn_sync.setEnabled(True)

    def simulate_wear(self):
        if self.active_vin:
            for _ in range(50):
                TripSimulator.simulate_trip(self.active_vin)
            self.refresh_ui()