import os
import shutil
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QFileDialog
from qfluentwidgets import (SubtitleLabel, BodyLabel, LineEdit, SpinBox, DoubleSpinBox,
                            ComboBox, PrimaryPushButton, InfoBar, InfoBarPosition, TextEdit)
from models.data_manager.company_registry_manager import CompanyRegistryManager

class TaxonomyEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("TaxonomyEditorWidget")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.header = SubtitleLabel("Ecosystem Management Panel", self)
        main_layout.addWidget(self.header)
        
        split_layout = QHBoxLayout()
        
        # --- LEFT PANE: Define Taxonomy (Unchanged) ---
        self.left_pane = QFrame(self)
        self.left_pane.setStyleSheet("QFrame { background-color: #272727; border-radius: 10px; border: 1px solid #3a3a3a; }")
        left_layout = QVBoxLayout(self.left_pane)
        left_layout.addWidget(SubtitleLabel("1. Define Taxonomy Node", self.left_pane))
        
        self.tax_name_input = LineEdit(self.left_pane)
        self.tax_name_input.setPlaceholderText("Category Name...")
        left_layout.addWidget(self.tax_name_input)
        
        left_layout.addWidget(BodyLabel("Hierarchy Level:"))
        self.tax_level_input = SpinBox(self.left_pane)
        left_layout.addWidget(self.tax_level_input)
        
        self.btn_add_taxonomy = PrimaryPushButton("Create Category", self.left_pane)
        self.btn_add_taxonomy.clicked.connect(self.save_taxonomy_node)
        left_layout.addWidget(self.btn_add_taxonomy)
        left_layout.addStretch()
        
        # --- RIGHT PANE: Upgraded Company Passport ---
        self.right_pane = QFrame(self)
        self.right_pane.setStyleSheet("QFrame { background-color: #1e1e1e; border-radius: 10px; border: 1px solid #00A67E; }")
        right_layout = QVBoxLayout(self.right_pane)
        right_layout.addWidget(SubtitleLabel("2. Issue Company Passport", self.right_pane))
        
        # Basic Info
        self.comp_name_input = LineEdit(self.right_pane)
        self.comp_name_input.setPlaceholderText("Company Name (e.g., Ferrari)...")
        right_layout.addWidget(self.comp_name_input)
        
        self.logo_layout = QHBoxLayout()
        self.comp_logo_input = LineEdit(self.right_pane)
        self.comp_logo_input.setPlaceholderText("Select a logo image...")
        self.comp_logo_input.setReadOnly(True) 
        self.btn_browse_logo = PrimaryPushButton("Browse...", self.right_pane)
        self.btn_browse_logo.clicked.connect(self.browse_for_logo)
        self.logo_layout.addWidget(self.comp_logo_input)
        self.logo_layout.addWidget(self.btn_browse_logo)
        right_layout.addLayout(self.logo_layout)
        
        # NEW: Description
        self.comp_desc_input = TextEdit(self.right_pane)
        self.comp_desc_input.setPlaceholderText("Brief description of the company's role in the Motor Valley...")
        self.comp_desc_input.setMaximumHeight(80)
        right_layout.addWidget(self.comp_desc_input)
        
        # NEW: Coordinates (Centered on Modena by default)
        coord_layout = QHBoxLayout()
        self.lat_input = DoubleSpinBox(self.right_pane)
        self.lat_input.setRange(-90.0, 90.0)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(44.6471) # Modena Lat
        
        self.lon_input = DoubleSpinBox(self.right_pane)
        self.lon_input.setRange(-180.0, 180.0)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(10.9252) # Modena Lon
        
        coord_layout.addWidget(BodyLabel("Lat:"))
        coord_layout.addWidget(self.lat_input)
        coord_layout.addWidget(BodyLabel("Lon:"))
        coord_layout.addWidget(self.lon_input)
        right_layout.addLayout(coord_layout)
        
        # NEW: Memberships & Taxonomy
        dropdown_layout = QHBoxLayout()
        self.comp_category_combo = ComboBox(self.right_pane)
        
        self.membership_combo = ComboBox(self.right_pane)
        self.membership_combo.addItems(["Founding Member", "Ordinary Member", "Supporting Member"])
        
        dropdown_layout.addWidget(self.comp_category_combo)
        dropdown_layout.addWidget(self.membership_combo)
        right_layout.addLayout(dropdown_layout)
        
        self.btn_add_company = PrimaryPushButton("Issue Digital Passport", self.right_pane)
        self.btn_add_company.clicked.connect(self.save_company)
        right_layout.addWidget(self.btn_add_company)
        
        split_layout.addWidget(self.left_pane)
        split_layout.addWidget(self.right_pane)
        main_layout.addLayout(split_layout)
        
        self.refresh_combo_box()

    def browse_for_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.comp_logo_input.setText(file_path)

    def refresh_combo_box(self):
        self.comp_category_combo.clear()
        for node in CompanyRegistryManager.get_all_taxonomy_nodes():
            self.comp_category_combo.addItem(f"{node['label']} (Level {node['level']})", userData=node['id'])

    def save_taxonomy_node(self):
        name = self.tax_name_input.text()
        level = self.tax_level_input.value()
        if name:
            CompanyRegistryManager.add_taxonomy_node(name, level)
            InfoBar.success("Success", f"Taxonomy Category '{name}' created.", parent=self, position=InfoBarPosition.TOP)
            self.tax_name_input.clear()
            self.refresh_combo_box()

    def save_company(self):
        name = self.comp_name_input.text()
        source_logo_path = self.comp_logo_input.text()
        type_id = self.comp_category_combo.currentData()
        desc = self.comp_desc_input.toPlainText()
        lat = self.lat_input.value()
        lon = self.lon_input.value()
        tier = self.membership_combo.currentText()
        
        if name and source_logo_path and type_id:
            try:
                filename = os.path.basename(source_logo_path)
                dest_dir = os.path.join("cycle_sync_app", "storage", "logos")
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, filename)
                
                if os.path.abspath(source_logo_path) != os.path.abspath(dest_path):
                    shutil.copy2(source_logo_path, dest_path)
                    
                CompanyRegistryManager.register_company(
                    name=name, logo_path=filename, type_node_id=type_id,
                    description=desc, latitude=lat, longitude=lon, membership_tier=tier
                )
                InfoBar.success("Success", f"Passport issued for '{name}'.", parent=self, position=InfoBarPosition.TOP)
                
                self.comp_name_input.clear()
                self.comp_logo_input.clear()
                self.comp_desc_input.clear()
                
            except Exception as e:
                InfoBar.error("Error", f"Could not save: {str(e)}", parent=self, position=InfoBarPosition.TOP)
        else:
            InfoBar.warning("Missing Info", "Name, Logo, and Category are required.", parent=self, position=InfoBarPosition.TOP)