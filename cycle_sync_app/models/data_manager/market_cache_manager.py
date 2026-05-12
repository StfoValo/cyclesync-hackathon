import sqlite3
from models.data_manager.database_manager import DatabaseManager

class MarketCacheManager:
    @staticmethod
    def initialize_cache_table():
        """Creates the ETL cache table for background web scraping."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_intelligence_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_sector TEXT NOT NULL,
                source_name TEXT,
                source_url TEXT,
                extracted_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[ETL] Market Intelligence Cache Table initialized.")

    @staticmethod
    def cache_market_data(sector: str, source_name: str, source_url: str, extracted_text: str):
        """Used by the background ingestion service to save new articles."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # Guardrail: Check if we already scraped this exact URL so we don't duplicate data
        cursor.execute('''
            SELECT id FROM market_intelligence_cache 
            WHERE source_url = ? AND material_sector = ?
        ''', (source_url, sector))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO market_intelligence_cache (material_sector, source_name, source_url, extracted_text)
                VALUES (?, ?, ?, ?)
            ''', (sector, source_name, source_url, extracted_text))
            conn.commit()
            
        conn.close()

    @staticmethod
    def get_recent_context(sector: str, limit: int = 3) -> str:
        """Used by the MotorValleyAgent to fetch the latest scraped data for Gemini."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_name, source_url, extracted_text 
            FROM market_intelligence_cache 
            WHERE material_sector = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (sector, limit))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return f"System Fallback: No live data currently cached for {sector}."
        
        # Format it beautifully for the AI's prompt
        formatted_context = ""
        for src, url, text in results:
            formatted_context += f"Source: {src} | URL: {url}\nInsight: {text}\n\n"
            
        return formatted_context.strip()