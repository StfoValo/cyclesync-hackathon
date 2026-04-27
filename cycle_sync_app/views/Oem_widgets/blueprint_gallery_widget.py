from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap
from qfluentwidgets import SmoothScrollArea, FlowLayout, SubtitleLabel, PrimaryPushButton, BodyLabel, CaptionLabel, ComboBox, Theme, setTheme
import os

class BlueprintGalleryWidget(QWidget):
    create_requested = pyqtSignal()
    filter_changed = pyqtSignal(str) # Emitted when the user changes the category filter

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("BlueprintGalleryWidget")
        setTheme(Theme.DARK)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15) 
        
        # --- TOP BAR: Title, Filter, & Create Button ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        self.title = SubtitleLabel("Blueprint Management Hub", self)
        self.title.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        top_bar.addWidget(self.title)
        top_bar.addStretch(1)
        
        # Category Filter (New Location for professional look)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)
        self.filter_label = BodyLabel("Filter by Category:", self)
        self.filter_label.setStyleSheet("color: #aaaaaa;")
        self.category_filter = ComboBox(self)
        self.category_filter.setMinimumWidth(200)
        self.category_filter.currentIndexChanged.connect(self._on_filter_index_changed)
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.category_filter)
        
        top_bar.addLayout(filter_layout)
        top_bar.addSpacing(20)
        
        self.btn_create = PrimaryPushButton("+ Define New Blueprint", self)
        self.btn_create.setStyleSheet("""
            PrimaryPushButton {
                background: #00A67E; 
                border-color: #00A67E; 
                font-weight: bold;
                padding: 10px 20px;
            }
            PrimaryPushButton:hover {
                background: #008f6c;
                border-color: #008f6c;
            }
        """)
        self.btn_create.clicked.connect(self.create_requested.emit)
        top_bar.addWidget(self.btn_create)
        main_layout.addLayout(top_bar)
        
        # --- MAIN SCROLL CONTENT (Optimized Flow) ---
        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # The main container holding the FlowLayout
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        
        # This is the critical change: Use ONE main FlowLayout for ALL cards.
        self.flowLayout = FlowLayout(self.container, needAni=True)
        self.flowLayout.setContentsMargins(0, 10, 0, 0)
        self.flowLayout.setSpacing(20) # Consistent spacing between all cards
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area, stretch=1)

    def populate_filters(self, categories: list):
        """Refreshes the filter ComboBox with available categories."""
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", userData="All")
        for cat in categories:
            self.category_filter.addItem(cat.title(), userData=cat)
        self.category_filter.blockSignals(False)

    def _on_filter_index_changed(self):
        selected_data = self.category_filter.currentData()
        self.filter_changed.emit(selected_data)

    def render_cards(self, models_data: list, active_filter: str = "All"):
        """Populates the single, efficient FlowLayout with dynamic, filterable cards."""
        # 1. Efficiently clear all existing cards
        self.flowLayout.removeAllWidgets()
        
        # 2. Build the new cards (respecting the filter)
        for model in models_data:
            # Column mapping matches the oem_model.py order updated in previous steps
            id_db, model_name, base_price, manufacture_cost, car_type, powertrain, drivetrain, image_path = model
            
            # Apply the view-side filter (if not "All")
            if active_filter != "All" and car_type != active_filter:
                continue
            
            # --- CARD DEFINITION ---
            card = QFrame(self.container)
            card.setFixedSize(240, 310)
            card.setStyleSheet("""
                QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; padding: 10px; }
                QFrame:hover { border: 2px solid #00A67E; background-color: #333333; }
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # Image (Scaled to fill nicely)
            img_label = QLabel(card)
            img_label.setFixedSize(200, 130)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(img_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(scaled_pixmap)
            else:
                # Premium "missing image" placeholder
                img_label.setText("DIGITAL TWIN PENDING")
                img_label.setStyleSheet("""
                    QLabel { 
                        color: #555555; 
                        border: 2px dashed #444444; 
                        border-radius: 8px; 
                        font-family: 'Segoe UI', sans-serif; 
                        font-size: 10px;
                        font-weight: bold;
                    }
                """)
            card_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            card_layout.addSpacing(10)
            
            # Model Name & Price
            name_label = BodyLabel(model_name, card)
            name_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px; border: none; background: transparent;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name_label)
            
            # Pricing (High Contrast Circular Economy indicator)
            price_label = CaptionLabel(f"Market Value: €{base_price:,.2f}", card)
            price_label.setStyleSheet("color: #00A67E; font-size: 13px; border: none; background: transparent; font-weight: bold;")
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(price_label)
            
            # Material/Type Badge (Utilization indicator)
            mat_label = CaptionLabel(f"Chassis: {car_type.upper()}", card)
            mat_label.setStyleSheet("color: #aaaaaa; font-size: 11px; border: none; background: transparent; letter-spacing: 1px;")
            mat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(mat_label)
            
            card_layout.addSpacing(10)
            
            # --- NEW: Aggressive Classification Badges (From Step 18) ---
            badge_layout = QHBoxLayout()
            badge_layout.setSpacing(5)
            badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Powertrain Badge
            pt_color = "#4CAF50" if powertrain == "BEV" else "#2196F3"
            pt_badge = QLabel(powertrain, card)
            pt_badge.setStyleSheet(f"""
                QLabel {{
                    color: {pt_color}; 
                    border: 1px solid {pt_color}; 
                    border-radius: 4px; 
                    padding: 3px 8px; 
                    font-weight: bold; 
                    font-size: 10px; 
                    letter-spacing: 1px;
                }}
            """)
            
            # Drivetrain Badge
            dt_badge = QLabel(drivetrain, card)
            dt_badge.setStyleSheet("""
                QLabel {
                    color: #FF9800; 
                    border: 1px solid #FF9800; 
                    border-radius: 4px; 
                    padding: 3px 8px; 
                    font-weight: bold; 
                    font-size: 10px;
                    letter-spacing: 1px;
                }
            """)
            
            badge_layout.addWidget(pt_badge)
            badge_layout.addWidget(dt_badge)
            card_layout.addLayout(badge_layout)
            
            # Final touch: Add card to the main flowLayout
            self.flowLayout.addWidget(card)