from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from views.registration.step1_role_view import Step1RoleView
from views.registration.step2_cached_login_view import Step2CachedLoginView

class WizardView(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 500)
        self.setWindowTitle("CycleSync - Initialization")
        self.setStyleSheet("background-color: #1e1e1e;") 
        
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)
        
        # Instantiate our step views
        self.step1 = Step1RoleView()
        self.step2_login = Step2CachedLoginView()
        
        # Add them to the stack
        self.stack.addWidget(self.step1)
        self.stack.addWidget(self.step2_login)