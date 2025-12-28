"""
Forensic Face Recognition System
Main Application Entry Point
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forensic_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import configuration
from config.config import APP_NAME, APP_VERSION, create_directories

# Import authentication
from gui.auth.login_window import LoginWindow
from gui.main_window import MainWindow

def show_splash_screen(app):
    """Show splash screen during startup"""
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor("#49759c"))
    
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    
    font = QFont("Arial", 16, QFont.Bold)
    splash.setFont(font)
    
    splash.showMessage(
        f"{APP_NAME}\nVersion {APP_VERSION}\n\nInitializing...",
        Qt.AlignCenter | Qt.AlignVCenter,
        Qt.white
    )
    
    splash.show()
    app.processEvents()
    
    return splash

def main():
    """Main application function"""
    try:
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Create required directories
        create_directories()
        logger.info("Required directories created/verified")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        # Show splash screen
        splash = show_splash_screen(app)
        
        # Simulate loading time
        QTimer.singleShot(1000, splash.close)
        
        # Show login window
        login = LoginWindow()
        
        if login.exec_():  # PyQt5 uses exec_() instead of exec()
            # Get logged in user
            user = login.get_user()
            logger.info(f"User logged in: {user['username']} ({user['role']})")
            
            # Close splash and show main window
            splash.finish(login)
            
            # Create and show main window
            window = MainWindow(user)
            window.show()
            
            logger.info("Main window displayed")
            
            # Execute application
            sys.exit(app.exec_())  # PyQt5 uses exec_() instead of exec()
        else:
            logger.info("Login cancelled by user")
            sys.exit(0)
            
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()