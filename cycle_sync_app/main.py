import sys
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme  # <-- 1. Import the theme tools here
from controllers.main_controller import MainController

# Database Managers
from models.data_manager.database_manager import DatabaseManager
from models.data_manager.tire_manager import TireManager
from models.data_manager.market_cache_manager import MarketCacheManager

# Background Service
from data_ingestion_engine.ingestion_service import BackgroundIngestionService

# --- COMPANY PASSPORT APP CODE ---
from models.data_manager.company_registry_manager import CompanyRegistryManager 

def main():
    #  Initialize the Core Database
    DatabaseManager.initialize_database()
    
    # Inject the Tire Blueprints & Mounting Data
    TireManager.inject_dummy_tires()
    
    # Initialize the ETL Scraping Cache
    MarketCacheManager.initialize_cache_table()

    # Initialize the Registry & Inject Fake Data
    CompanyRegistryManager.initialize_registry_tables()
    # --- START THE SILENT ETL PIPELINE ---
    ingestion_thread = BackgroundIngestionService()
    ingestion_thread.start()
    # -------------------------------------

    # Initialize the Qt Application
    app = QApplication(sys.argv)
    
    # Force Dark Mode globally BEFORE any windows are drawn
    setTheme(Theme.DARK)
    
    # Initialize the main controller
    controller = MainController()
    
    # tell the controller to run (which shows the window)
    controller.run()
    
    #  Execute the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()