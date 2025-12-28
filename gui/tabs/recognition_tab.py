# gui/tabs/recognition_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QMessageBox, QProgressBar, QFileDialog, QGroupBox, QTableWidget,
                             QTableWidgetItem)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RecognitionWorker(QThread):
    """Background worker for face recognition"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    
    def __init__(self, image_path, db, face_engine, user):
        super().__init__()
        self.image_path = image_path
        self.db = db
        self.face_engine = face_engine
        self.user = user
    
    def run(self):
        try:
            self.progress.emit("Extracting face encoding...")
            
            # Get face encoding from suspect image
            suspect_encoding = self.face_engine.encode_face(self.image_path)
            
            if suspect_encoding is None:
                self.progress.emit("No face detected in image")
                self.finished.emit([])
                return
            
            self.progress.emit("Loading criminal database...")
            
            # Get all criminal mugshot encodings
            known_encodings = self.db.get_mugshot_encodings()
            
            if not known_encodings:
                self.progress.emit("No criminals in database")
                self.finished.emit([])
                return
            
            self.progress.emit(f"Comparing against {len(known_encodings)} mugshots...")
            
            # Find matches
            matches = []
            for known in known_encodings:
                similarity = self.face_engine.calculate_similarity(
                    suspect_encoding, 
                    known['encoding']
                )
                
                if similarity >= 60:  # 60% threshold
                    criminal = self.db.get_criminal_by_id(known['criminal_id'])

                    if criminal:
                        matches.append({
                            'criminal_id': known['criminal_id'],
                            'name': known['name'],
                            'criminal_code': known['criminal_code'],
                            'similarity': similarity,
                            'charges': criminal[6] if criminal else 'Unknown',
                            'case_number': criminal[9] if criminal else 'N/A'
                        })
            
            # Sort by similarity
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            self.progress.emit(f"Found {len(matches)} matches")
            self.finished.emit(matches)
            
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit([])

class SuspectRecognitionTab(QWidget):
    """Tab for recognizing suspects against criminal database"""
    matches_found = pyqtSignal(list)
    
    def __init__(self, db, face_engine, parent, user=None):
        super().__init__()
        self.db = db
        self.face_engine = face_engine
        self.parent = parent
        self.user = user or {'username': 'system', 'role': 'admin'}
        self.suspect_image_path = None
        self.current_matches = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title_layout = QHBoxLayout()
        title = QLabel("🔍 Suspect Face Recognition")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        user_label = QLabel(f"Operator: {self.user['username']}")
        user_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(user_label)
        layout.addLayout(title_layout)
        
        # Image input group
        input_group = QGroupBox("Upload Suspect Image")
        input_layout = QHBoxLayout()
        
        upload_btn = QPushButton("📁 Upload Image")
        upload_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        upload_btn.clicked.connect(self.upload_image)
        input_layout.addWidget(upload_btn)
        
        camera_btn = QPushButton("📷 Capture from Camera")
        camera_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        camera_btn.clicked.connect(self.capture_from_camera)
        input_layout.addWidget(camera_btn)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Preview section
        preview_group = QGroupBox("Suspect Image Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("No image loaded")
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setMaximumSize(400, 300)
        self.preview_label.setStyleSheet("border: 2px solid #ccc; background: #f5f5f5;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Search button
        self.search_btn = QPushButton("🔍 Search for Matches")
        self.search_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 12px; font-size: 16px; font-weight: bold;")
        self.search_btn.clicked.connect(self.search_matches)
        self.search_btn.setEnabled(False)
        layout.addWidget(self.search_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Status: Ready - Upload or capture an image")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Results table
        results_group = QGroupBox("Match Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['Name', 'Criminal ID', 'Similarity %', 'Charges', 'Case #'])
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.results_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Suspect Image", 
            "data/suspects", 
            "Images (*.jpg *.png *.bmp *.jpeg)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load and display image"""
        try:
            self.suspect_image_path = file_path
            pixmap = QPixmap(file_path)
            
            if pixmap.isNull():
                raise Exception("Invalid image file")
            
            # Scale to fit preview
            scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            
            filename = os.path.basename(file_path)
            self.status_label.setText(f"Status: Loaded '{filename}' - Ready to search")
            self.search_btn.setEnabled(True)
            
            logger.info(f"Suspect image loaded: {filename} by {self.user['username']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def capture_from_camera(self):
        """Capture image from webcam"""
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                QMessageBox.critical(self, "Error", "Cannot access camera")
                return
            
            self.status_label.setText("Status: Camera active - Press SPACE to capture, ESC to cancel")
            captured = False
            
            while not captured:
                ret, frame = cap.read()
                if ret:
                    # Draw instructions
                    display_frame = frame.copy()
                    cv2.putText(display_frame, "Press SPACE to capture", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Press ESC to cancel", (10, 70),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    cv2.imshow("Capture Suspect", display_frame)
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == 32:  # SPACE
                        os.makedirs('data/suspects', exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = f"data/suspects/suspect_{timestamp}.jpg"
                        cv2.imwrite(file_path, frame)
                        
                        cv2.destroyAllWindows()
                        cap.release()
                        
                        self.load_image(file_path)
                        captured = True
                    
                    elif key == 27:  # ESC
                        cv2.destroyAllWindows()
                        cap.release()
                        self.status_label.setText("Status: Capture cancelled")
                        break
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Camera error: {str(e)}")
            logger.error(f"Camera capture error: {e}")
    
    def search_matches(self):
        """Search for matching criminals"""
        if not self.suspect_image_path:
            QMessageBox.warning(self, "Error", "Upload or capture an image first")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Status: Searching for matches...")
        self.search_btn.setEnabled(False)
        self.results_table.setRowCount(0)
        
        # Start background worker
        self.worker = RecognitionWorker(
            self.suspect_image_path, 
            self.db, 
            self.face_engine,
            self.user
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.start()
        
        logger.info(f"Face recognition started by {self.user['username']}")
    
    def update_progress(self, message):
        """Update progress message"""
        self.status_label.setText(f"Status: {message}")
    
    def on_search_finished(self, matches):
        """Handle search results"""
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)
        self.current_matches = matches
        
        if matches:
            self.status_label.setText(f"Status: ✓ Found {len(matches)} match(es)")
            self.display_matches(matches)
            
            # Save to database
            self.save_suspect_and_matches(matches)
            
            # Emit signal
            self.matches_found.emit(matches)
            
            QMessageBox.information(
                self, 
                "Matches Found", 
                f"Found {len(matches)} potential match(es)!\n\n"
                f"Top match: {matches[0]['name']} ({matches[0]['similarity']:.1f}%)"
            )
        else:
            self.status_label.setText("Status: No matches found")
            self.results_table.setRowCount(0)
            QMessageBox.information(self, "No Matches", "No matching criminals found in database.")
        
        logger.info(f"Recognition completed: {len(matches)} matches found")
    
    def display_matches(self, matches):
        """Display matches in table"""
        self.results_table.setRowCount(len(matches))
        
        for row, match in enumerate(matches):
            self.results_table.setItem(row, 0, QTableWidgetItem(match['name']))
            self.results_table.setItem(row, 1, QTableWidgetItem(match['criminal_code']))
            
            # Color-code similarity
            similarity_item = QTableWidgetItem(f"{match['similarity']:.1f}%")
            if match['similarity'] >= 80:
                similarity_item.setBackground(Qt.green)
            elif match['similarity'] >= 70:
                similarity_item.setBackground(Qt.yellow)
            self.results_table.setItem(row, 2, similarity_item)
            
            charges = match['charges'][:40] + '...' if len(match['charges']) > 40 else match['charges']
            self.results_table.setItem(row, 3, QTableWidgetItem(charges))
            self.results_table.setItem(row, 4, QTableWidgetItem(match['case_number']))
        
        self.results_table.resizeColumnsToContents()
    
    def save_suspect_and_matches(self, matches):
        """Save suspect and matches to database"""
        try:
            # Get face encoding
            encoding = self.face_engine.encode_face(self.suspect_image_path)
            
            # Add suspect to database
            suspect_id = self.db.add_suspect(
                image_path=self.suspect_image_path,
                face_encoding=encoding,
                name="Unknown Suspect",
                description=f"Matched {len(matches)} criminal(s)",
                uploaded_by=self.user['username']
            )
            
            # Save each match
            for match in matches:
                self.db.save_match(
                    suspect_id=suspect_id,
                    criminal_id=match['criminal_id'],
                    similarity_score=match['similarity'],
                    confidence=match['similarity'],
                    notes=f"Auto-matched by system",
                    matched_by=self.user['username']
                )
            
            logger.info(f"Suspect and {len(matches)} matches saved to database")
            
        except Exception as e:
            logger.error(f"Failed to save suspect/matches: {e}")
            QMessageBox.warning(self, "Warning", f"Matches found but failed to save to database: {str(e)}")