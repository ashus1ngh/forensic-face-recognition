"""
Database Models and Schema Definitions
"""

# Criminal Record Model
CRIMINAL_SCHEMA = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'criminal_id': 'TEXT UNIQUE NOT NULL',
    'name': 'TEXT NOT NULL',
    'age': 'INTEGER',
    'height': 'TEXT',
    'physical_description': 'TEXT',
    'charges': 'TEXT NOT NULL',
    'status': 'TEXT DEFAULT "active"',
    'case_number': 'TEXT',
    'jurisdiction': 'TEXT',
    'notes': 'TEXT',
    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
}

# Mugshot Model
MUGSHOT_SCHEMA = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'criminal_id': 'INTEGER NOT NULL',
    'image_path': 'TEXT NOT NULL',
    'face_encoding': 'BLOB NOT NULL',
    'capture_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'FOREIGN KEY': '(criminal_id) REFERENCES criminals(id) ON DELETE CASCADE'
}

# Add more models as needed...