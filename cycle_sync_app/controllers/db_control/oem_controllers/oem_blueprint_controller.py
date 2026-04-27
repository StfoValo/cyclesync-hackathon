import os
import shutil
from PyQt6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
STORAGE_DIR = os.path.join(APP_DIR, 'storage', 'car_photos')

class OemBlueprintController:
    def __init__(self, view, model, account_id=None):
        self.view = view 
        self.model = model
        self.account_id = account_id
        
        self.view.gallery.create_requested.connect(self.show_form)
        self.view.form.cancel_requested.connect(self.show_gallery_and_clear_form)
        self.view.form.form_submitted.connect(self.handle_form_submission)
        self.load_existing_data()

    def show_form(self):
        self.view.stacked_widget.setCurrentIndex(1)

    def show_gallery_and_clear_form(self):
        self.clear_form()
        self.view.stacked_widget.setCurrentIndex(0)

    def clear_form(self):
        self.view.form.model_name_input.clear()
        self.view.form.car_type_combo.setCurrentIndex(0)
        self.view.form.powertrain_combo.setCurrentIndex(0)
        self.view.form.drivetrain_combo.setCurrentIndex(0)
        self.view.form.base_price_input.setValue(50000.0)
        self.view.form.manufacture_cost_input.setValue(30000.0)
        if hasattr(self.view.form, 'reset_image'):
            self.view.form.reset_image()

    def load_existing_data(self):
        results = self.model.get_models_by_account(self.account_id)
        resolved_results = []
        for row in results:
            row_list = list(row)
            img_path = row_list[7] # image_path is now at index 7!
            
            if img_path and not os.path.isabs(img_path):
                row_list[7] = os.path.join(APP_DIR, img_path)
            resolved_results.append(tuple(row_list))
            
        self.view.gallery.render_cards(resolved_results)
        
    def handle_form_submission(self, data):
        model_name = data.get("model_name", "").strip()
        base_price = data.get("base_price", 0.0)
        manufacture_cost = data.get("manufacture_cost", 0.0)
        car_type = data.get("car_type", "sedan")
        powertrain = data.get("powertrain", "ICE")
        drivetrain = data.get("drivetrain", "FWD")
        original_image_path = data.get("image_path", "")
        
        if not model_name:
            InfoBar.error(title='Validation Error', content='Model Name cannot be empty.', orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.view.form)
            return

        stored_relative_path = ""
        if original_image_path and os.path.exists(original_image_path):
            os.makedirs(STORAGE_DIR, exist_ok=True)
            safe_model_name = model_name.replace(" ", "_").lower()
            file_extension = os.path.splitext(original_image_path)[1]
            new_filename = f"{safe_model_name}{file_extension}"
            destination_absolute_path = os.path.join(STORAGE_DIR, new_filename)
            
            if os.path.abspath(original_image_path) != os.path.abspath(destination_absolute_path):
                shutil.copy2(original_image_path, destination_absolute_path)
            stored_relative_path = os.path.join('storage', 'car_photos', new_filename).replace('\\', '/')
            
        success = self.model.create_car_model(
            model_name=model_name, base_price=base_price, manufacture_cost=manufacture_cost,
            car_type=car_type, powertrain=powertrain, drivetrain=drivetrain,
            account_id=self.account_id, image_path=stored_relative_path
        )
        
        if success:
            InfoBar.success(title='Success', content=f'Car model "{model_name}" created.', orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.view.gallery)
            self.load_existing_data()
            self.show_gallery_and_clear_form()
        else:
            InfoBar.error(title='Database Error', content='Could not save blueprint.', orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.view.form)