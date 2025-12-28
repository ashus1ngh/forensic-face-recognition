"""
Theme Manager for UI Styling - Enhanced Version
"""

from config.config import LIGHT_THEME, DARK_THEME, COLORS

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.current_theme = 'Light'
        self.themes = {
            'Light': LIGHT_THEME,
            'Dark': DARK_THEME
        }
    
    def get_stylesheet(self, theme_name='Light'):
        """
        Get complete stylesheet for theme
        
        Args:
            theme_name (str): 'Light' or 'Dark'
            
        Returns:
            str: Qt stylesheet
        """
        theme = self.themes.get(theme_name, LIGHT_THEME)
        self.current_theme = theme_name
        
        if theme_name == 'Dark':
            return self._get_dark_stylesheet(theme)
        else:
            return self._get_light_stylesheet(theme)
    
    def _get_light_stylesheet(self, theme):
        """Generate light theme stylesheet with modern design"""
        return f"""
            /* ==================== MAIN WINDOW ==================== */
            QMainWindow {{
                background-color: #F5F7FA;
            }}
            
            /* ==================== CENTRAL WIDGET ==================== */
            QWidget {{
                background-color: #F5F7FA;
                color: {theme['foreground']};
                font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Roboto', Arial, sans-serif;
                font-size: 14px;
            }}
            
            /* ==================== TAB WIDGET - Modern Flat Design ==================== */
            QTabWidget::pane {{
                border: none;
                background-color: white;
                border-radius: 10px;
                padding: 5px;
            }}
            
            QTabBar {{
                background-color: transparent;
                border: none;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: #6B7280;
                padding: 14px 28px;
                margin-right: 4px;
                border: none;
                border-bottom: 3px solid transparent;
                font-weight: 600;
                font-size: 15px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            
            QTabBar::tab:selected {{
                background-color: white;
                color: {theme['primary']};
                border-bottom: 3px solid {theme['primary']};
            }}
            
            QTabBar::tab:hover {{
                background-color: #F3F4F6;
                color: {theme['primary']};
            }}
            
            /* ==================== LABELS ==================== */
            QLabel {{
                color: {theme['foreground']};
                background-color: transparent;
                font-size: 14px;
            }}
            
            /* ==================== LINE EDIT - Modern Input Fields ==================== */
            QLineEdit {{
                padding: 12px 16px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                color: {theme['foreground']};
                selection-background-color: {theme['primary']};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {theme['primary']};
                background-color: white;
            }}
            
            QLineEdit:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QLineEdit:disabled {{
                background-color: #F9FAFB;
                color: #9CA3AF;
                border: 2px solid #E5E7EB;
            }}
            
            /* ==================== TEXT EDIT ==================== */
            QTextEdit, QPlainTextEdit {{
                padding: 12px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                color: {theme['foreground']};
                selection-background-color: {theme['primary']};
                font-size: 14px;
            }}
            
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== SPIN BOX ==================== */
            QSpinBox, QDoubleSpinBox {{
                padding: 10px 14px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                color: {theme['foreground']};
                font-size: 14px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background-color: transparent;
                border-top-right-radius: 6px;
            }}
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border: none;
                background-color: transparent;
                border-bottom-right-radius: 6px;
            }}
            
            /* ==================== COMBO BOX - Modern Dropdown ==================== */
            QComboBox {{
                padding: 12px 16px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                color: {theme['foreground']};
                font-size: 14px;
                min-width: 150px;
            }}
            
            QComboBox:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QComboBox:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                padding-right: 10px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {theme['foreground']};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                selection-background-color: {theme['primary']};
                selection-color: white;
                padding: 6px;
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: #F3F4F6;
            }}
            
            /* ==================== BUTTONS - Modern Elevated Style ==================== */
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 13px 26px;
                font-weight: 600;
                font-size: 14px;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: #4A6B8A;
            }}
            
            QPushButton:pressed {{
                background-color: #3D5A73;
                padding-top: 15px;
                padding-bottom: 11px;
            }}
            
            QPushButton:disabled {{
                background-color: #E5E7EB;
                color: #9CA3AF;
            }}
            
            /* Secondary Button */
            QPushButton[class="secondary"] {{
                background-color: {theme['secondary']};
            }}
            
            QPushButton[class="secondary"]:hover {{
                background-color: #9A8A7E;
            }}
            
            /* Danger Button */
            QPushButton[class="danger"] {{
                background-color: {COLORS['danger']};
            }}
            
            QPushButton[class="danger"]:hover {{
                background-color: #C62828;
            }}
            
            /* Success Button */
            QPushButton[class="success"] {{
                background-color: {COLORS['success']};
            }}
            
            QPushButton[class="success"]:hover {{
                background-color: #45A049;
            }}
            
            /* ==================== TABLE WIDGET - Modern Grid ==================== */
            QTableWidget {{
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                background-color: white;
                gridline-color: #F3F4F6;
                selection-background-color: {theme['primary']};
                selection-color: white;
                alternate-background-color: #F9FAFB;
                font-size: 14px;
            }}
            
            QTableWidget::item {{
                padding: 14px 10px;
                border: none;
            }}
            
            QTableWidget::item:hover {{
                background-color: #F3F4F6;
            }}
            
            QTableWidget::item:selected {{
                background-color: {theme['primary']};
                color: white;
            }}
            
            QHeaderView {{
                background-color: transparent;
            }}
            
            QHeaderView::section {{
                background-color: #F9FAFB;
                color: #374151;
                padding: 14px 10px;
                border: none;
                border-bottom: 2px solid {theme['primary']};
                font-weight: 700;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            QHeaderView::section:hover {{
                background-color: #F3F4F6;
            }}
            
            /* ==================== PROGRESS BAR ==================== */
            QProgressBar {{
                border: none;
                border-radius: 10px;
                text-align: center;
                background-color: #F3F4F6;
                color: {theme['foreground']};
                font-weight: 600;
                height: 26px;
                font-size: 13px;
            }}
            
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['accent']});
                border-radius: 10px;
            }}
            
            /* ==================== MENU BAR ==================== */
            QMenuBar {{
                background-color: white;
                color: {theme['foreground']};
                padding: 6px;
                border-bottom: 1px solid #E5E7EB;
            }}
            
            QMenuBar::item {{
                padding: 10px 16px;
                background-color: transparent;
                border-radius: 6px;
                font-weight: 500;
            }}
            
            QMenuBar::item:selected {{
                background-color: #F3F4F6;
                color: {theme['primary']};
            }}
            
            QMenu {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 12px 32px 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme['primary']};
                color: white;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: #E5E7EB;
                margin: 8px 10px;
            }}
            
            /* ==================== STATUS BAR ==================== */
            QStatusBar {{
                background-color: white;
                color: {theme['foreground']};
                border-top: 1px solid #E5E7EB;
                padding: 6px;
                font-size: 13px;
            }}
            
            /* ==================== SCROLL BAR - Minimal Design ==================== */
            QScrollBar:vertical {{
                border: none;
                background-color: transparent;
                width: 12px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #D1D5DB;
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['primary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: transparent;
                height: 12px;
                margin: 0;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: #D1D5DB;
                border-radius: 6px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme['primary']};
            }}
            
            /* ==================== CHECK BOX ==================== */
            QCheckBox {{
                spacing: 10px;
                font-size: 14px;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid #D1D5DB;
                border-radius: 5px;
                background-color: white;
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme['primary']};
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== RADIO BUTTON ==================== */
            QRadioButton {{
                spacing: 10px;
                font-size: 14px;
            }}
            
            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid #D1D5DB;
                border-radius: 11px;
                background-color: white;
            }}
            
            QRadioButton::indicator:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: white;
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== GROUP BOX - Card Style ==================== */
            QGroupBox {{
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                margin-top: 18px;
                padding: 20px;
                font-weight: 600;
                font-size: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 5px 12px;
                background-color: white;
                color: {theme['primary']};
                border-radius: 5px;
            }}
            
            /* ==================== TOOLTIP ==================== */
            QToolTip {{
                background-color: #1F2937;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            
            /* ==================== SLIDER ==================== */
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background-color: #E5E7EB;
                border-radius: 3px;
            }}
            
            QSlider::handle:horizontal {{
                background-color: {theme['primary']};
                border: none;
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background-color: #4A6B8A;
            }}
        """
    
    def _get_dark_stylesheet(self, theme):
        """Generate dark theme stylesheet with modern design"""
        return f"""
            /* ==================== MAIN WINDOW ==================== */
            QMainWindow {{
                background-color: {theme['background']};
            }}
            
            /* ==================== CENTRAL WIDGET ==================== */
            QWidget {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Roboto', Arial, sans-serif;
                font-size: 14px;
            }}
            
            /* ==================== TAB WIDGET ==================== */
            QTabWidget::pane {{
                border: none;
                background-color: #252932;
                border-radius: 10px;
                padding: 5px;
            }}
            
            QTabBar {{
                background-color: transparent;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: #9CA3AF;
                padding: 14px 28px;
                margin-right: 4px;
                border: none;
                border-bottom: 3px solid transparent;
                font-weight: 600;
                font-size: 15px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            
            QTabBar::tab:selected {{
                background-color: #252932;
                color: {theme['primary']};
                border-bottom: 3px solid {theme['primary']};
            }}
            
            QTabBar::tab:hover {{
                background-color: #2F3542;
                color: {theme['primary']};
            }}
            
            /* ==================== LABELS ==================== */
            QLabel {{
                color: {theme['foreground']};
                background-color: transparent;
            }}
            
            /* ==================== LINE EDIT ==================== */
            QLineEdit {{
                padding: 12px 16px;
                border: 2px solid #3A3F4B;
                border-radius: 8px;
                background-color: #252932;
                color: {theme['foreground']};
                selection-background-color: {theme['primary']};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            QLineEdit:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QLineEdit:disabled {{
                background-color: #1F2328;
                color: #6B7280;
            }}
            
            /* ==================== TEXT EDIT ==================== */
            QTextEdit, QPlainTextEdit {{
                padding: 12px;
                border: 2px solid #3A3F4B;
                border-radius: 8px;
                background-color: #252932;
                color: {theme['foreground']};
                font-size: 14px;
            }}
            
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== SPIN BOX ==================== */
            QSpinBox, QDoubleSpinBox {{
                padding: 10px 14px;
                border: 2px solid #3A3F4B;
                border-radius: 8px;
                background-color: #252932;
                color: {theme['foreground']};
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== COMBO BOX ==================== */
            QComboBox {{
                padding: 12px 16px;
                border: 2px solid #3A3F4B;
                border-radius: 8px;
                background-color: #252932;
                color: {theme['foreground']};
                font-size: 14px;
            }}
            
            QComboBox:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {theme['foreground']};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: #252932;
                border: 1px solid #3A3F4B;
                border-radius: 8px;
                selection-background-color: {theme['primary']};
                selection-color: white;
                padding: 6px;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: #2F3542;
            }}
            
            /* ==================== BUTTONS ==================== */
            QPushButton {{
                background-color: {theme['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 13px 26px;
                font-weight: 600;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: #4A8AB8;
            }}
            
            QPushButton:pressed {{
                background-color: {theme['accent']};
            }}
            
            QPushButton:disabled {{
                background-color: #3A3F4B;
                color: #6B7280;
            }}
            
            /* ==================== TABLE WIDGET ==================== */
            QTableWidget {{
                border: 1px solid #3A3F4B;
                border-radius: 10px;
                background-color: #252932;
                gridline-color: #3A3F4B;
                selection-background-color: {theme['primary']};
                alternate-background-color: #2F3542;
                color: {theme['foreground']};
            }}
            
            QTableWidget::item {{
                padding: 14px 10px;
            }}
            
            QTableWidget::item:hover {{
                background-color: #2F3542;
            }}
            
            QHeaderView::section {{
                background-color: #1F2328;
                color: {theme['foreground']};
                padding: 14px 10px;
                border: none;
                border-bottom: 2px solid {theme['primary']};
                font-weight: 700;
                font-size: 13px;
            }}
            
            /* ==================== PROGRESS BAR ==================== */
            QProgressBar {{
                border: none;
                border-radius: 10px;
                text-align: center;
                background-color: #2F3542;
                color: white;
                font-weight: 600;
                height: 26px;
            }}
            
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['accent']});
                border-radius: 10px;
            }}
            
            /* ==================== MENU BAR ==================== */
            QMenuBar {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                padding: 6px;
                border-bottom: 1px solid #3A3F4B;
            }}
            
            QMenuBar::item {{
                padding: 10px 16px;
                background-color: transparent;
                border-radius: 6px;
            }}
            
            QMenuBar::item:selected {{
                background-color: #2F3542;
                color: {theme['primary']};
            }}
            
            QMenu {{
                background-color: #252932;
                color: {theme['foreground']};
                border: 1px solid #3A3F4B;
                border-radius: 10px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 12px 32px 12px 24px;
                border-radius: 6px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme['primary']};
            }}
            
            /* ==================== STATUS BAR ==================== */
            QStatusBar {{
                background-color: {theme['background']};
                color: {theme['foreground']};
                border-top: 1px solid #3A3F4B;
                padding: 6px;
            }}
            
            /* ==================== SCROLL BAR ==================== */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 12px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #3A3F4B;
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['primary']};
            }}
            
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 12px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: #3A3F4B;
                border-radius: 6px;
            }}
            
            /* ==================== CHECK BOX ==================== */
            QCheckBox {{
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid #3A3F4B;
                border-radius: 5px;
                background-color: #252932;
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid {theme['primary']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme['primary']};
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== RADIO BUTTON ==================== */
            QRadioButton {{
                spacing: 10px;
            }}
            
            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid #3A3F4B;
                border-radius: 11px;
                background-color: #252932;
            }}
            
            QRadioButton::indicator:checked {{
                border: 2px solid {theme['primary']};
            }}
            
            /* ==================== GROUP BOX ==================== */
            QGroupBox {{
                background-color: #252932;
                border: 1px solid #3A3F4B;
                border-radius: 10px;
                margin-top: 18px;
                padding: 20px;
                font-weight: 600;
                font-size: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 12px;
                background-color: #252932;
                color: {theme['primary']};
            }}
            
            /* ==================== SLIDER ==================== */
            QSlider::groove:horizontal {{
                height: 6px;
                background-color: #3A3F4B;
                border-radius: 3px;
            }}
            
            QSlider::handle:horizontal {{
                background-color: {theme['primary']};
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }}
        """