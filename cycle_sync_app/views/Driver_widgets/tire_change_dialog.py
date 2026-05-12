from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout
from qfluentwidgets import MessageBoxBase, SubtitleLabel, ComboBox, BodyLabel

class TireChangeDialog(MessageBoxBase):
    def __init__(self, parent=None, blueprints=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Register New Tires', self)
        
        self.blueprints = blueprints or [] # List of tuples: (id, brand, model_name)
        
        # Setup UI
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(10)
        
        self.viewLayout.addWidget(BodyLabel("Select your new tire configuration below. This will reset your telemetry wear tracking to 100%.", self))
        self.viewLayout.addSpacing(15)

        self.tire_combo = ComboBox(self)
        self.tire_combo.setPlaceholderText("Select Tire Brand & Model")
        
        # Populate the dropdown
        for bp_id, brand, model in self.blueprints:
            self.tire_combo.addItem(f"{brand} - {model}", userData=bp_id)
            
        self.viewLayout.addWidget(self.tire_combo)
        
        self.widget.setMinimumWidth(350)

    def get_selected_blueprint_id(self):
        """Returns the database ID of the selected tire."""
        return self.tire_combo.currentData()