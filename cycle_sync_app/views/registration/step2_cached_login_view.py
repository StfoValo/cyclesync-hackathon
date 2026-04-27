from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import PrimaryPushButton, SubtitleLabel, LineEdit, PasswordLineEdit

class Step2CachedLoginView(QWidget):
    # Emits (username, password)
    login_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle = SubtitleLabel("Register / Login to Profile", self)
        layout.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addSpacing(20)
        
        self.username_input = LineEdit(self)
        self.username_input.setPlaceholderText("Username (Leave empty for Judge mode)")
        self.username_input.setFixedSize(300, 40)
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addSpacing(10)
        
        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFixedSize(300, 40)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addSpacing(20)
        
        self.login_btn = PrimaryPushButton("Access App / Save Profile", self)
        self.login_btn.setFixedSize(300, 40)
        self.login_btn.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.login_requested.emit(username, password)
        
    def update_role_text(self, role: str):
        self.subtitle.setText(f"Set up or Access {role} Profile")
