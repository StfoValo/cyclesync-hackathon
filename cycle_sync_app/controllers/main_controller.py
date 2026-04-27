from PyQt6.QtCore import QObject, QPropertyAnimation, QEasingCurve
from controllers.wizard_controller import WizardController
from views.main_windows.main_window_user import MainWindowUser
from views.main_windows.main_window_oem import MainWindowOem # <-- Add Import
from views.main_windows.main_window_recycler import MainWindowRecycler

class MainController(QObject):
    # ... (__init__, run, transition_to_dashboard remain EXACTLY the same) ...
    def __init__(self):
        super().__init__()
        self.wizard_controller = WizardController()
        self.main_window = None 
        self.wizard_controller.wizard_completed.connect(self.transition_to_dashboard)

    def run(self):
        self.wizard_controller.show()

    def transition_to_dashboard(self, user_data):
        print(f"[MainController] Onboarding complete. Handing off data: {user_data}")
        role = user_data.get('role', 'DRIVER')
        account_id = user_data.get('account_id')
        username = user_data.get('username')
        self.switch_active_ui(role, account_id, username)
        self.wizard_controller.view.close()

    def switch_active_ui(self, new_role, account_id=None, username=None):
        print(f"[MainController] Switching UI to role: {new_role} for account: {account_id}, username: {username}")
        
        if self.main_window is not None:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None
            
        if new_role == "DRIVER":
            self.main_window = MainWindowUser(account_id=account_id, username=username)
            self.main_window.switch_role_requested.connect(lambda: self.switch_active_ui("OEM", account_id, username))
        
        elif new_role == "OEM":
            self.main_window = MainWindowOem(account_id=account_id) # <-- Hooked up the actual window!
            self.main_window.switch_role_requested.connect(lambda: self.switch_active_ui("RECYCLER", account_id, username))
        
        elif new_role == "RECYCLER":
            self.main_window = MainWindowRecycler(account_id=account_id, username=username)
            self.main_window.switch_role_requested.connect(lambda: self.switch_active_ui("DRIVER", account_id, username))
        else:
            self.main_window = MainWindowUser(account_id=account_id, username=username)

        self.main_window.setWindowOpacity(0.0) 
        self.main_window.show()
        
        self.fade_anim = QPropertyAnimation(self.main_window, b"windowOpacity")
        self.fade_anim.setDuration(1200) 
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_anim.start()