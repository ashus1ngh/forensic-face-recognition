"""
Lightweight face recognition using OpenCV - Optimized for Speed
"""
import cv2
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FaceRecognitionEngine:
    """Fast face recognition engine using OpenCV"""
    
    def __init__(self):
        # Use OpenCV Haar Cascade for speed
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        # OpenCV LBPH Face Recognizer for matching
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1, neighbors=8, grid_x=8, grid_y=8, threshold=100
        )
        
        self.known_encodings = []
        self.known_names = []
        self.known_images_dir = Path("data/mugshots")
        
        logger.info("FaceRecognitionEngine initialized (OpenCV mode)")
    
    def detect_faces_opencv(self, frame):
        """
        Detect faces in OpenCV frame - Required by MugshotCaptureTab
        Returns: List of (x, y, w, h) tuples
        """
        if frame is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces  # Returns list of (x, y, w, h)
    
    def get_face_encoding_from_cv2(self, frame):
        """
        Extract face encoding from OpenCV frame - Required by MugshotCaptureTab
        Returns: Face encoding (numpy array) or None
        """
        if frame is None:
            return None
        
        faces = self.detect_faces_opencv(frame)
        
        if len(faces) == 0:
            logger.warning("No face detected in frame")
            return None
        
        # Use the largest face
        if len(faces) > 1:
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        
        x, y, w, h = faces[0]
        
        # Extract face region
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to standard size for consistency
        face_roi = cv2.resize(face_roi, (100, 100))
        
        # Create encoding using histogram
        encoding = self._create_face_encoding(face_roi)
        
        return encoding
    
    def _create_face_encoding(self, face_image):
        """Create a simple face encoding using histogram and features"""
        # Calculate histogram
        hist = cv2.calcHist([face_image], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Calculate HOG features for better encoding
        hog = cv2.HOGDescriptor((100, 100), (20, 20), (10, 10), (10, 10), 9)
        hog_features = hog.compute(face_image).flatten()
        
        # Combine histogram and HOG features
        encoding = np.concatenate([hist[:64], hog_features[:64]])
        
        return encoding
    
    def extract_faces(self, image_path):
        """Extract faces from an image file"""
        image = cv2.imread(str(image_path))
        if image is None:
            return []
        
        faces = self.detect_faces_opencv(image)
        
        # Convert to (top, right, bottom, left) format
        return [(y, x+w, y+h, x) for x, y, w, h in faces]
    
    def encode_face(self, image_path):
        """Encode a face from an image file"""
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        
        return self.get_face_encoding_from_cv2(image)
    
    def compare_faces(self, encoding1, encoding2, tolerance=0.6):
        """
        Compare two face encodings
        Returns: True if faces match, False otherwise
        """
        if encoding1 is None or encoding2 is None:
            return False
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(encoding1 - encoding2)
        
        # Normalize distance (encodings are ~128 dimensional)
        max_distance = np.sqrt(len(encoding1))
        normalized_distance = distance / max_distance
        
        return normalized_distance < tolerance
    
    def calculate_similarity(self, encoding1, encoding2):
        """
        Calculate similarity score between two encodings
        Returns: Similarity score (0-100)
        """
        if encoding1 is None or encoding2 is None:
            return 0.0
        
        # Calculate distance
        distance = np.linalg.norm(encoding1 - encoding2)
        max_distance = np.sqrt(len(encoding1))
        normalized_distance = distance / max_distance
        
        # Convert to similarity percentage (0-100)
        similarity = max(0, (1 - normalized_distance) * 100)
        
        return similarity
    
    def recognize_face(self, image_path, known_encodings_dict, tolerance=0.6):
        """
        Recognize a face against known encodings
        Args:
            image_path: Path to image
            known_encodings_dict: List of dicts with 'encoding', 'name', 'criminal_id'
            tolerance: Match threshold
        Returns: Dict with match results
        """
        # Get encoding from image
        test_encoding = self.encode_face(image_path)
        
        if test_encoding is None:
            return {
                "matched": False,
                "name": "Unknown",
                "confidence": 0.0,
                "criminal_id": None
            }
        
        if not known_encodings_dict:
            return {
                "matched": False,
                "name": "Unknown", 
                "confidence": 0.0,
                "criminal_id": None
            }
        
        # Find best match
        best_match = None
        best_similarity = 0.0
        
        for known_face in known_encodings_dict:
            if known_face['encoding'] is None:
                continue
            
            similarity = self.calculate_similarity(test_encoding, known_face['encoding'])
            
            if similarity > best_similarity and similarity >= (tolerance * 100):
                best_similarity = similarity
                best_match = known_face
        
        if best_match:
            return {
                "matched": True,
                "name": best_match.get('name', 'Unknown'),
                "confidence": best_similarity,
                "criminal_id": best_match.get('criminal_id'),
                "criminal_code": best_match.get('criminal_code')
            }
        
        return {
            "matched": False,
            "name": "Unknown",
            "confidence": 0.0,
            "criminal_id": None
        }
    
    def batch_recognize(self, image_paths, known_encodings_dict, tolerance=0.6):
        """Recognize faces in multiple images"""
        results = []
        for image_path in image_paths:
            result = self.recognize_face(image_path, known_encodings_dict, tolerance)
            results.append({
                "image": str(image_path),
                "match": result
            })
        return results
    
    def get_face_quality_score(self, frame):
        """
        Assess quality of detected face
        Returns: Score 0-100
        """
        faces = self.detect_faces_opencv(frame)
        
        if len(faces) == 0:
            return 0
        
        x, y, w, h = faces[0]
        face_size = w * h
        frame_size = frame.shape[0] * frame.shape[1]
        
        # Face should be 5-30% of frame
        size_ratio = face_size / frame_size
        
        # Check for eyes (indicates face is frontal)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi)
        
        # Calculate quality score
        score = 0
        
        # Size score (0-40 points)
        if 0.05 <= size_ratio <= 0.30:
            score += 40
        elif 0.03 <= size_ratio <= 0.40:
            score += 20
        
        # Eyes detected (0-40 points)
        if len(eyes) >= 2:
            score += 40
        elif len(eyes) == 1:
            score += 20
        
        # Sharpness score (0-20 points)
        laplacian = cv2.Laplacian(face_roi, cv2.CV_64F).var()
        if laplacian > 100:
            score += 20
        elif laplacian > 50:
            score += 10
        
        return min(score, 100)