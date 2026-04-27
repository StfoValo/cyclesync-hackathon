from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, FluentIcon, setTheme, Theme, NavigationItemPosition

# Import the Views
from views.Oem_widgets.oem_blueprint_hub import OemBlueprintHub
from views.Oem_widgets.fleet_telemetry_widget import FleetTelemetryWidget
from views.Oem_widgets.oem_ai_dashboard_widget import OemAiDashboardWidget

# Import the Models (New paths)
from models.oem_models.oem_model import OEMModel
from models.oem_models.fleet_model import FleetModel

# Import the Controllers (New paths)
from controllers.db_control.oem_controllers.oem_blueprint_controller import OemBlueprintController
from controllers.db_control.oem_controllers.fleet_controller import FleetController

class PlaceholderPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(" ", "").replace("&", ""))
        self.label = SubtitleLabel(text, self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

class MainWindowOem(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowTitle("CycleSync - OEM Portal")
        self.resize(1100, 750)
        
        self.account_id = account_id

        # 1. Initialize Views
        self.blueprint_interface = OemBlueprintHub(self)
        self.fleet_interface = FleetTelemetryWidget(self)
        self.supply_interface = OemAiDashboardWidget(self)
        
        # 2. Initialize Models
        self.oem_model = OEMModel()
        self.fleet_model = FleetModel()

        # 3. Initialize Controllers
        self.blueprint_controller = OemBlueprintController(self.blueprint_interface, self.oem_model, self.account_id)
        
        # Pass BOTH views to the FleetController
        self.fleet_controller = FleetController(self.fleet_interface, self.supply_interface, self.fleet_model, self.account_id)

        self.init_navigation()

    def init_navigation(self):
        # Changed the order: Blueprints first, Fleet second
        self.addSubInterface(self.blueprint_interface, FluentIcon.DOCUMENT, 'Car Blueprints')
        self.addSubInterface(self.fleet_interface, FluentIcon.GLOBE, 'Fleet Registry & Telemetry')
        self.addSubInterface(self.supply_interface, FluentIcon.CONNECT, 'Supply Chain Insights')
        
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch Role',
            onClick=lambda: self.switch_role_requested.emit("RECYCLER"),
            position=NavigationItemPosition.BOTTOM
        )