"""
Configuration Settings for Forensic Face Recognition System
Complete Configuration with Enhanced UI Colors and Styling
"""

import os
from pathlib import Path

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_NAME = "Forensic Face\n Recognition System"
APP_VERSION = "2.0.0"
ORGANIZATION = "Law Enforcement Agency"

# ============================================================================
# WINDOW SETTINGS
# ============================================================================

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1400
MIN_WINDOW_HEIGHT = 700

# ============================================================================
# PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "database.db"

# Image directories
MUGSHOTS_DIR = DATA_DIR / "mugshots"
SUSPECTS_DIR = DATA_DIR / "suspects"
EXPORTS_DIR = DATA_DIR / "exports"
TEMP_DIR = DATA_DIR / "temp"

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DB_TIMEOUT = 30
DB_CHECK_SAME_THREAD = False
MAX_CONNECTIONS = 10

# ============================================================================
# FACE RECOGNITION SETTINGS
# ============================================================================

# Face detection model: 'hog' (faster) or 'cnn' (more accurate, needs GPU)
FACE_DETECTION_MODEL = 'hog'

# Face matching threshold (0-1, lower = stricter)
FACE_MATCH_THRESHOLD = 0.6

# Minimum similarity percentage for matches
FACE_MATCH_PERCENTAGE = 60.0

# Number of times to resample face for encoding (higher = more accurate but slower)
NUM_JITTERS = 1

# Maximum faces to detect in single image
MAX_FACES_PER_IMAGE = 10

# Image quality settings
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Face detection minimum size
MIN_FACE_SIZE = 80  # pixels

# ============================================================================
# CAMERA SETTINGS
# ============================================================================

CAMERA_INDEX = 0  # 0 for default webcam
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Real-time recognition settings
REALTIME_RECOGNITION_INTERVAL = 1000  # milliseconds
REALTIME_CONFIDENCE_THRESHOLD = 70.0

# ============================================================================
# BATCH PROCESSING SETTINGS
# ============================================================================

BATCH_MAX_IMAGES = 50
BATCH_THREAD_COUNT = 4
BATCH_TIMEOUT = 300  # seconds

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

EXPORT_PDF_DPI = 300
EXPORT_IMAGE_QUALITY = 95
EXPORT_INCLUDE_IMAGES = True
EXPORT_INCLUDE_TIMESTAMPS = True

# PDF Report settings
PDF_TITLE_FONT_SIZE = 24
PDF_HEADING_FONT_SIZE = 16
PDF_TEXT_FONT_SIZE = 12

# ============================================================================
# AUTHENTICATION SETTINGS
# ============================================================================

# User roles
ROLE_ADMIN = "Admin"
ROLE_INVESTIGATING_HEAD = "Investigating Head"
ROLE_INVESTIGATING_OFFICER = "Investigating Officer"

ROLES = [ROLE_ADMIN, ROLE_INVESTIGATING_HEAD, ROLE_INVESTIGATING_OFFICER]

# Role permissions
PERMISSIONS = {
    ROLE_ADMIN: [
        'add_criminal', 'edit_criminal', 'delete_criminal',
        'add_mugshot', 'delete_mugshot',
        'recognize_suspect', 'batch_process',
        'view_results', 'export_results',
        'manage_users', 'view_statistics',
        'change_settings', 'realtime_recognition'
    ],
    ROLE_INVESTIGATING_HEAD: [
        'add_criminal', 'edit_criminal', 'delete_criminal',
        'add_mugshot', 'delete_mugshot',
        'recognize_suspect', 'batch_process',
        'view_results', 'export_results',
        'view_statistics', 'realtime_recognition'
    ],
    ROLE_INVESTIGATING_OFFICER: [
        'add_criminal', 'add_mugshot',
        'recognize_suspect', 'batch_process',
        'view_results', 'export_results',
        'realtime_recognition'
    ]
}

# Session settings
SESSION_TIMEOUT = 3600  # seconds (1 hour)
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # seconds (5 minutes)

# ============================================================================
# UI THEME SETTINGS - ENHANCED MODERN COLORS
# ============================================================================

# Enhanced Color palette - Modern and Professional
COLORS = {
    # Primary colors - Blue tones for professional look
    'primary': "#5B8FB9",  # Modern blue
    'primary_dark': "#4A6B8A",  # Darker blue for hover
    'primary_light': "#7BA8CC",  # Lighter blue
    
    # Secondary colors - Warm neutrals
    'secondary': '#AD9C8E',  # Warm taupe
    'secondary_dark': '#9A8A7E',  # Darker taupe
    
    # Accent colors
    'accent': '#D9BBB0',  # Soft rose
    'accent_light': "#E8D5CD",  # Lighter rose
    
    # Background colors
    'bg_primary': "#F5F7FA",  # Very light blue-grey
    'bg_secondary': "#FFFFFF",  # Pure white
    'bg_card': "#FFFFFF",  # Card background
    'bg_hover': "#F3F4F6",  # Hover state
    
    # Text colors
    'text_primary': "#1F2937",  # Almost black
    'text_secondary': "#6B7280",  # Medium grey
    'text_tertiary': "#9CA3AF",  # Light grey
    'text_white': "#FFFFFF",  # White text
    
    # Border colors
    'border_light': '#E5E7EB',  # Very light grey
    'border_medium': '#D1D5DB',  # Medium grey
    'border_dark': '#9CA3AF',  # Dark grey
    
    # Status colors - Modern vibrant tones
    'success': '#10B981',  # Modern green
    'success_light': '#D1FAE5',  # Light green bg
    'warning': '#F59E0B',  # Amber
    'warning_light': '#FEF3C7',  # Light amber bg
    'danger': "#EF4444",  # Modern red
    'danger_light': '#FEE2E2',  # Light red bg
    'info': "#3B82F6",  # Bright blue
    'info_light': '#DBEAFE',  # Light blue bg
    
    # Dark theme colors
    'dark_bg': '#1A1D23',  # Very dark blue-grey
    'dark_surface': '#252932',  # Dark surface
    'dark_border': '#3A3F4B',  # Dark border
    'dark_text': "#E4E7EB85",  # Light text for dark mode
}

# Light theme - Modern and clean
LIGHT_THEME = {
    'name': 'Light',
    'background': COLORS['bg_primary'],
    'surface': COLORS['bg_secondary'],
    'foreground': COLORS['text_primary'],
    'primary': COLORS['primary'],
    'primary_dark': COLORS['primary_dark'],
    'secondary': COLORS['secondary'],
    'accent': COLORS['accent'],
    'border': COLORS['border_light'],
    'button_bg': COLORS['primary'],
    'button_hover': COLORS['primary_dark'],
    'table_alternate': COLORS['bg_hover'],
    'text_secondary': COLORS['text_secondary'],
    'success': COLORS['success'],
    'warning': COLORS['warning'],
    'danger': COLORS['danger'],
    'info': COLORS['info'],
    'info_light':COLORS['info_light'],
}

# Dark theme - Modern and elegant
DARK_THEME = {
    'name': 'Dark',
    'background': COLORS['dark_bg'],
    'surface': COLORS['dark_surface'],
    'foreground': COLORS['dark_text'],
    'primary': "#5798C4",
    'primary_dark': "#4A8AB8",
    'secondary': '#E74C3C',
    'accent': '#F39C12',
    'border': COLORS['dark_border'],
    'button_bg': COLORS['dark_surface'],
    'button_hover': '#3498DB',
    'table_alternate': '#2F3542',
    'text_secondary': '#9CA3AF',
    'success': COLORS['success'],
    'warning': COLORS['warning'],
    'danger': COLORS['danger'],
    'info': COLORS['info'],
    'info_light':COLORS['dark_bg'],
}

DEFAULT_THEME = 'Light'

# ============================================================================
# TYPOGRAPHY SETTINGS - ENHANCED
# ============================================================================

FONTS = {
    'primary': 'Segoe UI, SF Pro Display, Inter, Roboto, Arial, sans-serif',
    'monospace': 'Consolas, Monaco, Courier New, monospace',
    'size_xs': 11,
    'size_sm': 13,
    'size_base': 14,
    'size_lg': 16,
    'size_xl': 18,
    'size_2xl': 24,
    'size_3xl': 32,
}

# ============================================================================
# SPACING SETTINGS - CONSISTENT DESIGN
# ============================================================================

SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    '2xl': 24,
    '3xl': 32,
    '4xl': 48,
}

# ============================================================================
# BORDER RADIUS - MODERN ROUNDED CORNERS
# ============================================================================

BORDER_RADIUS = {
    'sm': 4,
    'md': 6,
    'lg': 8,
    'xl': 10,
    '2xl': 12,
    'full': 9999,
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_LEVEL = 'INFO'
LOG_FILE = 'forensic_system.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# VALIDATION SETTINGS
# ============================================================================

# Image quality validation
VALIDATE_IMAGE_QUALITY = True
MIN_IMAGE_BRIGHTNESS = 30
MAX_IMAGE_BRIGHTNESS = 250
MIN_IMAGE_SHARPNESS = 100

# Face validation
VALIDATE_FACE_QUALITY = True
MIN_FACE_CONFIDENCE = 0.8

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

ENABLE_CACHING = True
CACHE_SIZE = 100  # Number of face encodings to cache
ENABLE_PARALLEL_PROCESSING = True

# ============================================================================
# FILE EXTENSIONS
# ============================================================================

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']
EXPORT_FORMATS = ['PDF', 'CSV', 'JSON']

# ============================================================================
# STATUS CODES
# ============================================================================

STATUS_ACTIVE = 'active'
STATUS_INACTIVE = 'inactive'
STATUS_ARCHIVED = 'archived'

CRIMINAL_STATUSES = [STATUS_ACTIVE, STATUS_INACTIVE, STATUS_ARCHIVED]

# ============================================================================
# CONSTANTS FOR UI - ENHANCED WITH MODERN ICONS
# ============================================================================

# Status messages
MSG_SUCCESS = "✓ Operation completed successfully"
MSG_ERROR = "✗ An error occurred"
MSG_WARNING = "⚠ Warning"
MSG_INFO = "ℹ Information"

# Button labels - Modern with icons
BTN_ADD = "＋ Add"
BTN_EDIT = "✎ Edit"
BTN_DELETE = "🗑 Delete"
BTN_SAVE = "💾 Save"
BTN_CANCEL = "✕ Cancel"
BTN_SEARCH = "🔍 Search"
BTN_EXPORT = "📤 Export"
BTN_REFRESH = "⟳ Refresh"
BTN_UPLOAD = "⬆ Upload"
BTN_DOWNLOAD = "⬇ Download"

# Tab icons
ICON_CRIMINAL = "👤"
ICON_MUGSHOT = "📸"
ICON_RECOGNITION = "🔍"
ICON_BATCH = "📂"
ICON_REALTIME = "🎥"
ICON_RESULTS = "✓"
ICON_SETTINGS = "⚙"
ICON_DASHBOARD = "📊"
ICON_REPORTS = "📄"
ICON_USERS = "👥"

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_BATCH_PROCESSING = True
ENABLE_REALTIME_RECOGNITION = True
ENABLE_EXPORT_PDF = True
ENABLE_EXPORT_CSV = True
ENABLE_EXPORT_JSON = True
ENABLE_IMAGE_VALIDATION = True
ENABLE_ACTIVITY_LOGGING = True
ENABLE_USER_MANAGEMENT = True

# ============================================================================
# DEBUG SETTINGS
# ============================================================================

DEBUG_MODE = False
VERBOSE_LOGGING = False
SHOW_FPS = False
SHOW_PROCESSING_TIME = True

# ============================================================================
# VERSION INFORMATION
# ============================================================================

VERSION_INFO = {
    'major': 2,
    'minor': 0,
    'patch': 0,
    'release_date': '2024-11-26',
    'codename': 'Phoenix'
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_directories():
    """Create all required directories if they don't exist"""
    directories = [
        DATA_DIR,
        MUGSHOTS_DIR,
        SUSPECTS_DIR,
        EXPORTS_DIR,
        TEMP_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
    print(f"✓ Directories created/verified:")
    for directory in directories:
        print(f"  - {directory}")

def get_user_permissions(role):
    """
    Get permissions for a user role
    
    Args:
        role (str): User role
        
    Returns:
        list: List of permissions
    """
    return PERMISSIONS.get(role, [])

def has_permission(role, permission):
    """
    Check if a role has a specific permission
    
    Args:
        role (str): User role
        permission (str): Permission to check
        
    Returns:
        bool: True if role has permission
    """
    return permission in get_user_permissions(role)

def get_database_info():
    """Get database configuration information"""
    return {
        'path': str(DATABASE_PATH),
        'timeout': DB_TIMEOUT,
        'max_connections': MAX_CONNECTIONS
    }

def get_camera_config():
    """Get camera configuration"""
    return {
        'index': CAMERA_INDEX,
        'width': CAMERA_WIDTH,
        'height': CAMERA_HEIGHT,
        'fps': CAMERA_FPS
    }

def get_recognition_config():
    """Get face recognition configuration"""
    return {
        'detection_model': FACE_DETECTION_MODEL,
        'match_threshold': FACE_MATCH_THRESHOLD,
        'match_percentage': FACE_MATCH_PERCENTAGE,
        'num_jitters': NUM_JITTERS,
        'max_faces': MAX_FACES_PER_IMAGE
    }

def get_batch_config():
    """Get batch processing configuration"""
    return {
        'max_images': BATCH_MAX_IMAGES,
        'thread_count': BATCH_THREAD_COUNT,
        'timeout': BATCH_TIMEOUT
    }

def get_color(color_name):
    """
    Get color value by name
    
    Args:
        color_name (str): Name of color from COLORS dict
        
    Returns:
        str: Hex color code
    """
    return COLORS.get(color_name, COLORS['primary'])

def get_font_size(size_name):
    """
    Get font size by name
    
    Args:
        size_name (str): Name of size from FONTS dict
        
    Returns:
        int: Font size in points
    """
    return FONTS.get(f'size_{size_name}', FONTS['size_base'])

def get_spacing(size_name):
    """
    Get spacing value by name
    
    Args:
        size_name (str): Name of spacing from SPACING dict
        
    Returns:
        int: Spacing in pixels
    """
    return SPACING.get(size_name, SPACING['md'])

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check paths
    if not BASE_DIR.exists():
        errors.append(f"Base directory does not exist: {BASE_DIR}")
    
    # Check numeric ranges
    if not (0 <= FACE_MATCH_THRESHOLD <= 1):
        errors.append("FACE_MATCH_THRESHOLD must be between 0 and 1")
    
    if not (0 <= FACE_MATCH_PERCENTAGE <= 100):
        errors.append("FACE_MATCH_PERCENTAGE must be between 0 and 100")
    
    if BATCH_THREAD_COUNT < 1:
        errors.append("BATCH_THREAD_COUNT must be at least 1")
    
    # Check required roles
    if not all(role in PERMISSIONS for role in ROLES):
        errors.append("All roles must have defined permissions")
    
    return len(errors) == 0, errors

def print_config():
    """Print current configuration (for debugging)"""
    print("\n" + "="*60)
    print(f"{APP_NAME} v{APP_VERSION}")
    print("="*60)
    print(f"\nApplication Settings:")
    print(f"  Organization: {ORGANIZATION}")
    print(f"  Window Size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    print(f"\nPaths:")
    print(f"  Base: {BASE_DIR}")
    print(f"  Database: {DATABASE_PATH}")
    print(f"  Mugshots: {MUGSHOTS_DIR}")
    print(f"  Suspects: {SUSPECTS_DIR}")
    print(f"  Exports: {EXPORTS_DIR}")
    
    print(f"\nFace Recognition:")
    print(f"  Detection Model: {FACE_DETECTION_MODEL}")
    print(f"  Match Threshold: {FACE_MATCH_THRESHOLD}")
    print(f"  Match Percentage: {FACE_MATCH_PERCENTAGE}%")
    print(f"  Num Jitters: {NUM_JITTERS}")
    
    print(f"\nCamera:")
    print(f"  Index: {CAMERA_INDEX}")
    print(f"  Resolution: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    print(f"  FPS: {CAMERA_FPS}")
    
    print(f"\nBatch Processing:")
    print(f"  Max Images: {BATCH_MAX_IMAGES}")
    print(f"  Thread Count: {BATCH_THREAD_COUNT}")
    print(f"  Timeout: {BATCH_TIMEOUT}s")
    
    print(f"\nAuthentication:")
    print(f"  Roles: {', '.join(ROLES)}")
    print(f"  Session Timeout: {SESSION_TIMEOUT}s")
    print(f"  Max Login Attempts: {MAX_LOGIN_ATTEMPTS}")
    
    print(f"\nTheme:")
    print(f"  Default: {DEFAULT_THEME}")
    print(f"  Available: Light, Dark")
    
    print("\n" + "="*60 + "\n")

def get_version_string():
    """Get formatted version string"""
    v = VERSION_INFO
    return f"{v['major']}.{v['minor']}.{v['patch']}"

def get_full_version_info():
    """Get complete version information"""
    return f"{APP_NAME} v{get_version_string()} ({VERSION_INFO['codename']}) - {VERSION_INFO['release_date']}"

# ============================================================================
# SYSTEM REQUIREMENTS CHECK
# ============================================================================

def check_system_requirements():
    """Check if system meets minimum requirements"""
    import sys
    import platform
    
    requirements_met = True
    issues = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        requirements_met = False
        issues.append(f"Python 3.8+ required (found {python_version.major}.{python_version.minor})")
    
    # Check OS
    os_name = platform.system()
    if os_name not in ['Windows', 'Linux', 'Darwin']:
        issues.append(f"Unsupported OS: {os_name}")
    
    # Check available memory (basic check)
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.total < 8 * 1024 * 1024 * 1024:  # 8GB
            issues.append("Recommended: 8GB+ RAM")
    except ImportError:
        pass
    
    return requirements_met, issues

# Auto-create directories on import
try:
    create_directories()
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# Validate configuration on import
if DEBUG_MODE:
    valid, errors = validate_config()
    if not valid:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration validated successfully")