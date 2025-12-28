import sqlite3
import pickle
import logging
from pathlib import Path
from datetime import datetime
from config.config import DATABASE_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Criminal Records Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS criminals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    criminal_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    age INTEGER,
                    height TEXT,
                    physical_description TEXT,
                    charges TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    case_number TEXT,
                    jurisdiction TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by TEXT,
                    modified_by TEXT
                )
            ''')
            
            # Mugshots Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mugshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    criminal_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    face_encoding BLOB NOT NULL,
                    capture_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    captured_by TEXT,
                    FOREIGN KEY(criminal_id) REFERENCES criminals(id) ON DELETE CASCADE
                )
            ''')
            
            # Suspects Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suspects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    image_path TEXT NOT NULL,
                    face_encoding BLOB NOT NULL,
                    capture_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by TEXT
                )
            ''')
            
            # Matches Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suspect_id INTEGER NOT NULL,
                    criminal_id INTEGER NOT NULL,
                    similarity_score REAL NOT NULL,
                    confidence REAL,
                    notes TEXT,
                    match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    matched_by TEXT,
                    FOREIGN KEY(suspect_id) REFERENCES suspects(id) ON DELETE CASCADE,
                    FOREIGN KEY(criminal_id) REFERENCES criminals(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()
    
    # ========================================================================
    # CRIMINAL OPERATIONS
    # ========================================================================
    
    def add_criminal(self, criminal_id, name, age=None, height=None, 
                     physical_description=None, charges=None, status='active',
                     case_number=None, jurisdiction=None, notes=None, 
                     added_by=None, added_date=None):
        """Add a new criminal record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO criminals 
                (criminal_id, name, age, height, physical_description, charges, 
                 status, case_number, jurisdiction, notes, added_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (criminal_id, name, age, height, physical_description, charges,
                  status, case_number, jurisdiction, notes, added_by, 
                  added_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            criminal_db_id = cursor.lastrowid
            logger.info(f"Criminal added: {name} (ID: {criminal_id}) by {added_by}")
            return criminal_db_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Criminal ID already exists: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_criminals(self):
        """Get all criminals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM criminals ORDER BY created_at DESC')
            criminals = cursor.fetchall()
            return criminals
        finally:
            conn.close()
    
    def get_criminal_by_id(self, criminal_id):
        """Get criminal by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM criminals WHERE id = ?', (criminal_id,))
            criminal = cursor.fetchone()
            return criminal
        finally:
            conn.close()
    
    def search_criminals(self, query):
        """Search criminals by name or ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            search_term = f'%{query}%'
            cursor.execute('''
                SELECT * FROM criminals 
                WHERE name LIKE ? OR criminal_id LIKE ? OR charges LIKE ?
                ORDER BY created_at DESC
            ''', (search_term, search_term, search_term))
            
            criminals = cursor.fetchall()
            return criminals
        finally:
            conn.close()
    
    def update_criminal(self, criminal_db_id, modified_by=None, modified_date=None, **kwargs):
        """Update criminal record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['criminal_id', 'name', 'age', 'height', 'physical_description', 
                         'charges', 'status', 'case_number', 'jurisdiction', 'notes']
        
        try:
            # Add user tracking
            if modified_by:
                kwargs['modified_by'] = modified_by
                kwargs['updated_at'] = modified_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys() if k in allowed_fields + ['modified_by', 'updated_at']])
            values = [v for k, v in kwargs.items() if k in allowed_fields + ['modified_by', 'updated_at']]
            values.append(criminal_db_id)
            
            if set_clause:
                cursor.execute(f'UPDATE criminals SET {set_clause} WHERE id = ?', values)
                conn.commit()
                logger.info(f"Criminal updated: ID {criminal_db_id} by {modified_by}")
        finally:
            conn.close()
    
    def delete_criminal(self, criminal_id):
        """Delete criminal record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM criminals WHERE id = ?', (criminal_id,))
            conn.commit()
            logger.info(f"Criminal deleted: ID {criminal_id}")
        finally:
            conn.close()
    
    # ========================================================================
    # MUGSHOT OPERATIONS
    # ========================================================================
    
    def add_mugshot(self, criminal_id, image_path, encoding, captured_by=None, capture_date=None):
        """Add mugshot for criminal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            encoding_blob = pickle.dumps(encoding) if encoding is not None else None
            
            cursor.execute('''
                INSERT INTO mugshots (criminal_id, image_path, face_encoding, captured_by, capture_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (criminal_id, image_path, encoding_blob, captured_by,
                  capture_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            mugshot_id = cursor.lastrowid
            logger.info(f"Mugshot added for criminal ID {criminal_id} by {captured_by}")
            return mugshot_id
        finally:
            conn.close()
    
    def get_mugshots_for_criminal(self, criminal_id):
        """Get all mugshots for a criminal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM mugshots 
                WHERE criminal_id = ?
                ORDER BY capture_date DESC
            ''', (criminal_id,))
            
            mugshots = cursor.fetchall()
            return mugshots
        finally:
            conn.close()
    
    def get_all_mugshots(self):
        """Get all mugshots from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM mugshots ORDER BY capture_date DESC')
            mugshots = cursor.fetchall()
            return mugshots
        finally:
            conn.close()
    
    def get_mugshot_encodings(self):
        """Get all face encodings from mugshots"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.id, m.criminal_id, m.face_encoding, c.name, c.criminal_id as crim_id
                FROM mugshots m
                JOIN criminals c ON m.criminal_id = c.id
            ''')
            
            encodings = []
            for row in cursor.fetchall():
                if row[2]:  # Check if encoding exists
                    encoding = pickle.loads(row[2])
                    encodings.append({
                        'id': row[0],
                        'criminal_id': row[1],
                        'encoding': encoding,
                        'name': row[3],
                        'criminal_code': row[4]
                    })
            
            return encodings
        finally:
            conn.close()
    
    # ========================================================================
    # SUSPECT OPERATIONS
    # ========================================================================
    
    def add_suspect(self, image_path, face_encoding, name=None, description=None, uploaded_by=None):
        """Add suspect image"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            encoding_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
            
            cursor.execute('''
                INSERT INTO suspects (name, description, image_path, face_encoding, uploaded_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, image_path, encoding_blob, uploaded_by))
            
            conn.commit()
            suspect_id = cursor.lastrowid
            logger.info(f"Suspect added: {name or 'Unknown'} by {uploaded_by}")
            return suspect_id
        finally:
            conn.close()
    
    def get_all_suspects(self):
        """Get all suspects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM suspects ORDER BY capture_date DESC')
            suspects = cursor.fetchall()
            return suspects
        finally:
            conn.close()
    
    # ========================================================================
    # MATCH OPERATIONS
    # ========================================================================
    
    def save_match(self, suspect_id, criminal_id, similarity_score, 
                   confidence=None, notes=None, matched_by=None):
        """Save match result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO matches (suspect_id, criminal_id, similarity_score, 
                                   confidence, notes, matched_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (suspect_id, criminal_id, similarity_score, confidence, notes, matched_by))
            
            conn.commit()
            match_id = cursor.lastrowid
            logger.info(f"Match saved: Suspect {suspect_id} -> Criminal {criminal_id} by {matched_by}")
            return match_id
        finally:
            conn.close()
    
    def get_matches_for_suspect(self, suspect_id):
        """Get all matches for suspect"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.*, c.name, c.charges, c.case_number, c.criminal_id
                FROM matches m
                JOIN criminals c ON m.criminal_id = c.id
                WHERE m.suspect_id = ?
                ORDER BY m.similarity_score DESC
            ''', (suspect_id,))
            
            matches = cursor.fetchall()
            return matches
        finally:
            conn.close()
    
    def get_all_matches(self):
        """Get all matches"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.*, c.name, c.charges, c.criminal_id
                FROM matches m
                JOIN criminals c ON m.criminal_id = c.id
                ORDER BY m.match_date DESC
            ''')
            
            matches = cursor.fetchall()
            return matches
        finally:
            conn.close()
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM criminals')
            criminal_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM mugshots')
            mugshot_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM suspects')
            suspect_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM matches')
            match_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM criminals WHERE status = "active"')
            active_criminals = cursor.fetchone()[0]
            
            return {
                'criminals': criminal_count,
                'mugshots': mugshot_count,
                'suspects': suspect_count,
                'matches': match_count,
                'active_criminals': active_criminals
            }
        finally:
            conn.close()