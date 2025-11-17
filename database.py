"""
Database manager for OMAC - One 'Mazing ActionFigure Catalog.

Handles SQLite database operations for storing action figure data and photos.
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database operations for action figure collection."""
    
    def __init__(self, db_path: str = "action_figures.db"):
        """Initialize database manager with given database path."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create action_figures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_figures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                series TEXT,
                manufacturer TEXT,
                year INTEGER,
                scale TEXT,
                condition TEXT,
                purchase_price REAL,
                current_value REAL,
                location TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create photos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                figure_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                caption TEXT,
                is_primary BOOLEAN DEFAULT 0,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (figure_id) REFERENCES action_figures (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_figures_name ON action_figures(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_figures_series ON action_figures(series)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_photos_figure_id ON photos(figure_id)')
        
        conn.commit()
        conn.close()
    
    def add_figure(self, figure_data: Dict) -> int:
        """Add a new action figure to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO action_figures 
            (name, series, manufacturer, year, scale, condition, purchase_price, 
             current_value, location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            figure_data.get('name', ''),
            figure_data.get('series', ''),
            figure_data.get('manufacturer', ''),
            figure_data.get('year'),
            figure_data.get('scale', ''),
            figure_data.get('condition', ''),
            figure_data.get('purchase_price'),
            figure_data.get('current_value'),
            figure_data.get('location', ''),
            figure_data.get('notes', '')
        ))
        
        figure_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return figure_id
    
    def update_figure(self, figure_id: int, figure_data: Dict) -> bool:
        """Update an existing action figure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE action_figures SET
                name = ?, series = ?, manufacturer = ?, year = ?, scale = ?,
                condition = ?, purchase_price = ?, current_value = ?,
                location = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            figure_data.get('name', ''),
            figure_data.get('series', ''),
            figure_data.get('manufacturer', ''),
            figure_data.get('year'),
            figure_data.get('scale', ''),
            figure_data.get('condition', ''),
            figure_data.get('purchase_price'),
            figure_data.get('current_value'),
            figure_data.get('location', ''),
            figure_data.get('notes', ''),
            figure_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_figure(self, figure_id: int) -> bool:
        """Delete an action figure and its associated photos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete associated photo files
        photos = self.get_figure_photos(figure_id)
        for photo in photos:
            if os.path.exists(photo['file_path']):
                try:
                    os.remove(photo['file_path'])
                except OSError:
                    pass  # File might be in use or already deleted
        
        # Delete from database (photos will be deleted by CASCADE)
        cursor.execute('DELETE FROM action_figures WHERE id = ?', (figure_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_all_figures(self) -> List[Dict]:
        """Get all action figures from the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT af.*, 
                   (SELECT COUNT(*) FROM photos p WHERE p.figure_id = af.id) as photo_count,
                   (SELECT file_path FROM photos p WHERE p.figure_id = af.id AND p.is_primary = 1 LIMIT 1) as primary_photo
            FROM action_figures af
            ORDER BY af.name
        ''')
        
        figures = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return figures
    
    def get_figure(self, figure_id: int) -> Optional[Dict]:
        """Get a specific action figure by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM action_figures WHERE id = ?', (figure_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def search_figures(self, search_term: str) -> List[Dict]:
        """Search for action figures by name or series."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{search_term}%"
        cursor.execute('''
            SELECT af.*, 
                   (SELECT COUNT(*) FROM photos p WHERE p.figure_id = af.id) as photo_count,
                   (SELECT file_path FROM photos p WHERE p.figure_id = af.id AND p.is_primary = 1 LIMIT 1) as primary_photo
            FROM action_figures af
            WHERE af.name LIKE ? OR af.series LIKE ? OR af.manufacturer LIKE ?
            ORDER BY af.name
        ''', (search_term, search_term, search_term))
        
        figures = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return figures
    
    def add_photo(self, figure_id: int, file_path: str, caption: str = "", is_primary: bool = False) -> int:
        """Add a photo to an action figure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # If this is set as primary, unset other primary photos for this figure
        if is_primary:
            cursor.execute('UPDATE photos SET is_primary = 0 WHERE figure_id = ?', (figure_id,))
        
        cursor.execute('''
            INSERT INTO photos (figure_id, file_path, caption, is_primary)
            VALUES (?, ?, ?, ?)
        ''', (figure_id, file_path, caption, is_primary))
        
        photo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return photo_id
    
    def get_figure_photos(self, figure_id: int) -> List[Dict]:
        """Get all photos for a specific action figure."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM photos 
            WHERE figure_id = ? 
            ORDER BY is_primary DESC, upload_date DESC
        ''', (figure_id,))
        
        photos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return photos
    
    def get_all_photos(self) -> List[Dict]:
        """Get all photos in the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM photos ORDER BY figure_id, upload_date DESC')
        
        photos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return photos
    
    def delete_photo(self, photo_id: int) -> bool:
        """Delete a photo from the database and file system."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get photo info before deletion
        cursor.execute('SELECT file_path FROM photos WHERE id = ?', (photo_id,))
        row = cursor.fetchone()
        
        if row:
            file_path = row['file_path']
            cursor.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
            success = cursor.rowcount > 0
            
            if success and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # File might be in use
            
            conn.commit()
            conn.close()
            return success
        
        conn.close()
        return False
    
    def set_primary_photo(self, figure_id: int, photo_id: int) -> bool:
        """Set a photo as the primary photo for a figure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Unset all primary photos for this figure
        cursor.execute('UPDATE photos SET is_primary = 0 WHERE figure_id = ?', (figure_id,))
        
        # Set the specified photo as primary
        cursor.execute('UPDATE photos SET is_primary = 1 WHERE id = ? AND figure_id = ?', 
                      (photo_id, figure_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total_figures FROM action_figures')
        total_figures = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) as total_photos FROM photos')
        total_photos = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(purchase_price) as total_spent FROM action_figures WHERE purchase_price IS NOT NULL')
        total_spent = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_figures': total_figures,
            'total_photos': total_photos,
            'total_spent': total_spent,
            'total_value': total_spent  # Use total_spent for total_value
        }
    
    def clear_all_data(self):
        """Clear all data from the database (for restore operations)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete all photos first (due to foreign key constraint)
            cursor.execute('DELETE FROM photos')
            # Delete all figures
            cursor.execute('DELETE FROM action_figures')
            # Reset auto-increment counters
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="action_figures"')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="photos"')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()