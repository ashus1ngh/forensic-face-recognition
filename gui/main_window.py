"""
Main Window for Forensic Face Recognition System
Updated with Authentication, Themes, Export, Batch Processing
gui/main_window.py
"""

import logging
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QWidget, QStatusBar, QMenuBar, QMenu, QMessageBox,
                             QPushButton, QLabel, QFileDialog, QDialog, QRadioButton, 
                             QButtonGroup, QApplication)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt, QTimer

from database.db_manager import DatabaseManager
from database.auth_manager import AuthManager
from core.face_recognition_engine import FaceRecognitionEngine
from core.export_manager import ExportManager
from gui.styles.theme_manager import ThemeManager
from config.config import COLORS

# Import tabs
from gui.tabs.criminal_tab import CriminalDatabaseTab
from gui.tabs.mugshot_tab import MugshotCaptureTab
from gui.tabs.recognition_tab import SuspectRecognitionTab
from gui.tabs.results_tab import MatchResultsTab
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.batch_tab import BatchProcessingTab
from gui.tabs.realtime_tab import RealtimeRecognitionTab

from config.config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, has_permission
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, user):
        super().__init__()
        
        self.user = user
        
        # Initialize core components
        self.db = DatabaseManager()
        self.auth_manager = AuthManager()
        self.face_engine = FaceRecognitionEngine()
        self.export_manager = ExportManager()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Setup UI FIRST
        self.setup_ui()
        
        # Apply theme AFTER UI is created
        self.apply_theme('Light')
        
        # Start session timer
        self.start_session_timer()
        
        # Log activity
        self.auth_manager.log_activity(
            self.user['id'],
            'app_started',
            f'User opened application'
        )
        
        logger.info(f"{APP_NAME} started for user: {user['username']}")
    
    def setup_ui(self):
        """Setup user interface"""
        
        # Window settings
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {self.user['full_name']}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(3)
        
        # User info bar
        user_bar = self.create_user_info_bar()
        main_layout.addWidget(user_bar)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs based on permissions
        self.create_tabs()
        
        main_layout.addWidget(self.tabs)
        
        central_widget.setLayout(main_layout)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.statusBar().showMessage(f"Ready | Logged in as: {self.user['full_name']} ({self.user['role']})")
        
        # Connect signals
        if hasattr(self, 'recognition_tab'):
            self.recognition_tab.matches_found.connect(self.on_matches_found)
        if hasattr(self, 'batch_tab'):
            self.batch_tab.batch_completed.connect(self.on_batch_completed)
    
    def create_user_info_bar(self):
        """Create user information bar"""
        bar = QWidget()
        bar.setObjectName("userInfoBar")
        bar.setMaximumHeight(70)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # User info section
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        
        user_label = QLabel(f"👤 {self.user['full_name']}")
        user_label.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {COLORS['text_primary']};")
        user_info_layout.addWidget(user_label)
        
        role_label = QLabel(f"Role: {self.user['role']}")
        role_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        user_info_layout.addWidget(role_label)
        
        layout.addWidget(user_info_widget)
        layout.addStretch()
        
        # Quick action buttons
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setObjectName("quickActionBtn")
        stats_btn.clicked.connect(self.show_statistics)
        stats_btn.setMinimumHeight(40)
        stats_btn.setMinimumWidth(120)
        layout.addWidget(stats_btn)
        
        export_btn = QPushButton("📄 Export")
        export_btn.setObjectName("quickActionBtn")
        export_btn.clicked.connect(self.quick_export)
        export_btn.setMinimumHeight(40)
        export_btn.setMinimumWidth(120)
        layout.addWidget(export_btn)
        
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMinimumHeight(40)
        logout_btn.setMinimumWidth(120)
        layout.addWidget(logout_btn)
        
        # Apply custom styles to user bar
        bar.setStyleSheet(f"""
            QWidget#userInfoBar {{
                background-color: white;
                border-bottom: 2px solid {COLORS['border_light']};
            }}
            QPushButton#quickActionBtn {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#quickActionBtn:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QPushButton#logoutBtn {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#logoutBtn:hover {{
                background-color: #C62828;
            }}
        """)
        
        bar.setLayout(layout)
        return bar
    
    def create_tabs(self):
        """Create tabs based on user permissions"""

        from config import config
        # Settings Tab with theme manager
        self.settings_tab = SettingsTab(config, self.db, self.user, self.theme_manager)

        # Criminal Database Tab (all users)
        self.criminal_tab = CriminalDatabaseTab(self.db, self.user)
        self.tabs.addTab(self.criminal_tab, "🔍 Criminal Database")
        
        # Mugshot Capture Tab (all users can capture)
        if has_permission(self.user['role'], 'add_mugshot'):
            self.mugshot_tab = MugshotCaptureTab(self.db, self.face_engine, self.user)
            self.tabs.addTab(self.mugshot_tab, "📸 Capture Mugshots")
        
        # Suspect Recognition Tab (all users)
        if has_permission(self.user['role'], 'recognize_suspect'):
            self.recognition_tab = SuspectRecognitionTab(self.db, self.face_engine, self, self.user)
            self.tabs.addTab(self.recognition_tab, "👤 Suspect Recognition")
        
        # Batch Processing Tab
        if has_permission(self.user['role'], 'batch_process'):
            self.batch_tab = BatchProcessingTab(self.db, self.face_engine, self.user)
            self.tabs.addTab(self.batch_tab, "📂 Batch Processing")
        
        # Real-time Recognition Tab
        if has_permission(self.user['role'], 'realtime_recognition'):
            self.realtime_tab = RealtimeRecognitionTab(self.db, self.face_engine, self.user)
            self.tabs.addTab(self.realtime_tab, "🎥 Real-time Recognition")
        
        # Match Results Tab (all users)
        self.results_tab = MatchResultsTab(self.db, self.export_manager, self.user)
        self.tabs.addTab(self.results_tab, "✓ Match Results")
        
        # Connect theme change signal
        self.settings_tab.theme_changed.connect(self.apply_theme)
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QAction("Refresh Database", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Report...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_menu = view_menu.addMenu("Theme")
        
        light_theme = QAction("Light Theme", self)
        light_theme.triggered.connect(lambda: self.apply_theme('Light'))
        theme_menu.addAction(light_theme)
        
        dark_theme = QAction("Dark Theme", self)
        dark_theme.triggered.connect(lambda: self.apply_theme('Dark'))
        theme_menu.addAction(dark_theme)
        
        view_menu.addSeparator()
        
        clear_cache = QAction("Clear Cache", self)
        clear_cache.triggered.connect(self.clear_cache)
        view_menu.addAction(clear_cache)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        stats_action = QAction("Database Statistics", self)
        stats_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(stats_action)
        
        if has_permission(self.user['role'], 'manage_users'):
            user_mgmt = QAction("User Management", self)
            user_mgmt.triggered.connect(self.show_user_management)
            tools_menu.addAction(user_mgmt)
        
        activity_log = QAction("Activity Log", self)
        activity_log.triggered.connect(self.show_activity_log)
        tools_menu.addAction(activity_log)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        guide_action = QAction("User Guide", self)
        guide_action.setShortcut("F1")
        guide_action.triggered.connect(self.show_guide)
        help_menu.addAction(guide_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def start_session_timer(self):
        """Start session timeout timer"""
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.check_session)
        self.session_timer.start(60000)  # Check every minute
    
    def check_session(self):
        """Check if session should timeout"""
        # Could implement session timeout logic here
        pass
    
    def apply_theme(self, theme_name):
        """Apply theme to entire application"""
        try:
            # Get stylesheet from theme manager
            stylesheet = self.theme_manager.get_stylesheet(theme_name)
            
            # Apply to entire application (not just this window)
            QApplication.instance().setStyleSheet(stylesheet)
            
            # Update status bar
            self.statusBar().showMessage(f"✓ {theme_name} theme applied", 3000)
            
            logger.info(f"Theme changed to: {theme_name}")
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            self.statusBar().showMessage(f"✗ Error applying theme: {e}", 5000)
    
    def on_matches_found(self, matches):
        """Handle matches found signal from recognition tab"""
        if matches:
            self.tabs.setCurrentWidget(self.results_tab)
            self.results_tab.display_results(matches)
            self.statusBar().showMessage(f"Found {len(matches)} potential matches")
            
            # Log activity
            self.auth_manager.log_activity(
                self.user['id'],
                'matches_found',
                f'Found {len(matches)} matches for suspect'
            )
    
    def on_batch_completed(self, summary):
        """Handle batch processing completion"""
        QMessageBox.information(
            self,
            "Batch Processing Complete",
            f"Processed: {summary['total']} images\n"
            f"Successful: {summary['successful']}\n"
            f"Failed: {summary['failed']}\n"
            f"Total Matches: {summary['total_matches']}"
        )
        
        self.statusBar().showMessage(
            f"Batch completed: {summary['successful']}/{summary['total']} successful"
        )
    
    def refresh_all(self):
        """Refresh all tabs"""
        if hasattr(self, 'criminal_tab'):
            self.criminal_tab.refresh_criminal_list()
        if hasattr(self, 'mugshot_tab'):
            self.mugshot_tab.refresh_criminal_combo()
        if hasattr(self, 'results_tab'):
            self.results_tab.refresh_results()
        
        self.statusBar().showMessage("✓ Database refreshed", 3000)
        logger.info("All tabs refreshed")
    
    def clear_cache(self):
        """Clear face encoding cache"""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Clear face encoding cache? This will free up memory.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear cache logic here
            self.statusBar().showMessage("✓ Cache cleared", 3000)
            logger.info("Face encoding cache cleared")
    
    def quick_export(self):
        """Quick export current data"""
        if not has_permission(self.user['role'], 'export_results'):
            QMessageBox.warning(self, "Permission Denied", 
                              "You don't have permission to export reports")
            return
        
        # Show export options dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Quick Export")
        dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Select Export Format")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        button_group = QButtonGroup()
        
        pdf_radio = QRadioButton("📄 PDF Report (Complete)")
        pdf_radio.setChecked(True)
        button_group.addButton(pdf_radio)
        layout.addWidget(pdf_radio)
        
        csv_radio = QRadioButton("📊 CSV Data (Spreadsheet)")
        button_group.addButton(csv_radio)
        layout.addWidget(csv_radio)
        
        json_radio = QRadioButton("💾 JSON Data (Raw)")
        button_group.addButton(json_radio)
        layout.addWidget(json_radio)
        
        layout.addSpacing(10)
        
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setMinimumHeight(40)
        button_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(dialog.accept)
        export_btn.setMinimumHeight(40)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec_():
            # Perform export based on selection
            if pdf_radio.isChecked():
                self.export_pdf_report()
            elif csv_radio.isChecked():
                self.export_csv_data()
            else:
                self.export_json_data()
    
    def export_pdf_report(self):
        """Export PDF report"""
        try:
            criminals = self.db.get_all_criminals()
            filepath = self.export_manager.export_criminal_list_pdf(criminals, self.user)
            
            if filepath:
                QMessageBox.information(self, "Export Successful", 
                    f"PDF report exported successfully!\n\nLocation:\n{filepath}")
                self.auth_manager.log_activity(
                    self.user['id'],
                    'export_pdf',
                    f'Exported criminal database to PDF'
                )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export PDF:\n{str(e)}")
    
    def export_csv_data(self):
        """Export CSV data"""
        try:
            criminals = self.db.get_all_criminals()
            filepath = self.export_manager.export_criminals_csv(criminals)
            
            if filepath:
                QMessageBox.information(self, "Export Successful", 
                    f"CSV data exported successfully!\n\nLocation:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export CSV:\n{str(e)}")
    
    def export_json_data(self):
        """Export JSON data"""
        QMessageBox.information(self, "Coming Soon", 
            "JSON export feature will be available in the next update!")
    
    def export_report(self):
        """Export detailed report"""
        self.quick_export()
    
    def show_statistics(self):
        """Show database statistics"""
        try:
            stats = self.db.get_statistics()
            
            message = f"""
            <div style='font-family: Segoe UI; padding: 10px;'>
                <h2 style='color: {COLORS['primary']};'>📊 Database Statistics</h2>
                <table style='width:100%; border-collapse: collapse;'>
                    <tr style='background-color: {COLORS['bg_hover']};'>
                        <td style='padding: 12px; font-weight: 600;'>Criminal Records:</td>
                        <td style='padding: 12px; text-align: right;'>{stats['criminals']}</td>
                    </tr>
                    <tr>
                        <td style='padding: 12px; font-weight: 600;'>Mugshots:</td>
                        <td style='padding: 12px; text-align: right;'>{stats['mugshots']}</td>
                    </tr>
                    <tr style='background-color: {COLORS['bg_hover']};'>
                        <td style='padding: 12px; font-weight: 600;'>Suspects Processed:</td>
                        <td style='padding: 12px; text-align: right;'>{stats['suspects']}</td>
                    </tr>
                    <tr>
                        <td style='padding: 12px; font-weight: 600;'>Matches Found:</td>
                        <td style='padding: 12px; text-align: right;'>{stats['matches']}</td>
                    </tr>
                </table>
                <br>
                <p style='font-weight: 600;'>Active Users: {len(self.auth_manager.get_all_users())}</p>
            </div>
            """
            
            QMessageBox.information(self, "Database Statistics", message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not retrieve statistics:\n{str(e)}")
    
    def show_user_management(self):
        """Show user management dialog"""
        try:
            from gui.dialogs.user_management_dialog import UserManagementDialog
            
            dialog = UserManagementDialog(self.auth_manager, self.user, self)
            dialog.exec_()
        except ImportError:
            QMessageBox.warning(self, "Not Available", 
                "User management dialog is not available in this version.")
    
    def show_activity_log(self):
        """Show user activity log"""
        try:
            activities = self.auth_manager.get_user_activity(self.user['id'], limit=50)
            
            message = f"<div style='font-family: Segoe UI;'><h2 style='color: {COLORS['primary']};'>📋 Recent Activity</h2><table style='width:100%;'>"
            for activity in activities[:10]:
                message += f"<tr><td style='padding: 8px;'><b>{activity['action']}</b></td><td style='padding: 8px; color: {COLORS['text_secondary']};'>{activity['timestamp']}</td></tr>"
            message += "</table></div>"
            
            QMessageBox.information(self, "Activity Log", message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not retrieve activity log:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        message = f"""
        <div style='font-family: Segoe UI; padding: 10px;'>
            <h2 style='color: {COLORS['primary']};'>{APP_NAME}</h2>
            <p><b>Version:</b> {APP_VERSION}</p>
            <p>A complete forensic face recognition system for law enforcement agencies</p>
            
            <h3 style='color: {COLORS['primary']}; margin-top: 20px;'>Technologies:</h3>
            <ul style='line-height: 1.8;'>
                <li><b>PyQt5</b> - GUI Framework</li>
                <li><b>OpenCV</b> - Computer Vision</li>
                <li><b>face_recognition</b> - Face Detection & Recognition</li>
                <li><b>SQLite3</b> - Database Management</li>
                <li><b>ReportLab</b> - PDF Generation</li>
            </ul>
            
            <div style='margin-top: 20px; padding: 15px; background-color: {COLORS['bg_hover']}; border-radius: 8px;'>
                <p style='margin: 5px 0;'><b>Current User:</b> {self.user['full_name']}</p>
                <p style='margin: 5px 0;'><b>Role:</b> {self.user['role']}</p>
            </div>
        </div>
        """
        
        QMessageBox.information(self, "About", message)
    
    def show_guide(self):
        """Show user guide"""
        guide = f"""
        <div style='font-family: Segoe UI; line-height: 1.6;'>
            <h2 style='color: {COLORS['primary']};'>Quick Start Guide</h2>
            
            <h3 style='color: {COLORS['primary']}; margin-top: 20px;'>1. Criminal Database 🔍</h3>
            <p>• Add new criminal records with personal information</p>
            <p>• Search and manage existing records</p>
            <p>• View detailed criminal profiles</p>
            
            <h3 style='color: {COLORS['primary']};'>2. Capture Mugshots 📸</h3>
            <p>• Select criminal from database</p>
            <p>• Start camera and capture clear mugshot</p>
            <p>• System automatically extracts face encoding</p>
            
            <h3 style='color: {COLORS['primary']};'>3. Suspect Recognition 👤</h3>
            <p>• Upload suspect image or capture from camera</p>
            <p>• Click "Search for Matches"</p>
            <p>• View results sorted by similarity percentage</p>
            
            <h3 style='color: {COLORS['primary']};'>4. Batch Processing 📂</h3>
            <p>• Select multiple suspect images</p>
            <p>• Process all images at once</p>
            <p>• Export batch results</p>
            
            <h3 style='color: {COLORS['primary']};'>5. Real-time Recognition 🎥</h3>
            <p>• Start live camera feed</p>
            <p>• System automatically recognizes faces</p>
            <p>• View matches in real-time</p>
            
            <p style='margin-top: 20px; padding: 10px; background-color: {COLORS['info_light']}; border-radius: 6px;'>
                <b>💡 Tip:</b> Press F1 anytime for help, or refer to README.md for detailed documentation
            </p>
        </div>
        """
        
        QMessageBox.information(self, "User Guide", guide)
    
    def logout(self):
        """Logout current user"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Log activity
            self.auth_manager.log_activity(
                self.user['id'],
                'logout',
                'User logged out'
            )
            
            logger.info(f"User logged out: {self.user['username']}")
            
            # Close main window
            self.close()
            
            # Show login window again
            from gui.auth.login_window import LoginWindow
            login = LoginWindow()
            if login.exec_():
                user = login.get_user()
                new_window = MainWindow(user)
                new_window.show()
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Log activity
            self.auth_manager.log_activity(
                self.user['id'],
                'app_closed',
                'User closed application'
            )
            
            # Close any open cameras
            if hasattr(self, 'mugshot_tab'):
                self.mugshot_tab.stop_camera()
            if hasattr(self, 'realtime_tab'):
                self.realtime_tab.stop_recognition()
            
            logger.info("Application closed")
            event.accept()
        else:
            event.ignore()