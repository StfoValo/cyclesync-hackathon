from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from views.Oem_widgets.blueprint_gallery_widget import BlueprintGalleryWidget
from views.Oem_widgets.car_model_form_widget import CarModelFormWidget

class OemBlueprintHub(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("OemBlueprintHub")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)
        
        self.gallery = BlueprintGalleryWidget(self)
        self.form = CarModelFormWidget(self)
        
        self.stacked_widget.addWidget(self.gallery) # Index 0
        self.stacked_widget.addWidget(self.form)    # Index 1
