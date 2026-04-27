from PyQt6.QtCore import QObject, pyqtSignal
from views.registration.wizard_view import WizardView
from controllers.db_control.auth_controller import AuthController
from models.auth_model import AuthModel

class WizardController(QObject):
    wizard_completed = pyqtSignal(dict) 

    def __init__(self):
        super().__init__()
        self.view = WizardView()
        self.user_data = {}
        
        self.auth_model = AuthModel()
        self.auth_controller = AuthController(self.view.step2_login, self.auth_model)
        
        self._connect_signals()

    def _connect_signals(self):
        self.view.step1.role_selected.connect(self.handle_role_selection)
        self.auth_controller.auth_successful.connect(self.handle_auth_successful)

    def handle_role_selection(self, role):
        self.user_data['role'] = role
        print(f"[Wizard] User selected role: {role}")
        
        self.auth_controller.current_role = role
        self.view.step2_login.update_role_text(role)
        self.view.stack.setCurrentWidget(self.view.step2_login)

    def handle_auth_successful(self, auth_data):
        print(f"[Wizard] Auth successful: {auth_data}")
        self.user_data['account_id'] = auth_data['account_id']
        self.user_data['username'] = auth_data['username']
        self.finish_onboarding()

    def finish_onboarding(self):
        print("[Wizard] Onboarding complete. Emitting signal to MainController.")
        self.wizard_completed.emit(self.user_data)

    def show(self):
        self.view.show()