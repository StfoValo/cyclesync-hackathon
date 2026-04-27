from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, FluentIcon, setTheme, Theme, NavigationItemPosition

# Import the original Hub and Controller
from views.Recycler_widgets.recycler_hub import RecyclerHub
from models.recycler_models.macro_market_model import MacroMarketModel
from controllers.db_control.recycler_controllers.analytics_controller import AnalyticsController

# Import the new Explorer
from views.Recycler_widgets.company_explorer_widget import CompanyExplorerWidget 
from views.Recycler_widgets.taxonomy_editor_widget import TaxonomyEditorWidget

class MainWindowRecycler(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None, username=None):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowTitle("CycleSync - Recycler Hub")
        self.resize(1100, 750)
        
        # 1. Initialize the new Landing Page (Company Explorer)
        self.explorer_page = CompanyExplorerWidget(self)
        self.taxonomy_editor = TaxonomyEditorWidget(self)
        
        # 2. Initialize the original Analytics Hub (Exchange + Terminal)
        self.analytics_hub = RecyclerHub(self)
        self.market_model = MacroMarketModel()
        self.analytics_controller = AnalyticsController(self.analytics_hub, self.market_model)

        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.taxonomy_editor, FluentIcon.SETTING, 'Ecosystem Management')
        # Top icon: The new Ecosystem Explorer
        self.addSubInterface(self.explorer_page, FluentIcon.GLOBE, 'Ecosystem Explorer')
        # Second icon: The AI Salvage Exchange
        self.addSubInterface(self.analytics_hub, FluentIcon.ACCEPT, 'Salvage Exchange')
        
        # Bottom Switcher
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch Role',
            onClick=lambda: self.switch_role_requested.emit("DRIVER"),
            position=NavigationItemPosition.BOTTOM
        )