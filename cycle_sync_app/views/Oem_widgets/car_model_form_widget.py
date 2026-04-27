import os
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap
from qfluentwidgets import LineEdit, DoubleSpinBox, PrimaryPushButton, SubtitleLabel, BodyLabel, FluentIcon, PushButton, ComboBox

class CarModelFormWidget(QWidget):
    form_submitted = pyqtSignal(dict)
    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("CarModelFormWidget")
        self.selected_image_path = ""
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        self.card = QFrame(self)
        self.card.setFixedWidth(750) 
        self.card.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; }")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        
        self.title = SubtitleLabel("Define New Car Blueprint", self.card)
        card_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        content_layout = QHBoxLayout()
        card_layout.addLayout(content_layout)
        
        # --- LEFT COLUMN (Form) ---
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(18)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.model_name_input = LineEdit(self.card)
        self.base_price_input = DoubleSpinBox(self.card)
        self.base_price_input.setMaximum(1000000.0)
        self.manufacture_cost_input = DoubleSpinBox(self.card)
        self.manufacture_cost_input.setMaximum(1000000.0)
        
        self.car_type_combo = ComboBox(self.card)
        self.car_type_combo.addItems(["utilitarian", "sedan", "SUV", "sportscar"])
        
        self.powertrain_combo = ComboBox(self.card)
        self.powertrain_combo.addItems(["ICE", "BEV", "HEV"])
        
        self.drivetrain_combo = ComboBox(self.card)
        self.drivetrain_combo.addItems(["FWD", "RWD", "AWD"])
        
        form_layout.addRow(BodyLabel("Model Name:", self.card), self.model_name_input)
        form_layout.addRow(BodyLabel("Base Price (€):", self.card), self.base_price_input)
        form_layout.addRow(BodyLabel("Manufacture Cost (€):", self.card), self.manufacture_cost_input)
        form_layout.addRow(BodyLabel("Car Type:", self.card), self.car_type_combo)
        form_layout.addRow(BodyLabel("Powertrain:", self.card), self.powertrain_combo)
        form_layout.addRow(BodyLabel("Drivetrain:", self.card), self.drivetrain_combo)
        
        content_layout.addLayout(form_layout)
        
        # --- RIGHT COLUMN (Image Preview) ---
        image_layout = QVBoxLayout()
        image_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.image_preview = QLabel("No Image Selected", self.card)
        self.image_preview.setFixedSize(200, 150)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("QLabel { border: 2px dashed #555; border-radius: 8px; color: #aaa; }")
        image_layout.addWidget(self.image_preview)
        image_layout.addSpacing(10)
        
        self.btn_select_image = PushButton(FluentIcon.PHOTO, "Select Photo", self.card)
        self.btn_select_image.clicked.connect(self._on_select_image)
        image_layout.addWidget(self.btn_select_image, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        content_layout.addLayout(image_layout)
        
        # --- SUBMIT BUTTONS ---
        self.submit_btn = PrimaryPushButton(FluentIcon.ADD, "Save Blueprint", self.card)
        self.submit_btn.clicked.connect(self._on_submit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        self.btn_cancel = PushButton("Cancel", self.card)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.submit_btn)
        
        card_layout.addLayout(btn_layout)
        main_layout.addWidget(self.card)

    def _on_select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Car Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def reset_image(self):
        self.selected_image_path = ""
        self.image_preview.clear()
        self.image_preview.setText("No Image Selected")

    def _on_submit(self):
        data = {
            "model_name": self.model_name_input.text(),
            "base_price": self.base_price_input.value(),
            "manufacture_cost": self.manufacture_cost_input.value(),
            "car_type": self.car_type_combo.currentText(),
            "powertrain": self.powertrain_combo.currentText(),
            "drivetrain": self.drivetrain_combo.currentText(),
            "image_path": self.selected_image_path
        }
        self.form_submitted.emit(data)