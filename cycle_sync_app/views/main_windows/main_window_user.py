from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (FluentWindow, SubtitleLabel, FluentIcon, 
                            setTheme, Theme, NavigationItemPosition, ComboBox)

from views.Driver_widgets.garage_widget import GarageWidget
from views.Driver_widgets.tire_tracker_widget import TireTrackerWidget

from models.driver_models.vehicle_model import VehicleModel
from models.driver_models.tire_model import TireModel  # <-- Added missing model import

from controllers.db_control.driver_controllers.garage_controller import GarageController
from controllers.db_control.driver_controllers.tire_controller import TireController  # <-- Fixed path!

from views.Driver_widgets.powertrain_widgets.powertrain_hub_widget import PowertrainHubWidget
from controllers.db_control.driver_controllers.powertrain_hub_controller import PowertrainHubController

class PlaceholderPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(" ", "").replace("&", ""))
        self.label = SubtitleLabel(text, self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

class MainWindowUser(FluentWindow):
    # Signal emitted when judge wants to switch role
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None, username=None):
        super().__init__()
        self.account_id = account_id
        self.username = username
        
        # Force Dark Mode
        setTheme(Theme.DARK)

        self.setWindowTitle("CycleSync - Driver Dashboard")
        self.resize(1000, 700)

        self.garage_widget = GarageWidget()
        self.vehicle_model = VehicleModel()
        
        # Global Vehicle Selector in the Window Header
        self.vehicle_combo = ComboBox(self)
        self.vehicle_combo.setMinimumWidth(250)
        self.vehicle_combo.currentIndexChanged.connect(self._on_global_vehicle_changed)
        self.titleBar.layout().insertWidget(1, self.vehicle_combo)
        self.titleBar.layout().insertSpacing(2, 20)
        
        self.garage_controller = GarageController(self.garage_widget, self.vehicle_model, self.username)
        
        self.tire_interface = TireTrackerWidget() 
        self.tire_model = TireModel()
        self.tire_controller = TireController(self.tire_interface, self.tire_model, self.vehicle_model, self.username)

        self.powertrain_interface = PowertrainHubWidget()
        self.powertrain_controller = PowertrainHubController(self.powertrain_interface, self.vehicle_model, self.username)

        self.privacy_interface = PlaceholderPage("Data Privacy & Consent")
        
        self.init_navigation()
        self.load_global_vehicles()

    def load_global_vehicles(self):
        vehicles = self.vehicle_model.get_vehicles_by_owner(self.username)
        self.vehicle_combo.blockSignals(True)
        self.vehicle_combo.clear()
        for v in vehicles:
            vin, model_name = v[0], v[1]
            self.vehicle_combo.addItem(f"{model_name} ({vin[-6:]})", userData=vin)
        self.vehicle_combo.blockSignals(False)
        
        if vehicles:
            self._on_global_vehicle_changed()
        else:
            self.garage_controller.set_active_vin(None)
            self.tire_controller.set_active_vin(None)

    def _on_global_vehicle_changed(self):
        vin = self.vehicle_combo.currentData()
        if vin:
            self.garage_controller.set_active_vin(vin)
            self.tire_controller.set_active_vin(vin)

    def init_navigation(self):
        self.addSubInterface(
            self.garage_widget, 
            FluentIcon.HEART, 
            'My Garage'
        )

        self.addSubInterface(
            self.powertrain_interface, 
            FluentIcon.POWER_BUTTON, 
            'Powertrain Diagnostics')
        
        self.addSubInterface(
            self.tire_interface, 
            FluentIcon.SYNC, 
            'Tire Lifecycle Tracker'
        )
        
        self.addSubInterface(
            self.privacy_interface, 
            FluentIcon.FINGERPRINT, 
            'Data Privacy & Consent'
        )
        
        # Judge Mode Switcher
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch Role',
            onClick=lambda: self.switch_role_requested.emit("OEM"),
            position=NavigationItemPosition.BOTTOM
        )

    def _on_global_vehicle_changed(self):
        vin = self.vehicle_combo.currentData()
        if vin:
            self.garage_controller.set_active_vin(vin)
            self.tire_controller.set_active_vin(vin)
            # THIS IS THE MISSING LINK:
            self.powertrain_controller.set_active_vin(vin)
