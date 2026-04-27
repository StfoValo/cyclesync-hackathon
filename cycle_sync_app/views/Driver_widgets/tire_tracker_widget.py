from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout
from qfluentwidgets import (SubtitleLabel, BodyLabel, TitleLabel, 
                            CaptionLabel, PrimaryPushButton, SmoothScrollArea, ProgressBar, ProgressRing)

class TireTrackerWidget(QWidget):
    simulate_requested = pyqtSignal(str)
    sync_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("TireTrackerWidget")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = SubtitleLabel("Tire Lifecycle & AI Matchmaker", self)
        main_layout.addWidget(self.title)
        main_layout.addSpacing(10)

        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(25)
        
        self._build_equipment_section()
        self._build_kpi_dashboard()
        self._build_telemetry_grid()
        self._build_matchmaker_section()
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def _create_card(self):
        card = QFrame(self)
        card.setStyleSheet("QFrame { background-color: #121212; border-radius: 12px; border: 1px solid #333333; }")
        return card

    def _build_equipment_section(self):
        self.equip_card = self._create_card()
        layout = QVBoxLayout(self.equip_card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(SubtitleLabel("Digital Twin Blueprint", self.equip_card))
        header_layout.addStretch()
        
        self.btn_change_tires = PrimaryPushButton("Mount New Tires", self.equip_card)
        header_layout.addWidget(self.btn_change_tires)
        
        layout.addLayout(header_layout)
        
        self.tire_brand_label = TitleLabel("Loading Brand...", self.equip_card)
        self.tire_brand_label.setStyleSheet("color: #FF8C00;")
        self.tire_model_label = BodyLabel("Loading Model...", self.equip_card)
        self.mounting_info_label = CaptionLabel("Mounted at: -- km | Distance Driven on Tires: -- km", self.equip_card)
        self.mounting_info_label.setStyleSheet("color: #888;")
        
        layout.addWidget(self.tire_brand_label)
        layout.addWidget(self.tire_model_label)
        layout.addWidget(self.mounting_info_label)
        
        self.layout.addWidget(self.equip_card)

    def _build_kpi_dashboard(self):
        self.kpi_card = self._create_card()
        layout = QHBoxLayout(self.kpi_card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        safety_layout = QVBoxLayout()
        safety_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.safety_ring = ProgressRing(self.kpi_card)
        self.safety_ring.setFixedSize(100, 100)
        self.safety_ring.setTextVisible(True)
        self.safety_ring.setValue(0)
        safety_layout.addWidget(BodyLabel("Safety Index", self.kpi_card), alignment=Qt.AlignmentFlag.AlignCenter)
        safety_layout.addWidget(self.safety_ring, alignment=Qt.AlignmentFlag.AlignCenter)
        
        circ_layout = QVBoxLayout()
        circ_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.circ_ring = ProgressRing(self.kpi_card)
        self.circ_ring.setFixedSize(100, 100)
        self.circ_ring.setTextVisible(True)
        self.circ_ring.setValue(0)
        circ_layout.addWidget(BodyLabel("Circularity Score", self.kpi_card), alignment=Qt.AlignmentFlag.AlignCenter)
        circ_layout.addWidget(self.circ_ring, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(safety_layout)
        layout.addLayout(circ_layout)
        self.layout.addWidget(self.kpi_card)

    def _build_telemetry_grid(self):
        self.telemetry_card = self._create_card()
        layout = QVBoxLayout(self.telemetry_card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(SubtitleLabel("Live Axle Telemetry", self.telemetry_card))
        header_layout.addStretch()
        self.btn_simulate = PrimaryPushButton("Simulate Tire Wear", self.telemetry_card)
        header_layout.addWidget(self.btn_simulate)
        layout.addLayout(header_layout)
        
        self.wheel_grid = QGridLayout()
        self.wheel_grid.setSpacing(15)
        
        self.tread_bars = {}
        self.tread_labels = {}
        self.pressure_labels = {}
        
        positions = [('Front Left (FL)', 0, 0, 'FL'), ('Front Right (FR)', 0, 1, 'FR'), 
                     ('Rear Left (RL)', 1, 0, 'RL'), ('Rear Right (RR)', 1, 1, 'RR')]
                     
        for title, row, col, key in positions:
            wheel_box = QFrame(self.telemetry_card)
            wheel_box.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; border: 1px solid #2a2a2a; }")
            w_layout = QVBoxLayout(wheel_box)
            
            w_layout.addWidget(BodyLabel(title, wheel_box))
            
            tread_val_label = BodyLabel("8.00 mm", wheel_box)
            self.tread_labels[key] = tread_val_label
            w_layout.addWidget(tread_val_label)
            
            tread_bar = ProgressBar(wheel_box)
            tread_bar.setFixedSize(150, 8)
            tread_bar.setValue(100)
            self.tread_bars[key] = tread_bar
            w_layout.addWidget(tread_bar)
            
            pressure_label = CaptionLabel("34 PSI - Optimal", wheel_box)
            pressure_label.setStyleSheet("color: #00A67E;")
            self.pressure_labels[key] = pressure_label
            w_layout.addWidget(pressure_label)
            
            self.wheel_grid.addWidget(wheel_box, row, col)
            
        layout.addLayout(self.wheel_grid)
        self.layout.addWidget(self.telemetry_card)

    def _build_matchmaker_section(self):
        self.sync_card = self._create_card()
        layout = QHBoxLayout(self.sync_card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text_layout = QVBoxLayout()
        self.status_title = SubtitleLabel("System Status: Optimal", self.sync_card)
        self.status_title.setStyleSheet("color: #00A67E;")
        self.ai_analysis_label = BodyLabel("AI Valuations and Recycler matches will appear here when wear reaches critical thresholds.", self.sync_card)
        
        text_layout.addWidget(self.status_title)
        text_layout.addWidget(self.ai_analysis_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Add resale label so update_resale_value doesn't crash
        resale_layout = QVBoxLayout()
        resale_layout.addWidget(CaptionLabel("Est. Salvage Value", self.sync_card))
        self.resale_label = TitleLabel("€0.00", self.sync_card)
        self.resale_label.setStyleSheet("color: #E2B93B;")
        resale_layout.addWidget(self.resale_label)
        
        layout.addLayout(resale_layout)
        layout.addSpacing(20)
        
        self.btn_sync = PrimaryPushButton("Analyze & Sync to OEM Data Lake", self.sync_card)
        layout.addWidget(self.btn_sync)
        
        self.layout.addWidget(self.sync_card)


    def update_safety_index(self, value: float):
        val = int(max(0, min(100, value)))
        self.safety_ring.setValue(val)
        self.safety_ring.setFormat(f"{val}%")
        
        # Change color based on safety
        if val > 75:
            self.safety_ring.setStyleSheet("") # Default fluent green
        elif val > 40:
            self.safety_ring.setStyleSheet("qproperty-color: #E2B93B;") # Yellow
        else:
            self.safety_ring.setStyleSheet("qproperty-color: #FF5A5A;") # Red

    def update_circularity_score(self, value: float):
        """Updates the text for the Circularity Score."""
        val = int(max(0, min(100, value)))
        self.circ_ring.setValue(val)
        self.circ_ring.setFormat(f"{val}%")
        
        # Change color based on circularity
        if val > 75:
            self.circ_ring.setStyleSheet("") # Default fluent green
        elif val > 40:
            self.circ_ring.setStyleSheet("qproperty-color: #E2B93B;") # Yellow
        else:
            self.circ_ring.setStyleSheet("qproperty-color: #FF5A5A;") # Red

    def update_resale_value(self, value: float):
        """Updates the text for the Est. Salvage Value."""
        if hasattr(self, 'resale_label'):
            self.resale_label.setText(f"€{value:,.2f}")