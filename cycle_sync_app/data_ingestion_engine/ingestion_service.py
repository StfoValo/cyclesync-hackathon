import time
from PyQt6.QtCore import QThread
from data_ingestion_engine.market_scraper import MarketScraper

class BackgroundIngestionService(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        # 1. Run the scraper immediately when the thread starts
        MarketScraper.run_ingestion()
        
        # 2. For a production app, you would loop this every hour.
        # For the hackathon, running it once on boot is perfect!
        # while True:
        #     time.sleep(3600) # Sleep for 1 hour
        #     MarketScraper.run_ingestion()