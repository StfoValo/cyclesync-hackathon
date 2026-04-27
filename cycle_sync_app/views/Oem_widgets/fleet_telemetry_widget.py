import os
import io
import folium
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from qfluentwidgets import SubtitleLabel, PrimaryPushButton, Theme, setTheme, SegmentedWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class FleetTelemetryWidget(QWidget):
    simulate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("FleetTelemetryWidget")
        setTheme(Theme.DARK)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # --- TOP BAR: Title & Toggle ---
        top_bar = QHBoxLayout()
        self.header = SubtitleLabel("Global Operating System", self)
        top_bar.addWidget(self.header)
        top_bar.addStretch()
        
        # The View Toggle
        self.view_toggle = SegmentedWidget(self)
        self.view_toggle.addItem(routeKey='fleet', text='Live Fleet Telemetry')
        self.view_toggle.addItem(routeKey='suppliers', text='Supplier Network')
        self.view_toggle.setCurrentItem('fleet')

        top_bar.addWidget(self.view_toggle)
        top_bar.addStretch()
        
        self.btn_simulate = PrimaryPushButton("Generate Regional Fleet", self)
        self.btn_simulate.clicked.connect(self.simulate_requested.emit)
        top_bar.addWidget(self.btn_simulate)
        self.layout.addLayout(top_bar)
        
        # --- MAP CONTAINER ---
        self.web_view = QWebEngineView(self)
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.layout.addWidget(self.web_view, stretch=1)

    def render_map(self, regional_kpis, suppliers, active_view):
        """Builds the interactive map based on the active toggle."""
        fleet_map = folium.Map(location=[46.5, 9.5], zoom_start=4, tiles='CartoDB dark_matter')
        css = "<style>.leaflet-tile-pane { filter: brightness(1.2) contrast(0.9); }</style>"
        fleet_map.get_root().header.add_child(folium.Element(css))

        if active_view == 'fleet':
            # --- RENDER FLEET ---
            for r in regional_kpis:
                if r['center_lat'] is None or r['center_lon'] is None:
                    continue
                
                # Dynamically build the HTML for the car models breakdown
                models_html = ""
                for model_name, count in r.get('models_breakdown', {}).items():
                    models_html += f"""
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; color: #ccc;">
                        <span>↳ {model_name}:</span><span style="color: #00A67E; font-weight: bold;">{count:,}</span>
                    </div>
                    """
                
                html_popup = f"""
                <div style="width: 260px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 12px; border-radius: 8px;">
                    <h3 style="margin: 0 0 10px 0; color: white; border-bottom: 1px solid #555; padding-bottom: 5px;">📍 {r['region_name']}</h3>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Total Active Fleet:</span><span style="color: white; font-weight: bold;">{r['total_cars']:,}</span>
                    </div>
                    
                    <div style="background-color: #1a1a1a; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                        {models_html}
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Avg Odometer:</span><span style="color: white; font-weight: bold;">{r['avg_km']:,.0f} km</span>
                    </div>
                </div>
                """
                
                radius_size = min(35, max(15, r['total_cars'] / 350))
                folium.CircleMarker(
                    location=[r['center_lat'], r['center_lon']],
                    radius=radius_size,
                    popup=folium.Popup(html_popup, max_width=320),
                    color="#00A67E", fill=True, fill_color="#00A67E", fill_opacity=0.6, weight=2
                ).add_to(fleet_map)
                
        elif active_view == 'suppliers':
            # --- RENDER SUPPLIERS ---
            for sup in suppliers:
                icon_color = "orange" if "Assembly" in sup['type'] else "blue"
                icon_type = "wrench" if "Assembly" in sup['type'] else "industry"
                
                html_popup = f"""
                <div style="width: 220px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 10px; border-radius: 8px; border: 1px solid {icon_color};">
                    <h3 style="margin: 0 0 5px 0; color: white;">🏭 {sup['name']}</h3>
                    <div style="color: {icon_color}; font-weight: bold; margin-bottom: 10px;">{sup['type']}</div>
                    <div style="font-size: 12px; color: #bbb;">Region: {sup['region']}</div>
                </div>
                """
                
                folium.Marker(
                    location=[sup['lat'], sup['lon']],
                    popup=folium.Popup(html_popup, max_width=250),
                    icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
                ).add_to(fleet_map)

        data = io.BytesIO()
        fleet_map.save(data, close_file=False)
        html_content = data.getvalue().decode()
        
        base_url = QUrl.fromLocalFile(os.path.abspath(os.getcwd()) + os.sep)
        self.web_view.setHtml(html_content, baseUrl=base_url)