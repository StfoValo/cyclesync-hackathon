# Views Layer

This directory contains the user interface components of the CycleSync application, built using PyQt6 and the `qfluentwidgets` library to achieve a modern, premium aesthetic. It is strictly separated into modular sub-components.

## Current Architecture

The frontend is currently partitioned into dedicated UI flows and windows:

*   **`main_windows/`**:
    Houses the isolated, persona-specific main application shells.
    *   `main_window_user.py`: The Driver's specific UI with navigation items. It embeds a global ComboBox in the title bar allowing users to dynamically switch between multiple owned vehicles.
    *   `main_window_oem.py`: The Manufacturer's UI displaying Fleet Telemetry, Supply Chain Insights, and the "Define Car Model" (Birth Blueprint) form widget.
    *   `main_window_recycler.py`: The Recycler's UI featuring the Global Salvage Exchange dashboard.

*   **`Oem_widgets/`**:
    Contains specialized, modular components for the OEM dashboard.
    *   `car_model_form_widget.py`: A sleek, card-based form utilized by OEMs to define the base specifications and `car_type` for a new vehicle model.
    *   `blueprint_gallery_widget.py`: Displays cards for previously created car blueprints.
    *   `oem_blueprint_hub.py`: The container holding both the blueprint form and gallery.
    *   `fleet_telemetry_widget.py`: An interactive dashboard that visualizes global tracking. Its Folium map dynamically generates robust popups displaying vehicle breakdowns per model in each region.

*   **`registration/` (Wizard UI)**:
    A sub-module containing the views for the unified "Cached Login" onboarding process. It uses a `QStackedWidget` for seamless transitions.
    *   `wizard_view.py`: The main container for the wizard flow.
    *   `step1_role_view.py`: The UI for selecting the user persona (Driver, OEM, Recycler).
    *   `step2_cached_login_view.py`: A unified screen providing a 1-click mock "Cached Authentication" button, dramatically speeding up the hackathon pitch demo while fully supporting backend multi-tenant simulation.

*   **`Driver_widgets/`**:
    Contains specialized components for the car owner dashboard.
    *   `garage_widget.py`: The "My Garage" visual interface. Displays premium `QFrame` vehicle cards rendering car model imagery alongside dynamic telemetry data. Reacts to the global vehicle ComboBox selection.
    *   `tire_tracker_widget.py`: Visualizes 4-wheel live telemetry and executes the ported MATLAB predictive engine, rendering Circularity Scores, Safety Indices, and Est. Salvage Value.
    *   `tire_change_dialog.py`: A popup dialog allowing the driver to select and register a new set of tires from the OEM catalog, resetting telemetry.

*   **`Recycler_widgets/`**:
    Contains specialized components for the recycler dashboard.
    *   `recycler_hub.py`: The main container using a `QStackedWidget` to seamlessly transition between the macro market view and the specific AI analytics terminal.
    *   `global_exchange_widget.py`: The "Global Salvage Exchange" terminal. Displays a macro market view of salvageable materials.
    *   `material_analytics_widget.py`: The AI Terminal interface that displays the streamed market intelligence report and data for a specific material sector.
    *   `company_explorer_widget.py`: Widget shows geographical map. Map is interactive. Map uses Folium. User filters categories.
    *   `taxonomy_editor_widget.py`: Panel manages ecosystem. Panel defines taxonomy. Panel issues company passports. Passports include GPS coordinates.

## Future Roadmap

*   Expansion of the placeholder pages within `main_window_user.py` and `main_window_oem.py`.
*   Integration of AI-driven analysis directly inside the Global Salvage Exchange.
