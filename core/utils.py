"""
Utility Functions for Forensic Face Recognition System
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from PIL import Image
from datetime import datetime
import json

from config.config import (
    MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT, MAX_IMAGE_SIZE,
    MIN_IMAGE_BRIGHTNESS, MAX_IMAGE_BRIGHTNESS,
    MIN_IMAGE_SHARPNESS, MIN_FACE_SIZE,
    ALLOWED_IMAGE_EXTENSIONS
)

logger = logging.getLogger(__name__)

# ============================================================================
# IMAGE VALIDATION
# ============================================================================

def validate_image_file(image_path):
    """
    Validate if file is a valid image
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        path = Path(image_path)
        
        # Check if file exists
        if not path.exists():
            return False, "File does not exist"
        
        # Check file extension
        if path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > MAX_IMAGE_SIZE:
            return False, f"File too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024):.1f}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Try to open image
        try:
            img = Image.open(image_path)
            img.verify()
        except Exception:
            return False, "Invalid or corrupted image file"
        
        return True, "Valid image"
        
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return False, str(e)

def validate_image_quality(image_path):
    """
    Validate image quality for face recognition
    
    Args:
        image_path (str): Path to image
        
    Returns:
        tuple: (bool, dict) - (is_valid, quality_metrics)
    """
    try:
        # Load image
        img = cv2.imread(str(image_path))
        
        if img is None:
            return False, {'error': 'Could not read image'}
        
        height, width = img.shape[:2]
        
        # Check dimensions
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            return False, {
                'error': f'Image too small. Minimum: {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}',
                'width': width,
                'height': height
            }
        
        # Calculate brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # Calculate sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Calculate contrast
        contrast = gray.std()
        
        quality_metrics = {
            'width': width,
            'height': height,
            'brightness': float(brightness),
            'sharpness': float(sharpness),
            'contrast': float(contrast)
        }
        
        # Validate metrics
        issues = []
        
        if brightness < MIN_IMAGE_BRIGHTNESS:
            issues.append('Image too dark')
        elif brightness > MAX_IMAGE_BRIGHTNESS:
            issues.append('Image too bright')
        
        if sharpness < MIN_IMAGE_SHARPNESS:
            issues.append('Image too blurry')
        
        if contrast < 30:
            issues.append('Image has low contrast')
        
        if issues:
            quality_metrics['issues'] = issues
            quality_metrics['warning'] = ', '.join(issues)
            return False, quality_metrics
        
        quality_metrics['status'] = 'Good quality'
        return True, quality_metrics
        
    except Exception as e:
        logger.error(f"Quality validation error: {e}")
        return False, {'error': str(e)}

def detect_face_in_image(image_path):
    """
    Check if image contains a detectable face
    
    Args:
        image_path (str): Path to image
        
    Returns:
        tuple: (bool, dict) - (has_face, face_info)
    """
    try:
        import face_recognition
        
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return False, {'error': 'No face detected in image'}
        
        if len(face_locations) > 1:
            return False, {
                'error': f'Multiple faces detected ({len(face_locations)})',
                'count': len(face_locations)
            }
        
        # Get face size
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        
        if face_width < MIN_FACE_SIZE or face_height < MIN_FACE_SIZE:
            return False, {
                'error': f'Face too small. Minimum: {MIN_FACE_SIZE}x{MIN_FACE_SIZE}px',
                'size': f'{face_width}x{face_height}'
            }
        
        return True, {
            'status': 'Face detected',
            'location': face_locations[0],
            'size': f'{face_width}x{face_height}'
        }
        
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return False, {'error': str(e)}

# ============================================================================
# IMAGE PROCESSING
# ============================================================================

def resize_image(image_path, max_width=800, max_height=800):
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image_path (str): Path to image
        max_width (int): Maximum width
        max_height (int): Maximum height
        
    Returns:
        np.ndarray: Resized image
    """
    try:
        img = cv2.imread(str(image_path))
        
        if img is None:
            return None
        
        height, width = img.shape[:2]
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height, 1.0)
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
        
    except Exception as e:
        logger.error(f"Image resize error: {e}")
        return None

def enhance_image(image):
    """
    Enhance image quality for better face recognition
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Enhanced image
    """
    try:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Apply slight sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Image enhancement error: {e}")
        return image

def crop_face_from_image(image_path, face_location, padding=20):
    """
    Crop face region from image
    
    Args:
        image_path (str): Path to image
        face_location (tuple): (top, right, bottom, left)
        padding (int): Padding around face
        
    Returns:
        np.ndarray: Cropped face image
    """
    try:
        img = cv2.imread(str(image_path))
        
        if img is None:
            return None
        
        top, right, bottom, left = face_location
        
        # Add padding
        height, width = img.shape[:2]
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(height, bottom + padding)
        right = min(width, right + padding)
        
        # Crop face
        face = img[top:bottom, left:right]
        
        return face
        
    except Exception as e:
        logger.error(f"Face crop error: {e}")
        return None

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def generate_unique_filename(prefix, extension='.jpg'):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return f"{prefix}_{timestamp}{extension}"

def save_image(image, directory, filename):
    """
    Save image to directory
    
    Args:
        image (np.ndarray): Image to save
        directory (Path): Directory path
        filename (str): Filename
        
    Returns:
        str: Full path to saved image
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / filename
        cv2.imwrite(str(filepath), image)
        logger.info(f"Image saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return None

def delete_file(filepath):
    """Delete file safely"""
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.info(f"File deleted: {filepath}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

# ============================================================================
# DATA FORMATTING
# ============================================================================

def format_datetime(dt_string):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_string

def format_file_size(size_bytes):
    """Format file size for display"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def calculate_similarity_color(similarity):
    """
    Get color based on similarity percentage
    
    Returns:
        str: Color name for Qt
    """
    if similarity >= 80:
        return 'green'
    elif similarity >= 70:
        return 'lightgreen'
    elif similarity >= 60:
        return 'yellow'
    elif similarity >= 50:
        return 'orange'
    else:
        return 'red'

# ============================================================================
# EXPORT HELPERS
# ============================================================================

def export_to_json(data, filepath):
    """Export data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=str)
        logger.info(f"Data exported to JSON: {filepath}")
        return True
    except Exception as e:
        logger.error(f"JSON export error: {e}")
        return False

def export_to_csv(data, filepath, headers):
    """Export data to CSV file"""
    try:
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Data exported to CSV: {filepath}")
        return True
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return False

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def is_valid_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Basic phone number validation"""
    import re
    pattern = r'^[\d\s\-\+\(\)]+$'
    return re.match(pattern, phone) is not None and len(phone) >= 10