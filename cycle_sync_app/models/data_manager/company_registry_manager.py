import sqlite3
import os
from models.data_manager.database_manager import DatabaseManager

class CompanyRegistryManager:
    @staticmethod
    def initialize_registry_tables():
        """Creates the tables for the Motor Valley Federated Registry."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxonomy_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                level INTEGER NOT NULL,  
                parent_id INTEGER,       
                FOREIGN KEY (parent_id) REFERENCES taxonomy_nodes(id)
            )
        ''')
        
        # --- UPGRADED COMPANY PASSPORT TABLE ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                logo_path TEXT NOT NULL,  
                type_node_id INTEGER NOT NULL,
                description TEXT,           -- NEW: Company summary
                latitude REAL,              -- NEW: GPS Latitude
                longitude REAL,             -- NEW: GPS Longitude
                membership_tier TEXT,       -- NEW: Founding, Ordinary, Supporting
                FOREIGN KEY (type_node_id) REFERENCES taxonomy_nodes(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[Federated Registry] SQLite Tables initialized.")

    @staticmethod
    def add_taxonomy_node(label: str, level: int, parent_id: int = None):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO taxonomy_nodes (label, level, parent_id)
            VALUES (?, ?, ?)
        ''', (label, level, parent_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_taxonomy_nodes() -> list:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, label, level, parent_id FROM taxonomy_nodes")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "label": r[1], "level": r[2], "parent_id": r[3]} for r in rows]

    @staticmethod
    def register_company(name: str, logo_path: str, type_node_id: int, 
                         description: str = "", latitude: float = 0.0, 
                         longitude: float = 0.0, membership_tier: str = "Supporting Member"):
        """Issues a new Digital Passport for a company with extended metadata."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO company_registry 
            (name, logo_path, type_node_id, description, latitude, longitude, membership_tier)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, logo_path, type_node_id, description, latitude, longitude, membership_tier))
        conn.commit()
        conn.close()

    @staticmethod
    def get_registered_companies() -> list:
        """Retrieves all companies, joining with their taxonomy label and new metadata."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.logo_path, t.label, 
                   c.description, c.latitude, c.longitude, c.membership_tier
            FROM company_registry c
            JOIN taxonomy_nodes t ON c.type_node_id = t.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0], 
            "name": r[1], 
            "logo_path": r[2], 
            "type_label": r[3],
            "description": r[4],          # Added to payload
            "latitude": r[5],             # Added to payload
            "longitude": r[6],            # Added to payload
            "membership_tier": r[7]       # Added to payload
        } for r in rows]