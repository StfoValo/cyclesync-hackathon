# Models Layer

This directory acts as the data and logic backend for the CycleSync application. To ensure a robust, production-ready prototype for the hackathon, we utilize a localized SQLite database (`cyclesync.db`).

## Current Architecture

The backend currently consists of the following components:

*   **`data_manager/`**:
    *   **`database_manager.py`**: The core initialization and connection manager. It creates the schema for `accounts`, `car_models` (Birth Blueprints with powertrain/drivetrain), `vehicles`, and `components`. It drops legacy hardcoded defaults, enabling dynamic multi-tenant fleet creation and custom blueprint uploads.
    *   **`tire_manager.py`**: A specialized utility that initializes the tire catalog (e.g., Michelin, Pirelli) upon startup and safely mounts an initial set of tires to the baseline dummy vehicle.
    *   **`market_cache_manager.py`**: Acts as a local cache for the live data scraped by the ETL pipeline. It manages the storage and retrieval of real-world RSS feed context for the AI Agent.
    *   **`company_registry_manager.py`**: Manager handles company registry. Manager creates SQLite tables. Tables store taxonomy nodes. Tables store company passports. Passports include GPS coordinates. Passports include memberships.

*   **`auth_model.py`**:
    Handles multi-tenant authentication logic. It supports creating full accounts as well as a `mock_cached_login` mechanism that fetches the correct dummy `account_id` and `username` depending on the role selected in the UI.

*   **`oem_models/`**:
    *   **`oem_model.py`**: Manages data specific to the Manufacturer (OEM). Currently features `create_car_model`, securely storing structural details like `base_price`, `manufacture_cost`, `car_type`, `powertrain`, and `drivetrain`.
    *   **`fleet_model.py`**: Handles global Monte Carlo tracking of simulated physical vehicles. It iterates through all owned models across predefined global regions to deliver comprehensive spatial and model-based KPIs.

*   **`driver_models/`**:
    *   **`vehicle_model.py`**: Handles data retrieval for the Driver perspective. Performs SQL JOINs across `vehicles`, `car_models`, and `vehicle_telemetry` to extract real-time vehicle specifications (powertrain, weight, pricing) and live tracking metrics.
    *   **`tire_model.py`**: Implements an advanced, non-linear tire wear algorithm ported directly from MATLAB. It processes mass, drivetrain, and powertrain data to calculate safety indices, circularity scores, and AI salvage matching.

*   **`telemetry_simulation/`**:
    *   **`trip_simulator.py`**: A dedicated utility to simulate live IoT data. It pseudo-randomly updates the `vehicle_telemetry` table (e.g., advancing the odometer, fluctuating the eco-driving score) to demonstrate real-time reactivity in the driver dashboard without needing physical hardware.

*   **`recycler_models/`**:
    *   **`macro_market_model.py`**: Simulates Recycler Data. Retrieves aggregate big data from the `global_salvage_pool` table to display marketplace statistics and valuations for end-of-life components.

## Future Roadmap

*   Enhancement of the `macro_market_model.py` to support real-time transaction simulations and dynamic AI matching.
