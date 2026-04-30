from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QFrame, QSizePolicy
from qfluentwidgets import SubtitleLabel, PrimaryPushButton, BodyLabel, TitleLabel, ComboBox, Theme, setTheme, FluentIcon

class AIStreamWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, stream_generator):
        super().__init__()
        self.stream_generator = stream_generator
        
    def run(self):
        try:
            for chunk in self.stream_generator:
                self.chunk_received.emit(chunk)
        except Exception as e:
            self.chunk_received.emit(f"\n**[Error]** {str(e)}")
        finally:
            self.finished.emit()

class AiStrategyWidget(QWidget):
    analyze_requested = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("AiStrategyWidget")
        setTheme(Theme.DARK)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # --- HEADER & CONTROLS ---
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("Campaign Orchestrator & ROI Analytics", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        self.region_selector = ComboBox(self)
        regions = ["Lombardia", "Lazio", "Campania", "Sicilia", "Veneto", "Emilia-Romagna", "Piemonte"]
        self.region_selector.addItems(sorted(regions))
        header_layout.addWidget(BodyLabel("Target Region:", self))
        header_layout.addWidget(self.region_selector)
        
        self.btn_analyze = PrimaryPushButton(FluentIcon.SEND, "Draft & Dispatch Campaign", self)
        self.btn_analyze.setStyleSheet("background: #5A32FA; border-color: #5A32FA;")
        self.btn_analyze.clicked.connect(self._on_analyze_clicked)
        header_layout.addWidget(self.btn_analyze)
        main_layout.addLayout(header_layout)

        # --- TWO COLUMN DASHBOARD ---
        dashboard_layout = QHBoxLayout()
        dashboard_layout.setSpacing(20)

        # LEFT COLUMN: The Smartphone Preview
        left_col = QVBoxLayout()
        phone_frame = QFrame(self)
        phone_frame.setStyleSheet("QFrame { background-color: #1e1e1e; border-radius: 20px; border: 4px solid #333; padding: 15px; }")
        phone_layout = QVBoxLayout(phone_frame)
        
        header = SubtitleLabel("📱Mobile App Preview", phone_frame)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phone_layout.addWidget(header)
        
        self.ai_terminal = QTextBrowser(self)
        self.ai_terminal.setStyleSheet("""
            QTextBrowser { background-color: #272727; color: #fff; font-size: 14px; border-radius: 10px; border: none; padding: 15px; }
        """)
        self.ai_terminal.setHtml("<div style='text-align: center; color: #777; margin-top: 50px;'>Awaiting AI Generation...</div>")
        phone_layout.addWidget(self.ai_terminal)
        left_col.addWidget(phone_frame)
        dashboard_layout.addLayout(left_col, stretch=1)

        # RIGHT COLUMN: Conversion Analytics
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        
        analytics_title = SubtitleLabel("📈 Post-Dispatch Conversion Funnel", self)
        right_col.addWidget(analytics_title)
        
        self.lbl_targeted = self._create_metric_card("Total Devices Targeted", "---", right_col)
        self.lbl_opened = self._create_metric_card("Notification Open Rate", "---", right_col)
        self.lbl_booked = self._create_metric_card("Repairs Booked (Network)", "---", right_col)
        self.lbl_roi = self._create_metric_card("Est. Claims Prevented (ROI)", "---", right_col)
        
        dashboard_layout.addLayout(right_col, stretch=1)
        main_layout.addLayout(dashboard_layout)

    def _create_metric_card(self, title, default_val, layout):
        card = QFrame(self)
        card.setStyleSheet("QFrame { background-color: #272727; border-radius: 10px; border: 1px solid #3a3a3a; padding: 15px; }")
        card_layout = QHBoxLayout(card)
        card_layout.addWidget(BodyLabel(title, card))
        card_layout.addStretch()
        val_label = TitleLabel(default_val, card)
        val_label.setStyleSheet("color: #00A67E; font-weight: bold;")
        card_layout.addWidget(val_label)
        layout.addWidget(card)
        return val_label

    def _on_analyze_clicked(self):
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Generating...")
        self.lbl_targeted.setText("---")
        self.lbl_opened.setText("---")
        self.lbl_booked.setText("---")
        self.lbl_roi.setText("---")
        
        selected_region = self.region_selector.currentText()
        self.analyze_requested.emit(selected_region)

    def prepare_ai_stream(self, region):
        self.ai_terminal.clear()

    def stream_ai_response(self, stream_generator):
        self.worker = AIStreamWorker(stream_generator)
        self.worker.chunk_received.connect(self._append_chunk)
        self.worker.finished.connect(self._on_stream_finished)
        self.worker.start()

    def _append_chunk(self, chunk):
        clean_chunk = chunk.replace('###', '<br><b style="color:#5A32FA;">>></b>').replace('**', '')
        self.ai_terminal.insertHtml(clean_chunk)
        scrollbar = self.ai_terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_stream_finished(self):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("Draft & Dispatch Campaign")
        
        # Wait 1.5 seconds to simulate real-world propagation, then fire the analytics!
        QTimer.singleShot(1500, self.trigger_mock_analytics)

    def trigger_mock_analytics(self):
        # We will mock the payload here purely for visual effect in the frontend
        # (In reality, the FleetController would pass the real payload)
        import random
        targeted = random.randint(8000, 15000)
        opened = int(targeted * random.uniform(0.35, 0.45))
        booked = int(opened * random.uniform(0.08, 0.12))
        roi = booked * random.uniform(2500, 4500)
        
        self.lbl_targeted.setText(f"{targeted:,}")
        self.lbl_opened.setText(f"{int((opened/targeted)*100)}%")
        self.lbl_booked.setText(f"{booked:,}")
        self.lbl_roi.setText(f"€{roi:,.0f}")