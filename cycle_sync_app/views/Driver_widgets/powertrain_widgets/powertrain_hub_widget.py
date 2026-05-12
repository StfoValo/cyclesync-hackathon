from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import SubtitleLabel

from views.Driver_widgets.powertrain_widgets.bev_widget import BEVWidget
# We will create the ICE widget later, so we use a temporary placeholder to prevent crashes!

class PlaceholderICEWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        label = SubtitleLabel("ICE Engine Analytics in development...", self)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)

class PowertrainHubWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("PowertrainHubWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)
        
        self.bev_widget = BEVWidget(self)
        self.ice_widget = PlaceholderICEWidget(self)
        
        self.stacked_widget.addWidget(self.bev_widget) # Index 0: BEV
        self.stacked_widget.addWidget(self.ice_widget) # Index 1: ICE