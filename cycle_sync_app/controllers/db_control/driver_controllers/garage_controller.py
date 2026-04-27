import os
from PyQt6.QtCore import QObject
from models.telemetry_simulation.trip_simulator import TripSimulator

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class GarageController(QObject):
    def __init__(self, view, model, username):
        super().__init__()
        self.view = view
        self.model = model
        self.username = username
        self.view.trip_simulated.connect(self.handle_trip_simulation)
        self.active_vin = None
        
    def set_active_vin(self, vin):
        self.active_vin = vin
        self.load_garage_data()
        
    def handle_trip_simulation(self, vin):
        TripSimulator.simulate_trip(vin)
        self.load_garage_data()
        
    def load_garage_data(self):
        self.view.clear_cards()
        if not self.active_vin:
            self.view.show_empty_message()
            return
            
        vehicles = self.model.get_vehicles_by_owner(self.username)
        for row in vehicles:
            if row[0] == self.active_vin:
                # Safely unpack just the first 6 elements for the UI card
                vin_str, model_name, car_type, image_path, odometer, driving_score = row[:6]
                
                absolute_image_path = ""
                if image_path:
                    if not os.path.isabs(image_path):
                        absolute_image_path = os.path.join(APP_DIR, image_path)
                    else:
                        absolute_image_path = image_path
                
                self.view.render_vehicle_card(vin_str, model_name, car_type, absolute_image_path, odometer, driving_score)
                break