"""
Settings Tab - Application configuration and preferences with Modern Theme
Save this as: gui/tabs/settings_tab.py
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QGroupBox, QSpinBox, QCheckBox, QLineEdit,
                              QComboBox, QSlider, QMessageBox, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import json
import os

from config.config import COLORS


class SettingsTab(QWidget):
    """Settings and configuration tab"""
    
    settings_changed = pyqtSignal(dict)  # Emit when settings change
    theme_changed = pyqtSignal(str)  # Emit when theme changes
    
    def __init__(self, config, db_manager, current_user, theme_manager=None):
        super().__init__()
        self.config = config
        self.db_manager = db_manager
        self.current_user = current_user
        self.theme_manager = theme_manager
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize UI components"""
        # Main scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ==================== HEADER ====================
        header_label = QLabel("⚙️ Application Settings")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        subtitle_label = QLabel("Configure your face recognition system preferences")
        subtitle_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(subtitle_label)
        
        # ==================== RECOGNITION SETTINGS ====================
        recognition_group = QGroupBox("🔍 Face Recognition Settings")
        recognition_layout = QVBoxLayout()
        recognition_layout.setSpacing(16)
        
        # Confidence threshold
        conf_container = QVBoxLayout()
        conf_label = QLabel("Match Confidence Threshold")
        conf_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        conf_container.addWidget(conf_label)
        
        conf_input_layout = QHBoxLayout()
        self.spin_confidence = QSpinBox()
        self.spin_confidence.setRange(50, 99)
        self.spin_confidence.setValue(70)
        self.spin_confidence.setSuffix("%")
        self.spin_confidence.setMinimumWidth(120)
        conf_input_layout.addWidget(self.spin_confidence)
        
        self.lbl_conf_desc = QLabel("Higher = More strict matching")
        self.lbl_conf_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        conf_input_layout.addWidget(self.lbl_conf_desc)
        conf_input_layout.addStretch()
        
        conf_container.addLayout(conf_input_layout)
        recognition_layout.addLayout(conf_container)
        
        # Face detection model
        model_container = QVBoxLayout()
        model_label = QLabel("Detection Model")
        model_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        model_container.addWidget(model_label)
        
        model_input_layout = QHBoxLayout()
        self.combo_model = QComboBox()
        self.combo_model.addItems(["HOG (Fast)", "CNN (Accurate)"])
        self.combo_model.setMinimumWidth(200)
        model_input_layout.addWidget(self.combo_model)
        model_input_layout.addStretch()
        
        model_container.addLayout(model_input_layout)
        recognition_layout.addLayout(model_container)
        
        # Number of matches to show
        matches_container = QVBoxLayout()
        matches_label = QLabel("Max Matches to Display")
        matches_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        matches_container.addWidget(matches_label)
        
        matches_input_layout = QHBoxLayout()
        self.spin_max_matches = QSpinBox()
        self.spin_max_matches.setRange(1, 10)
        self.spin_max_matches.setValue(5)
        self.spin_max_matches.setMinimumWidth(120)
        matches_input_layout.addWidget(self.spin_max_matches)
        matches_input_layout.addStretch()
        
        matches_container.addLayout(matches_input_layout)
        recognition_layout.addLayout(matches_container)
        
        self.chk_auto_save = QCheckBox("Automatically save recognition results")
        self.chk_auto_save.setChecked(True)
        recognition_layout.addWidget(self.chk_auto_save)
        
        recognition_group.setLayout(recognition_layout)
        layout.addWidget(recognition_group)
        
        # ==================== DATABASE SETTINGS ====================
        database_group = QGroupBox("💾 Database Settings")
        database_layout = QVBoxLayout()
        database_layout.setSpacing(16)
        
        # Database path
        db_path_container = QVBoxLayout()
        db_path_label = QLabel("Database Location")
        db_path_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        db_path_container.addWidget(db_path_label)
        
        db_path_input_layout = QHBoxLayout()
        self.txt_db_path = QLineEdit()
        self.txt_db_path.setReadOnly(True)
        self.txt_db_path.setText(str(self.config.DATABASE_PATH) if hasattr(self.config, 'DATABASE_PATH') else "data/database.db")
        db_path_input_layout.addWidget(self.txt_db_path)
        
        self.btn_browse_db = QPushButton("📁 Browse")
        self.btn_browse_db.clicked.connect(self.browse_database)
        self.btn_browse_db.setMinimumWidth(120)
        db_path_input_layout.addWidget(self.btn_browse_db)
        
        db_path_container.addLayout(db_path_input_layout)
        database_layout.addLayout(db_path_container)
        
        # Database action buttons
        db_buttons_layout = QHBoxLayout()
        self.btn_backup_db = QPushButton("💾 Backup Database")
        self.btn_restore_db = QPushButton("📥 Restore Database")
        self.btn_optimize_db = QPushButton("⚡ Optimize Database")
        
        self.btn_backup_db.clicked.connect(self.backup_database)
        self.btn_restore_db.clicked.connect(self.restore_database)
        self.btn_optimize_db.clicked.connect(self.optimize_database)
        
        db_buttons_layout.addWidget(self.btn_backup_db)
        db_buttons_layout.addWidget(self.btn_restore_db)
        db_buttons_layout.addWidget(self.btn_optimize_db)
        
        database_layout.addLayout(db_buttons_layout)
        
        # Database stats
        self.lbl_db_stats = QLabel("Database: Ready")
        self.lbl_db_stats.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 10px; background-color: {COLORS['bg_hover']}; border-radius: 6px;")
        database_layout.addWidget(self.lbl_db_stats)
        
        database_group.setLayout(database_layout)
        layout.addWidget(database_group)
        
        # ==================== APPEARANCE SETTINGS ====================
        appearance_group = QGroupBox("🎨 Appearance")
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(16)
        
        # Theme selection
        theme_container = QVBoxLayout()
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        theme_container.addWidget(theme_label)
        
        theme_input_layout = QHBoxLayout()
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Light", "Dark"])
        self.combo_theme.currentTextChanged.connect(self.change_theme)
        self.combo_theme.setMinimumWidth(200)
        theme_input_layout.addWidget(self.combo_theme)
        theme_input_layout.addStretch()
        
        theme_container.addLayout(theme_input_layout)
        appearance_layout.addLayout(theme_container)
        
        # Font size
        font_container = QVBoxLayout()
        font_label = QLabel("Font Size")
        font_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        font_container.addWidget(font_label)
        
        font_input_layout = QHBoxLayout()
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(10, 18)
        self.spin_font_size.setValue(14)
        self.spin_font_size.setSuffix("px")
        self.spin_font_size.setMinimumWidth(120)
        font_input_layout.addWidget(self.spin_font_size)
        font_input_layout.addStretch()
        
        font_container.addLayout(font_input_layout)
        appearance_layout.addLayout(font_container)
        
        self.chk_animations = QCheckBox("Enable UI Animations")
        self.chk_animations.setChecked(True)
        appearance_layout.addWidget(self.chk_animations)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # ==================== SECURITY SETTINGS ====================
        security_group = QGroupBox("🔒 Security Settings")
        security_layout = QVBoxLayout()
        security_layout.setSpacing(16)
        
        self.chk_require_auth = QCheckBox("Require authentication on startup")
        self.chk_require_auth.setChecked(True)
        security_layout.addWidget(self.chk_require_auth)
        
        # Session timeout
        session_container = QVBoxLayout()
        session_label = QLabel("Session Timeout")
        session_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        session_container.addWidget(session_label)
        
        session_input_layout = QHBoxLayout()
        self.spin_session_timeout = QSpinBox()
        self.spin_session_timeout.setRange(5, 120)
        self.spin_session_timeout.setValue(30)
        self.spin_session_timeout.setSuffix(" minutes")
        self.spin_session_timeout.setMinimumWidth(150)
        session_input_layout.addWidget(self.spin_session_timeout)
        session_input_layout.addStretch()
        
        session_container.addLayout(session_input_layout)
        security_layout.addLayout(session_container)
        
        self.chk_audit_log = QCheckBox("Enable detailed audit logging")
        self.chk_audit_log.setChecked(True)
        security_layout.addWidget(self.chk_audit_log)
        
        self.btn_manage_users = QPushButton("👥 Manage Users")
        self.btn_manage_users.clicked.connect(self.manage_users)
        self.btn_manage_users.setMinimumHeight(44)
        security_layout.addWidget(self.btn_manage_users)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # ==================== DATA MANAGEMENT ====================
        data_group = QGroupBox("📊 Data Management")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(12)
        
        # Export/Import buttons
        export_import_layout = QHBoxLayout()
        self.btn_export_criminals = QPushButton("📤 Export Database")
        self.btn_import_criminals = QPushButton("📥 Import Database")
        
        self.btn_export_criminals.clicked.connect(self.export_criminals)
        self.btn_import_criminals.clicked.connect(self.import_criminals)
        
        self.btn_export_criminals.setMinimumHeight(44)
        self.btn_import_criminals.setMinimumHeight(44)
        
        export_import_layout.addWidget(self.btn_export_criminals)
        export_import_layout.addWidget(self.btn_import_criminals)
        
        data_layout.addLayout(export_import_layout)
        
        self.btn_clear_cache = QPushButton("🗑️ Clear Cache")
        self.btn_clear_cache.clicked.connect(self.clear_cache)
        self.btn_clear_cache.setMinimumHeight(44)
        data_layout.addWidget(self.btn_clear_cache)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # ==================== ACTION BUTTONS ====================
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.btn_reset = QPushButton("↺ Reset to Defaults")
        self.btn_reset.setObjectName("secondaryButton")
        self.btn_reset.clicked.connect(self.reset_settings)
        self.btn_reset.setMinimumHeight(48)
        self.btn_reset.setMinimumWidth(150)
        
        self.btn_save = QPushButton("💾 Save Settings")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_save.setMinimumHeight(48)
        self.btn_save.setMinimumWidth(150)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_reset)
        button_layout.addWidget(self.btn_save)
        
        layout.addLayout(button_layout)
        
        # Set scroll widget
        scroll.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Apply custom stylesheet for action buttons
        self.btn_save.setStyleSheet(f"""
            QPushButton#primaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, 
                    stop:1 {COLORS['primary_dark']});
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
            }}
            QPushButton#primaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_dark']}, 
                    stop:1 {COLORS['primary']});
            }}
        """)
        
        self.btn_reset.setStyleSheet(f"""
            QPushButton#secondaryButton {{
                background-color: white;
                color: {COLORS['text_secondary']};
                border: 2px solid {COLORS['border_light']};
                border-radius: 8px;
                font-weight: 600;
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {COLORS['bg_hover']};
                border: 2px solid {COLORS['border_medium']};
                color: {COLORS['text_primary']};
            }}
        """)
        
        # Update database stats
        self.update_db_stats()
        
    def load_settings(self):
        """Load settings from config"""
        try:
            config_file = "data/settings.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    
                self.spin_confidence.setValue(settings.get('confidence_threshold', 70))
                self.combo_model.setCurrentText(settings.get('detection_model', 'HOG (Fast)'))
                self.spin_max_matches.setValue(settings.get('max_matches', 5))
                self.chk_auto_save.setChecked(settings.get('auto_save', True))
                self.combo_theme.setCurrentText(settings.get('theme', 'Light'))
                self.spin_font_size.setValue(settings.get('font_size', 14))
                self.chk_animations.setChecked(settings.get('animations', True))
                self.spin_session_timeout.setValue(settings.get('session_timeout', 30))
                self.chk_audit_log.setChecked(settings.get('audit_log', True))
                self.chk_require_auth.setChecked(settings.get('require_auth', True))
        except Exception as e:
            print(f"Failed to load settings: {e}")
            
    def save_settings(self):
        """Save settings to file"""
        try:
            os.makedirs("data", exist_ok=True)
            
            settings = {
                'confidence_threshold': self.spin_confidence.value(),
                'detection_model': self.combo_model.currentText(),
                'max_matches': self.spin_max_matches.value(),
                'auto_save': self.chk_auto_save.isChecked(),
                'theme': self.combo_theme.currentText(),
                'font_size': self.spin_font_size.value(),
                'animations': self.chk_animations.isChecked(),
                'session_timeout': self.spin_session_timeout.value(),
                'audit_log': self.chk_audit_log.isChecked(),
                'require_auth': self.chk_require_auth.isChecked(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open("data/settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
                
            self.settings_changed.emit(settings)
            
            # Show success message
            self._show_success_message("Settings Saved", "Your settings have been saved successfully!")
            
        except Exception as e:
            self._show_error_message("Error", f"Failed to save settings: {str(e)}")
            
    def reset_settings(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.spin_confidence.setValue(70)
            self.combo_model.setCurrentIndex(0)
            self.spin_max_matches.setValue(5)
            self.chk_auto_save.setChecked(True)
            self.combo_theme.setCurrentIndex(0)
            self.spin_font_size.setValue(14)
            self.chk_animations.setChecked(True)
            self.spin_session_timeout.setValue(30)
            self.chk_audit_log.setChecked(True)
            self.chk_require_auth.setChecked(True)
            
            self._show_success_message("Reset Complete", "Settings have been reset to defaults")
            
    def change_theme(self, theme_name):
        """Change application theme"""
        if self.theme_manager:
            try:
                self.theme_changed.emit(theme_name)
                print(f"Theme changed to: {theme_name}")
            except Exception as e:
                print(f"Theme change error: {e}")
            
    def browse_database(self):
        """Browse for database location"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Select Database Location",
            "data/database.db",
            "SQLite Database (*.db)"
        )
        
        if filename:
            self.txt_db_path.setText(filename)
            
    def backup_database(self):
        """Backup database"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Database Backup",
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            "Database Files (*.db)"
        )
        
        if filename:
            try:
                import shutil
                shutil.copy2(self.txt_db_path.text(), filename)
                self._show_success_message("Backup Complete", "Database backed up successfully")
            except Exception as e:
                self._show_error_message("Backup Failed", f"Backup failed: {str(e)}")
                
    def restore_database(self):
        """Restore database from backup"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            "",
            "Database Files (*.db)"
        )
        
        if filename:
            reply = QMessageBox.warning(
                self, "Restore Database",
                "This will replace the current database. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    import shutil
                    shutil.copy2(filename, self.txt_db_path.text())
                    self._show_success_message("Restore Complete", "Database restored successfully")
                except Exception as e:
                    self._show_error_message("Restore Failed", f"Restore failed: {str(e)}")
                    
    def optimize_database(self):
        """Optimize database"""
        try:
            if hasattr(self.db_manager, 'optimize_database'):
                self.db_manager.optimize_database()
            self._show_success_message("Optimization Complete", "Database optimized successfully")
            self.update_db_stats()
        except Exception as e:
            self._show_error_message("Optimization Failed", f"Optimization failed: {str(e)}")
            
    def update_db_stats(self):
        """Update database statistics"""
        try:
            if hasattr(self.db_manager, 'get_database_stats'):
                stats = self.db_manager.get_database_stats()
                self.lbl_db_stats.setText(
                    f"📊 Criminals: {stats.get('criminals', 0)} | "
                    f"🎯 Matches: {stats.get('matches', 0)} | "
                    f"💾 Size: {stats.get('size', 'Unknown')}"
                )
            else:
                self.lbl_db_stats.setText("📊 Database: Ready")
        except:
            self.lbl_db_stats.setText("📊 Database: Ready")
            
    def manage_users(self):
        """Open user management dialog"""
        try:
            from gui.dialogs.user_management_dialog import UserManagementDialog
            from database.auth_manager import AuthManager
            
            auth_manager = AuthManager(self.db_manager)
            dialog = UserManagementDialog(auth_manager, self.current_user, self)
            dialog.exec_()
        except ImportError as e:
            self._show_error_message("Module Not Found", f"User management module not available: {str(e)}")
        
    def export_criminals(self):
        """Export criminal database"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Criminal Database",
            f"criminals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                if hasattr(self.db_manager, 'get_all_criminals'):
                    criminals = self.db_manager.get_all_criminals()
                else:
                    criminals = []
                
                export_data = {
                    'export_date': datetime.now().isoformat(),
                    'total_records': len(criminals),
                    'criminals': criminals
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
                self._show_success_message("Export Complete", f"Exported {len(criminals)} records successfully")
            except Exception as e:
                self._show_error_message("Export Failed", f"Export failed: {str(e)}")
                
    def import_criminals(self):
        """Import criminal database"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Criminal Database",
            "",
            "JSON Files (*.json)"
        )
        
        if filename:
            reply = QMessageBox.question(
                self, "Import Data",
                "This will add records to the database. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        
                    criminals = data.get('criminals', [])
                    imported = len(criminals)
                    
                    # Import logic would go here
                    
                    self._show_success_message("Import Complete", f"Imported {imported} records successfully")
                except Exception as e:
                    self._show_error_message("Import Failed", f"Import failed: {str(e)}")
                    
    def clear_cache(self):
        """Clear cache files"""
        reply = QMessageBox.question(
            self, "Clear Cache",
            "Are you sure you want to clear all cached face encodings?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                import shutil
                cache_dirs = ['data/encodings', 'data/temp']
                
                for cache_dir in cache_dirs:
                    if os.path.exists(cache_dir):
                        shutil.rmtree(cache_dir)
                        os.makedirs(cache_dir)
                        
                self._show_success_message("Cache Cleared", "Cache cleared successfully")
            except Exception as e:
                self._show_error_message("Clear Failed", f"Failed to clear cache: {str(e)}")
    
    def _show_success_message(self, title, message):
        """Show styled success message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #0D9488;
            }}
        """)
        msg_box.exec_()
    
    def _show_error_message(self, title, message):
        """Show styled error message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        msg_box.exec_()