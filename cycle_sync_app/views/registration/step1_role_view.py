from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from qfluentwidgets import SubtitleLabel, PrimaryPushButton

class Step1RoleView(QWidget):
    # This signal tells the controller which path the user chose
    role_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = SubtitleLabel("Welcome to CycleSync. Who are you?", self)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        
        button_layout = QHBoxLayout()
        
        # We use PrimaryPushButton for a modern, elevated look
        self.btn_driver = PrimaryPushButton("🚗 Vehicle Owner", self)
        self.btn_oem = PrimaryPushButton("🏭 Manufacturer (OEM)", self)
        self.btn_recycler = PrimaryPushButton("♻️ Certified Recycler", self)
        
        # Connect buttons to emit our custom signal
        self.btn_driver.clicked.connect(lambda: self.role_selected.emit("DRIVER"))
        self.btn_oem.clicked.connect(lambda: self.role_selected.emit("OEM"))
        self.btn_recycler.clicked.connect(lambda: self.role_selected.emit("RECYCLER"))
        
        button_layout.addWidget(self.btn_driver)
        button_layout.addWidget(self.btn_oem)
        button_layout.addWidget(self.btn_recycler)
        
        layout.addLayout(button_layout)