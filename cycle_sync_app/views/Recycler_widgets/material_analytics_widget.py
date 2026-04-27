from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QTextBrowser
from qfluentwidgets import SubtitleLabel, TitleLabel, BodyLabel, PrimaryPushButton, TransparentToolButton, FluentIcon


class MaterialAnalyticsWidget(QWidget):
    # Signal to go back to the macro view
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("MaterialAnalyticsWidget")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- TOP BAR ---
        top_bar = QHBoxLayout()
        self.btn_back = TransparentToolButton(FluentIcon.RETURN, self)
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.title_label = SubtitleLabel("Material Analytics Terminal", self)
        
        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        main_layout.addSpacing(20)
        
        # --- SPLIT SCREEN LAYOUT ---
        split_layout = QHBoxLayout()
        
        # LEFT PANE: Data Engine (40%)
        self.left_pane = QFrame(self)
        self.left_pane.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; }")
        left_layout = QVBoxLayout(self.left_pane)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        self.sector_label = TitleLabel("SECTOR", self.left_pane)
        self.sector_label.setStyleSheet("color: #00A67E;")
        
        self.volume_label = BodyLabel("Available Volume: -- Tons", self.left_pane)
        self.value_label = BodyLabel("Est. Salvage Value: €--", self.left_pane)
        self.market_label = BodyLabel("Global Index Price: Scraping...", self.left_pane)
        
        left_layout.addWidget(self.sector_label)
        left_layout.addSpacing(15)
        left_layout.addWidget(SubtitleLabel("Internal Platform Data:", self.left_pane))
        left_layout.addWidget(self.volume_label)
        left_layout.addWidget(self.value_label)
        left_layout.addSpacing(15)
        left_layout.addWidget(SubtitleLabel("External Market Data:", self.left_pane))
        left_layout.addWidget(self.market_label)
        left_layout.addStretch()
        
        # RIGHT PANE: AI Terminal (60%)
        self.right_pane = QFrame(self)
        self.right_pane.setStyleSheet("QFrame { background-color: #1e1e1e; border-radius: 12px; border: 1px solid #00A67E; }")
        right_layout = QVBoxLayout(self.right_pane)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        ai_header = SubtitleLabel("CycleSync AI Synthesis", self.right_pane)
        ai_header.setStyleSheet("color: #00A67E;")
        right_layout.addWidget(ai_header)
        
        self.ai_terminal = QTextBrowser(self.right_pane)
        self.ai_terminal.setOpenExternalLinks(True) # Makes the scraped URLs clickable!
        self.ai_terminal.setReadOnly(True)
        self.ai_terminal.setStyleSheet("""
            QTextBrowser { 
                background-color: transparent; 
                color: #E0E0E0; 
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif; 
                font-size: 15px; 
                border: none;
            }
        """)
        self.ai_terminal.setMarkdown("> Awaiting Market Data...")
        right_layout.addWidget(self.ai_terminal)
        
        self.btn_action = PrimaryPushButton("Draft Acquisition Bid", self.right_pane)
        self.btn_action.hide() # Hidden until AI finishes
        right_layout.addWidget(self.btn_action)
        
        # Apply the 40/60 Split
        split_layout.addWidget(self.left_pane, 4)
        split_layout.addWidget(self.right_pane, 6)
        
        main_layout.addLayout(split_layout)

    def populate_data(self, sector, volume, value, market_price):
        self.sector_label.setText(str(sector).upper())
        self.volume_label.setText(f"Available Volume: {volume:,.1f} Tons")
        self.value_label.setText(f"Est. Salvage Value: €{value:,.2f}")
        self.market_label.setText(f"Global Index Price: €{market_price:,.2f} / Ton")
        self.ai_terminal.setText("> Establishing secure connection to AI Core...\n> Synthesizing global supply chain matrices...\n> Please wait...")
        self.btn_action.hide()