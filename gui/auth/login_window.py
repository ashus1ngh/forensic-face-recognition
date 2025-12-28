# gui/auth/login_window.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal
import logging

from database.auth_manager import AuthManager
from config.config import APP_NAME, COLORS

logger = logging.getLogger(__name__)

class LoginWindow(QDialog):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME} - Login")
        self.setFixedSize(550, 900)
        
        # Apply modern theme stylesheet
        self.setStyleSheet(self._get_login_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget for centering
        container = QFrame()
        container.setObjectName("loginContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(30)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        # ==================== HEADER SECTION ====================
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(30, 30, 30, 30)
        
        # App icon/logo placeholder
        logo_label = QLabel("🔐")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 56px; background: transparent;")
        header_layout.addWidget(logo_label)
        
        # Title
        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Secure Access Portal")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitleLabel")
        header_layout.addWidget(subtitle)
        
        container_layout.addWidget(header_frame)
        
        # ==================== FORM SECTION ====================
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Username field
        username_container = QVBoxLayout()
        username_container.setSpacing(8)
        
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        username_container.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setObjectName("inputField")
        self.username_input.setMinimumHeight(48)
        username_container.addWidget(self.username_input)
        
        form_layout.addLayout(username_container)
        
        # Password field
        password_container = QVBoxLayout()
        password_container.setSpacing(8)
        
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        password_container.addWidget(password_label)
        
        password_input_container = QFrame()
        password_input_layout = QHBoxLayout(password_input_container)
        password_input_layout.setContentsMargins(0, 0, 0, 0)
        password_input_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("inputField")
        self.password_input.setMinimumHeight(48)
        self.password_input.returnPressed.connect(self.login)
        password_input_layout.addWidget(self.password_input)
        
        password_container.addWidget(password_input_container)
        form_layout.addLayout(password_container)
        
        # Show password toggle
        show_password_layout = QHBoxLayout()
        show_password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.show_password_btn = QPushButton("👁 Show Password")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setObjectName("toggleButton")
        self.show_password_btn.toggled.connect(self.toggle_password)
        self.show_password_btn.setCursor(Qt.PointingHandCursor)
        show_password_layout.addWidget(self.show_password_btn)
        show_password_layout.addStretch()
        
        form_layout.addLayout(show_password_layout)
        form_layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("🔐 Login")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.setMinimumHeight(52)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)
        form_layout.addWidget(self.login_btn)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        form_layout.addWidget(cancel_btn)
        
        container_layout.addWidget(form_frame)
        
        # ==================== FOOTER SECTION ====================
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        # Warning info
        warning_container = QHBoxLayout()
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 16px;")
        warning_container.addWidget(warning_icon)
        
        info_label = QLabel("You have only 3 login attempts before account lockout")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        warning_container.addWidget(info_label, 1)
        
        footer_layout.addLayout(warning_container)
        
        container_layout.addWidget(footer_frame)
        
        # Add shadow effect to form frame
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        form_frame.setGraphicsEffect(shadow)
        
        # Add shadow to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(5)
        header_shadow.setColor(QColor(0, 0, 0, 30))
        header_frame.setGraphicsEffect(header_shadow)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Set focus
        self.username_input.setFocus()
    
    def _get_login_stylesheet(self):
        """Generate modern login window stylesheet"""
        return f"""
            /* ==================== MAIN DIALOG ==================== */
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
            
            #loginContainer {{
                background-color: transparent;
            }}
            
            /* ==================== HEADER FRAME ==================== */
            #headerFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']}, 
                    stop:1 {COLORS['primary_dark']});
                border-radius: 12px;
            }}
            
            #titleLabel {{
                color: white;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 0.5px;
                background: transparent;
            }}
            
            #subtitleLabel {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 15px;
                font-weight: 500;
                background: transparent;
            }}
            
            /* ==================== FORM FRAME ==================== */
            #formFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid {COLORS['border_light']};
            }}
            
            #fieldLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }}
            
            /* ==================== INPUT FIELDS ==================== */
            #inputField {{
                padding: 14px 18px;
                border: 2px solid {COLORS['border_light']};
                border-radius: 8px;
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                font-size: 15px;
                selection-background-color: {COLORS['primary']};
            }}
            
            #inputField:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: white;
            }}
            
            #inputField:hover {{
                border: 2px solid {COLORS['primary_light']};
            }}
            
            /* ==================== TOGGLE BUTTON ==================== */
            #toggleButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: none;
                text-align: left;
                font-size: 13px;
                font-weight: 500;
                padding: 5px 0px;
            }}
            
            #toggleButton:hover {{
                color: {COLORS['primary_dark']};
                text-decoration: underline;
            }}
            
            #toggleButton:checked {{
                color: {COLORS['primary_dark']};
            }}
            
            /* ==================== PRIMARY BUTTON ==================== */
            #primaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, 
                    stop:1 {COLORS['primary_dark']});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            
            #primaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary_dark']}, 
                    stop:1 {COLORS['primary']});
            }}
            
            #primaryButton:pressed {{
                background-color: {COLORS['primary_dark']};
                padding-top: 18px;
                padding-bottom: 14px;
            }}
            
            #primaryButton:disabled {{
                background-color: {COLORS['border_medium']};
                color: {COLORS['text_tertiary']};
            }}
            
            /* ==================== SECONDARY BUTTON ==================== */
            #secondaryButton {{
                background-color: white;
                color: {COLORS['text_secondary']};
                border: 2px solid {COLORS['border_light']};
                border-radius: 8px;
                padding: 14px;
                font-size: 15px;
                font-weight: 600;
            }}
            
            #secondaryButton:hover {{
                background-color: {COLORS['bg_hover']};
                border: 2px solid {COLORS['border_medium']};
                color: {COLORS['text_primary']};
            }}
            
            #secondaryButton:pressed {{
                background-color: {COLORS['border_light']};
            }}
            
            /* ==================== FOOTER FRAME ==================== */
            #footerFrame {{
                background-color: {COLORS['warning_light']};
                border-radius: 8px;
                border: 1px solid {COLORS['warning']};
            }}
            
            #infoLabel {{
                color: {COLORS['text_secondary']};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """
    
    def toggle_password(self, checked):
        """Toggle password visibility"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈 Hide Password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁 Show Password")
    
    def login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self._show_error_message("Missing Information", 
                                    "Please enter both username and password")
            return
        
        # Disable login button during authentication
        self.login_btn.setEnabled(False)
        self.login_btn.setText("🔄 Authenticating...")
        
        # Authenticate user
        user = self.auth_manager.authenticate(username, password)
        
        # Re-enable button
        self.login_btn.setEnabled(True)
        self.login_btn.setText("🔐 Login")
        
        if user:
            self.user = user
            logger.info(f"Login successful: {username}")
            self.auth_manager.log_activity(user['id'], 'login', 'User logged in')
            
            self._show_success_message("Login Successful", 
                                      f"Welcome back, {user['full_name']}!\n\nRole: {user['role']}")
            self.accept()
        else:
            logger.warning(f"Login failed: {username}")
            self._show_error_message("Authentication Failed", 
                                    "Invalid username or password.\n\n"
                                    "⚠️ Your account will be locked after 3 failed attempts.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def _show_success_message(self, title, message):
        """Show success message with modern styling"""
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
        """Show error message with modern styling"""
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
    
    def get_user(self):
        """Return authenticated user"""
        return self.user