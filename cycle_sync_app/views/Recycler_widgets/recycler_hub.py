from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from views.Recycler_widgets.global_exchange_widget import GlobalExchangeWidget
from views.Recycler_widgets.material_analytics_widget import MaterialAnalyticsWidget

class RecyclerHub(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("RecyclerHub")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)
        
        self.exchange = GlobalExchangeWidget(self)
        self.analytics = MaterialAnalyticsWidget(self)
        
        self.stacked_widget.addWidget(self.exchange)   # Index 0
        self.stacked_widget.addWidget(self.analytics)  # Index 1