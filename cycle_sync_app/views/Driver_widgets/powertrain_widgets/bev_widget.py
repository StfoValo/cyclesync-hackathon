from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (SubtitleLabel, BodyLabel, TitleLabel, 
                            PrimaryPushButton, SmoothScrollArea, ProgressRing)

import pyqtgraph as pg

class BEVWidget(QWidget):
    simulate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("BEVWidget")
        
        # Global PyQtGraph Settings for Bloomberg-style dark theme
        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#aaaaaa')
        pg.setConfigOptions(antialias=True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("Battery Health & EOL Predictor", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        self.btn_simulate = PrimaryPushButton("Simulate +25 Charge Cycles", self)
        self.btn_simulate.clicked.connect(self.simulate_requested.emit)
        header_layout.addWidget(self.btn_simulate)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(20)
        
        self._build_telemetry_card()
        self._build_kpi_dashboard()
        self._build_projection_plot() # THE NEW GRAPH
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def _create_card(self):
        card = QFrame(self)
        card.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; }")
        return card

    def _build_telemetry_card(self):
        self.tel_card = self._create_card()
        layout = QHBoxLayout(self.tel_card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text_layout = QVBoxLayout()
        self.vehicle_name_label = TitleLabel("Vehicle Name", self.tel_card)
        self.vehicle_name_label.setStyleSheet("color: #4CAF50;") 
        
        self.odo_label = BodyLabel("Odometer: -- km", self.tel_card)
        self.range_label = SubtitleLabel("Est. Real Range: -- km", self.tel_card)
        self.range_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        
        text_layout.addWidget(self.vehicle_name_label)
        text_layout.addWidget(self.odo_label)
        text_layout.addSpacing(10)
        text_layout.addWidget(self.range_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        ring_layout = QVBoxLayout()
        self.soh_ring = ProgressRing(self.tel_card)
        self.soh_ring.setFixedSize(120, 120)
        self.soh_ring.setStrokeWidth(12)
        self.soh_ring.setTextVisible(True)
        ring_layout.addWidget(BodyLabel("State of Health (SoH)", self.tel_card), alignment=Qt.AlignmentFlag.AlignCenter)
        ring_layout.addWidget(self.soh_ring, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(ring_layout)
        self.layout.addWidget(self.tel_card)

    def _build_kpi_dashboard(self):
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        sl_card = self._create_card()
        s_layout = QVBoxLayout(sl_card)
        s_layout.addWidget(BodyLabel("Stationary Storage Potential", sl_card), alignment=Qt.AlignmentFlag.AlignHCenter)
        self.sl_label = TitleLabel("-- / 100", sl_card)
        self.sl_label.setStyleSheet("color: #2196F3;")
        s_layout.addWidget(self.sl_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        kpi_layout.addWidget(sl_card)

        circ_card = self._create_card()
        c_layout = QVBoxLayout(circ_card)
        c_layout.addWidget(BodyLabel("Circularity Score", circ_card), alignment=Qt.AlignmentFlag.AlignHCenter)
        self.circ_label = TitleLabel("-- / 100", circ_card)
        self.circ_label.setStyleSheet("color: #00A67E;")
        c_layout.addWidget(self.circ_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        kpi_layout.addWidget(circ_card)

        resale_card = self._create_card()
        r_layout = QVBoxLayout(resale_card)
        r_layout.addWidget(BodyLabel("Est. Lithium Salvage Value", resale_card), alignment=Qt.AlignmentFlag.AlignHCenter)
        self.resale_label = TitleLabel("€ 0.00", resale_card)
        self.resale_label.setStyleSheet("color: #FF9800;")
        r_layout.addWidget(self.resale_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        kpi_layout.addWidget(resale_card)

        self.layout.addLayout(kpi_layout)

    def _build_projection_plot(self):
        """Constructs the PyQtGraph widget."""
        self.plot_card = self._create_card()
        p_layout = QVBoxLayout(self.plot_card)
        p_layout.setContentsMargins(20, 20, 20, 20)
        
        p_layout.addWidget(SubtitleLabel("Predictive End-of-Life (EOL) Trajectory", self.plot_card))
        p_layout.addSpacing(10)
        
        self.graph = pg.PlotWidget()
        self.graph.setFixedHeight(250)
        self.graph.showGrid(x=True, y=True, alpha=0.15)
        
        # --- THE FIX: Format axes for Odometer ---
        self.graph.setLabel('left', 'Real Range', units='km')
        self.graph.setLabel('bottom', 'Odometer', units='km') 
        # Optional: Format the X-axis numbers to look cleaner (e.g., 100k, 150k)
        self.graph.getAxis('bottom').enableAutoSIPrefix(False) 
        # -----------------------------------------
        
        self.range_curve = self.graph.plot(pen=pg.mkPen(color='#00A67E', width=3))
        
        self.eol_line = pg.InfiniteLine(angle=0, pen=pg.mkPen(color='#FF5A5A', width=2, style=Qt.PenStyle.DashLine))
        self.graph.addItem(self.eol_line)
        
        p_layout.addWidget(self.graph)
        self.layout.addWidget(self.plot_card)

    def update_dashboard(self, model_name, odo, soh, range_real, sl_score, circ_score, resale, eol_range, projection):
        self.vehicle_name_label.setText(model_name)
        self.odo_label.setText(f"Odometer: {odo:,.0f} km")
        self.range_label.setText(f"Est. Real Range: {range_real:.0f} km")
        
        # Removed the faulty setStyleSheet color logic here!
        val = int(max(0, min(100, soh)))
        self.soh_ring.setValue(val)
        self.soh_ring.setFormat(f"{soh:.1f}%")
            
        self.sl_label.setText(f"{sl_score:.0f} / 100")
        self.circ_label.setText(f"{circ_score:.0f} / 100")
        self.resale_label.setText(f"€ {resale:,.2f}")
        
        # --- UPDATE THE PLOT ---
        if projection:
            x_vals = [p[0] for p in projection]
            y_vals = [p[1] for p in projection]
            self.range_curve.setData(x_vals, y_vals)
            self.eol_line.setPos(eol_range)