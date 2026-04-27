# Controllers Layer

This directory contains the business logic and orchestration for the CycleSync application. The controllers act as the intermediaries between the `views` (frontend/UI) and the `models` (backend/data). We enforce a strict MVC architecture.

## Current Architecture

Currently, the following controllers and sub-modules have been implemented:

*   **`main_controller.py`**: 
    The core orchestrator (Router) of the application. It initializes the onboarding wizard and, upon completion, dynamically routes to the correct main dashboard (`MainWindowUser`, `MainWindowOem`, etc.) based on the user's role. It features a seamless `QPropertyAnimation` fade-in effect and handles "Judge Mode" UI switching.
    
*   **`wizard_controller.py`**: 
    Manages the logic and state of the user registration and cached login process. It interfaces directly with the `WizardView` and the `AuthController`.

*   **`db_control/`**: A sub-module for specialized controllers interacting with the database backend.
    *   **`auth_controller.py`**: Bridges the unified cached login view to the `AuthModel`. It processes the login requests and securely passes the authenticated data downstream.
    *   **`oem_controllers/`**: A sub-module for OEM specific logic.
        *   **`oem_blueprint_controller.py`**: Links the OEM form widget to the `OEMModel` to parse and safely validate data before inserting new "Birth Blueprints" into the SQLite database, subsequently triggering interactive UI `InfoBar` notifications.
        *   **`fleet_controller.py`**: Interacts with the `FleetModel` to retrieve real-time production numbers and tracking data. It now manages dynamic Monte Carlo simulation across all vehicle models and regions, passing aggregated multi-model KPIs seamlessly to the `FleetTelemetryWidget`.
    *   **`driver_controllers/`**: A sub-module for Driver specific logic.
        *   **`garage_controller.py`**: Coordinates the Driver's "My Garage" dashboard. It listens to the global vehicle ComboBox to dynamically switch active VINs. Joins physical vehicle registry data (VIN) with OEM birth blueprints (Model, Photo) and live telemetry.
        *   **`tire_controller.py`**: Orchestrates tire lifecycle tracking using a sophisticated predictive wear algorithm. It passes dynamic vehicle attributes (powertrain, drivetrain, mass) to calculate safety indices, circularity scores, and resale values, reacting globally to VIN changes.
    *   **`recycler_controllers/`**: A sub-module for Recycler specific logic.
        *   **`exchange_controller.py`**: Links the `MacroMarketModel` to the `GlobalExchangeWidget` to present high-level salvage market data to the recycler terminal.
        *   **`analytics_controller.py`**: Orchestrates the UI transitions within the `RecyclerHub`. It runs a background `QThread` (`AgentWorker`) that triggers the `MotorValleyAgent` and streams the generative AI text directly to the `MaterialAnalyticsWidget` terminal.

## Future Roadmap

Based on the application architecture outlined in the ideas:
*   `ai_controller.py`: The AI-driven middleman that calculates predictive valuations and matches components for the recycling marketplace.
