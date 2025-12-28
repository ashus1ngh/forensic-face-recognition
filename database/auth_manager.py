"""
Authentication and User Management Database
Complete Implementation with Security Features
"""

import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config.config import DATABASE_PATH, ROLE_ADMIN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication and authorization"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.init_auth_database()
        self.create_default_admin()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def init_auth_database(self):
        """Initialize authentication tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    badge_number TEXT,
                    department TEXT,
                    is_active INTEGER DEFAULT 1,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(created_by) REFERENCES users(id)
                )
            ''')
            
            # Login history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP,
                    ip_address TEXT,
                    success INTEGER DEFAULT 1,
                    failure_reason TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Activity log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Password history table (optional - for password reuse prevention)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    password_hash TEXT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Sessions table (optional - for session management)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            logger.info("Authentication database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Auth database initialization error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # ========================================================================
    # PASSWORD MANAGEMENT
    # ========================================================================
    
    def hash_password(self, password):
        """
        Hash password using SHA-256
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """
        Verify password against hash
        
        Args:
            password (str): Plain text password
            password_hash (str): Stored password hash
            
        Returns:
            bool: True if password matches
        """
        return self.hash_password(password) == password_hash
    
    def is_password_strong(self, password):
        """
        Check if password meets strength requirements
        
        Args:
            password (str): Password to check
            
        Returns:
            tuple: (bool, str) - (is_strong, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and numbers"
        
        return True, "Password is strong"
    
    # ========================================================================
    # USER CREATION & MANAGEMENT
    # ========================================================================
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Create default admin
                password_hash = self.hash_password('admin123')
                cursor.execute('''
                    INSERT INTO users (username, password_hash, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('admin', password_hash, 'System Administrator', ROLE_ADMIN, 1))
                
                conn.commit()
                logger.info("✓ Default admin user created")
                logger.info("  Username: admin")
                logger.info("  Password: admin123")
                logger.info("  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
                
        except sqlite3.Error as e:
            logger.error(f"Error creating default admin: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_user(self, username, password, full_name, role, email=None, 
                 phone=None, badge_number=None, department=None, created_by=None):
        """
        Add new user
        
        Args:
            username (str): Username (unique)
            password (str): Plain text password
            full_name (str): Full name
            role (str): User role
            email (str): Email address
            phone (str): Phone number
            badge_number (str): Badge number
            department (str): Department
            created_by (int): ID of user creating this account
            
        Returns:
            int: New user ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate password strength
            is_strong, message = self.is_password_strong(password)
            if not is_strong:
                raise ValueError(f"Weak password: {message}")
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users 
                (username, password_hash, full_name, role, email, phone, 
                 badge_number, department, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, role, email, phone,
                  badge_number, department, created_by))
            
            user_id = cursor.lastrowid
            
            # Add to password history
            cursor.execute('''
                INSERT INTO password_history (user_id, password_hash)
                VALUES (?, ?)
            ''', (user_id, password_hash))
            
            conn.commit()
            
            logger.info(f"✓ User created: {username} ({role})")
            
            # Log activity if created_by is provided
            if created_by:
                self.log_activity(created_by, 'user_created', 
                                f'Created user: {username} with role: {role}')
            
            return user_id
            
        except sqlite3.IntegrityError:
            logger.error(f"Username already exists: {username}")
            raise ValueError(f"Username '{username}' already exists")
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User data or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """
        Get user by username
        
        Args:
            username (str): Username
            
        Returns:
            dict: User data or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_all_users(self):
        """
        Get all users
        
        Returns:
            list: List of user dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, full_name, role, email, phone, 
                       badge_number, department, is_active, last_login, created_at
                FROM users 
                ORDER BY created_at DESC
            ''')
            users = cursor.fetchall()
            return [dict(user) for user in users]
        finally:
            conn.close()
    
    def update_user(self, user_id, **kwargs):
        """
        Update user information
        
        Args:
            user_id (int): User ID
            **kwargs: Fields to update
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['full_name', 'role', 'email', 'phone', 
                         'badge_number', 'department', 'is_active']
        
        try:
            set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys() if k in allowed_fields])
            values = [v for k, v in kwargs.items() if k in allowed_fields]
            values.append(user_id)
            
            if set_clause:
                cursor.execute(f'''
                    UPDATE users 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', values)
                conn.commit()
                logger.info(f"✓ User updated: ID {user_id}")
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def delete_user(self, user_id):
        """
        Delete user
        
        Args:
            user_id (int): User ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Don't allow deleting the last admin
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE role = ? AND is_active = 1 AND id != ?
            ''', (ROLE_ADMIN, user_id))
            
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user and user[0] == ROLE_ADMIN:
                    raise ValueError("Cannot delete the last active admin user")
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            logger.info(f"✓ User deleted: ID {user_id}")
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def authenticate(self, username, password):
        """
        Authenticate user
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            dict: User data if successful, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"Authentication failed: User '{username}' not found")
                self._log_failed_login(None, username, "User not found")
                return None
            
            user_dict = dict(user)
            
            # Check if account is locked
            if user_dict['locked_until']:
                locked_until = datetime.fromisoformat(user_dict['locked_until'])
                if datetime.now() < locked_until:
                    logger.warning(f"Account locked: {username}")
                    self._log_failed_login(user_dict['id'], username, "Account locked")
                    return None
                else:
                    # Unlock account
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = 0, locked_until = NULL 
                        WHERE id = ?
                    ''', (user_dict['id'],))
                    conn.commit()
            
            # Check if account is active
            if not user_dict['is_active']:
                logger.warning(f"Account inactive: {username}")
                self._log_failed_login(user_dict['id'], username, "Account inactive")
                return None
            
            # Verify password
            if self.verify_password(password, user_dict['password_hash']):
                # Reset failed attempts
                cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = 0, 
                        last_login = CURRENT_TIMESTAMP,
                        locked_until = NULL
                    WHERE id = ?
                ''', (user_dict['id'],))
                
                # Log successful login
                cursor.execute('''
                    INSERT INTO login_history (user_id, success)
                    VALUES (?, 1)
                ''', (user_dict['id'],))
                
                conn.commit()
                
                logger.info(f"✓ User authenticated: {username}")
                return user_dict
            else:
                # Increment failed attempts
                failed_attempts = user_dict['failed_login_attempts'] + 1
                
                if failed_attempts >= 3:
                    # Lock account for 5 minutes
                    locked_until = datetime.now() + timedelta(minutes=5)
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (failed_attempts, locked_until.isoformat(), user_dict['id']))
                    logger.warning(f"Account locked after 3 failed attempts: {username}")
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = ?
                        WHERE id = ?
                    ''', (failed_attempts, user_dict['id']))
                
                # Log failed login
                self._log_failed_login(user_dict['id'], username, "Invalid password")
                
                conn.commit()
                
                logger.warning(f"Authentication failed: Invalid password for {username} (Attempt {failed_attempts}/3)")
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Authentication error: {e}")
            return None
        finally:
            conn.close()
    
    def _log_failed_login(self, user_id, username, reason):
        """Log failed login attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO login_history (user_id, success, failure_reason)
                VALUES (?, 0, ?)
            ''', (user_id if user_id else 0, f"{username}: {reason}"))
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging failed login: {e}")
        finally:
            conn.close()
    
    # ========================================================================
    # PASSWORD MANAGEMENT
    # ========================================================================
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id (int): User ID
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            bool: True if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user['password_hash']):
                logger.warning(f"Password change failed: Incorrect old password for user {user_id}")
                return False
            
            # Validate new password strength
            is_strong, message = self.is_password_strong(new_password)
            if not is_strong:
                raise ValueError(f"Weak password: {message}")
            
            new_hash = self.hash_password(new_password)
            
            # Check password history (prevent reuse)
            cursor.execute('''
                SELECT password_hash FROM password_history 
                WHERE user_id = ? 
                ORDER BY changed_at DESC 
                LIMIT 3
            ''', (user_id,))
            
            recent_passwords = [row[0] for row in cursor.fetchall()]
            if new_hash in recent_passwords:
                raise ValueError("Cannot reuse recent passwords")
            
            # Update password
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_hash, user_id))
            
            # Add to password history
            cursor.execute('''
                INSERT INTO password_history (user_id, password_hash)
                VALUES (?, ?)
            ''', (user_id, new_hash))
            
            conn.commit()
            logger.info(f"✓ Password changed for user {user_id}")
            
            # Log activity
            self.log_activity(user_id, 'password_changed', 'User changed their password')
            
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def reset_password(self, user_id, new_password, reset_by):
        """
        Reset user password (admin function)
        
        Args:
            user_id (int): User ID
            new_password (str): New password
            reset_by (int): ID of admin resetting password
            
        Returns:
            bool: True if successful
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate new password
            is_strong, message = self.is_password_strong(new_password)
            if not is_strong:
                raise ValueError(f"Weak password: {message}")
            
            new_hash = self.hash_password(new_password)
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, 
                    failed_login_attempts = 0,
                    locked_until = NULL,
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_hash, user_id))
            
            # Add to password history
            cursor.execute('''
                INSERT INTO password_history (user_id, password_hash)
                VALUES (?, ?)
            ''', (user_id, new_hash))
            
            conn.commit()
            logger.info(f"✓ Password reset for user {user_id} by admin {reset_by}")
            
            # Log activity
            self.log_activity(reset_by, 'password_reset', 
                            f'Reset password for user ID {user_id}')
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # ========================================================================
    # ACTIVITY LOGGING
    # ========================================================================
    
    def log_activity(self, user_id, action, details=None, ip_address=None):
        """
        Log user activity
        
        Args:
            user_id (int): User ID
            action (str): Action performed
            details (str): Additional details
            ip_address (str): IP address
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO activity_log (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Activity logging error: {e}")
        finally:
            conn.close()
    
    def get_user_activity(self, user_id, limit=100):
        """
        Get user activity log
        
        Args:
            user_id (int): User ID
            limit (int): Maximum number of records
            
        Returns:
            list: List of activity records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM activity_log 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            activities = cursor.fetchall()
            return [dict(activity) for activity in activities]
        finally:
            conn.close()
    
    def get_all_activity(self, limit=500):
        """
        Get all activity logs (admin function)
        
        Args:
            limit (int): Maximum number of records
            
        Returns:
            list: List of activity records with user info
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT a.*, u.username, u.full_name 
                FROM activity_log a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            activities = cursor.fetchall()
            return [dict(activity) for activity in activities]
        finally:
            conn.close()
    
    # ========================================================================
    # LOGIN HISTORY
    # ========================================================================
    
    def get_login_history(self, user_id=None, limit=100):
        """
        Get login history
        
        Args:
            user_id (int): User ID (None for all users)
            limit (int): Maximum number of records
            
        Returns:
            list: List of login records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if user_id:
                cursor.execute('''
                    SELECT * FROM login_history 
                    WHERE user_id = ? 
                    ORDER BY login_time DESC 
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT l.*, u.username, u.full_name 
                    FROM login_history l
                    JOIN users u ON l.user_id = u.id
                    ORDER BY l.login_time DESC 
                    LIMIT ?
                ''', (limit,))
            
            history = cursor.fetchall()
            return [dict(record) for record in history]
        finally:
            conn.close()
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_user_statistics(self):
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]
            
            # Active users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            stats['active_users'] = cursor.fetchone()[0]
            
            # Users by role
            cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
            stats['by_role'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total logins today
            cursor.execute('''
                SELECT COUNT(*) FROM login_history 
                WHERE DATE(login_time) = DATE('now')
            ''')
            stats['logins_today'] = cursor.fetchone()[0]
            
            return stats
        finally:
            conn.close()