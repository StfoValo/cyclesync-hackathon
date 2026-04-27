from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from qfluentwidgets import (SubtitleLabel, SmoothScrollArea, FlowLayout, 
                            TitleLabel, BodyLabel, StrongBodyLabel, 
                            CaptionLabel, PrimaryPushButton)

class GlobalExchangeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("GlobalExchangeWidget")
        
        self.vBoxLayout = QVBoxLayout(self)
        
        self.subtitle = SubtitleLabel("Global Salvage Exchange - Macro Market View", self)
        self.vBoxLayout.addWidget(self.subtitle)
        
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("background-color: transparent;")
        self.flowLayout = FlowLayout(self.scrollWidget)
        self.flowLayout.setContentsMargins(10, 10, 10, 10)
        self.flowLayout.setHorizontalSpacing(20)
        self.flowLayout.setVerticalSpacing(20)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)
        
    def render_market_cards(self, market_data: list):
        # Clear existing
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        for row in market_data:
            card = QFrame()
            card.setFixedSize(300, 200)
            card.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;
                    border-radius: 10px;
                    border: 1px solid #3D3D3D;
                }
            """)
            cardLayout = QVBoxLayout(card)
            
            title = TitleLabel(str(row['material_sector']).upper())
            title.setStyleSheet("color: white;")
            cardLayout.addWidget(title)
            
            compLabel = BodyLabel(f"Component: {row['component_name']}")
            compLabel.setStyleSheet("color: #CCCCCC;")
            cardLayout.addWidget(compLabel)
            
            oemLabel = BodyLabel(f"Origin: {row['origin_oem']}")
            oemLabel.setStyleSheet("color: #CCCCCC;")
            cardLayout.addWidget(oemLabel)
            
            qtyLabel = StrongBodyLabel(f"Quantity: {row['quantity_tons']} Tons")
            qtyLabel.setStyleSheet("color: white;")
            cardLayout.addWidget(qtyLabel)
            
            valueLabel = CaptionLabel(f"Est. Value: €{row['estimated_salvage_value_eur']:,.2f}")
            valueLabel.setStyleSheet("color: #4CAF50;") # Green
            cardLayout.addWidget(valueLabel)
            
            btn = PrimaryPushButton("Run AI Market Analysis")
            cardLayout.addWidget(btn)
            
            self.flowLayout.addWidget(card)
