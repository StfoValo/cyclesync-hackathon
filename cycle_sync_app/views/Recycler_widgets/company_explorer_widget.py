import os
import io
import folium
from folium.plugins import MarkerCluster  # <-- NEW: Prevents marker clutter!
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from qfluentwidgets import SubtitleLabel, BodyLabel, ComboBox, Theme, setTheme
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

from models.data_manager.company_registry_manager import CompanyRegistryManager

class CompanyExplorerWidget(QWidget):
    """The interactive geographical map of the Motor Valley ecosystem."""
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("CompanyExplorerWidget") 
        setTheme(Theme.DARK)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15) 
        
        # --- TOP BAR: Title + Filter ---
        top_bar = QHBoxLayout()
        self.header = SubtitleLabel("Federated Ecosystem Map", self)
        top_bar.addWidget(self.header)
        top_bar.addStretch()
        
        # The Category Filter
        filter_label = BodyLabel("Filter by Category:", self)
        self.category_filter = ComboBox(self)
        self.category_filter.setMinimumWidth(200)
        self.category_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        top_bar.addWidget(filter_label)
        top_bar.addWidget(self.category_filter)
        self.layout.addLayout(top_bar)
        # -------------------------------
        
        self.web_view = QWebEngineView(self)
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        self.layout.addWidget(self.web_view, stretch=1)

    def showEvent(self, event):
        """Fires when the tab is opened. Refreshes filters and map."""
        super().showEvent(event)
        self.populate_filters()
        self.generate_and_load_map()

    def populate_filters(self):
        """Loads available categories from the database into the dropdown."""
        self.category_filter.blockSignals(True) # Prevent triggering the map reload while populating
        self.category_filter.clear()
        
        # Always add the "All" option first
        self.category_filter.addItem("All Categories", userData="All")
        
        nodes = CompanyRegistryManager.get_all_taxonomy_nodes()
        for node in nodes:
            self.category_filter.addItem(node['label'], userData=node['label'])
            
        self.category_filter.blockSignals(False)

    def on_filter_changed(self):
        """Triggered when the user selects a new category from the dropdown."""
        selected_category = self.category_filter.currentData()
        self.generate_and_load_map(selected_category)

    def generate_and_load_map(self, active_filter="All"):
        motor_valley_map = folium.Map(
            location=[44.6471, 10.9252], 
            zoom_start=9,
            tiles='CartoDB dark_matter' 
        )
        
        # CSS to brighten the dark map slightly
        lighten_css = """
        <style>
            .leaflet-tile-pane { filter: brightness(1.4) contrast(0.9); }
        </style>
        """
        motor_valley_map.get_root().header.add_child(folium.Element(lighten_css))
        
        # --- INITIALIZE MARKER CLUSTERING ---
        marker_cluster = MarkerCluster().add_to(motor_valley_map)
        
        companies = CompanyRegistryManager.get_registered_companies()
        
        for comp in companies:
            # Apply the Category Filter
            if active_filter != "All" and comp['type_label'] != active_filter:
                continue
                
            lat = comp.get('latitude', 0)
            lon = comp.get('longitude', 0)
            
            if lat == 0 and lon == 0:
                continue
                
            base_dir = os.path.abspath(os.path.join(os.getcwd(), 'cycle_sync_app', 'storage', 'logos'))
            logo_path = os.path.join(base_dir, comp['logo_path'])
            logo_url = f"file:///{logo_path.replace(os.sep, '/')}"
            
            html_popup = f"""
            <div style="width: 250px; font-family: 'Segoe UI', sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 15px; border-radius: 8px; border: 1px solid #00A67E;">
                <div style="text-align: center; margin-bottom: 10px;">
                    <img src="{logo_url}" width="80" style="border-radius: 5px;">
                </div>
                <h3 style="margin: 0 0 5px 0; color: white; text-align: center;">{comp['name']}</h3>
                <div style="text-align: center; color: #00A67E; font-weight: bold; font-size: 11px; margin-bottom: 10px;">
                    {comp['type_label'].upper()} • {comp['membership_tier'].upper()}
                </div>
                <p style="font-size: 12px; line-height: 1.4; color: #b0b0b0;">
                    {comp['description']}
                </p>
            </div>
            """
            
            # --- FIX: PERFECT CIRCULAR AVATARS ---
            # By setting the img to width/height 100%, object-fit: cover, and border-radius 50%,
            # the logo dynamically crops into a perfect circle filling the badge!
            icon_html = f"""
            <div style="
                width: 46px; 
                height: 46px; 
                background-color: #ffffff; 
                border: 2px solid #00A67E; 
                border-radius: 50%; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                box-shadow: 0px 4px 10px rgba(0, 166, 126, 0.4); 
                overflow: hidden;
            ">
                <img src="{logo_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
            </div>
            """
            custom_pin = folium.DivIcon(html=icon_html, icon_size=(46, 46), icon_anchor=(23, 23))
            
            # Note: We add the marker to the CLUSTER, not directly to the map!
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(html_popup, max_width=300),
                tooltip=comp['name'],
                icon=custom_pin
            ).add_to(marker_cluster)
            
        data = io.BytesIO()
        motor_valley_map.save(data, close_file=False)
        html_content = data.getvalue().decode()
        
        base_url = QUrl.fromLocalFile(os.path.abspath(os.getcwd()) + os.sep)
        self.web_view.setHtml(html_content, baseUrl=base_url)