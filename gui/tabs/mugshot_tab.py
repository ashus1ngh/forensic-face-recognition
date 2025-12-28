# gui/tabs/mugshot_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QMessageBox, QGroupBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import cv2
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MugshotCaptureTab(QWidget):
    def __init__(self, db, face_engine, user=None):
        super().__init__()
        self.db = db
        self.face_engine = face_engine
        self.user = user or {'username': 'system', 'role': 'admin'}
        self.cap = None
        self.timer = None
        self.current_frame = None
        self.is_camera_running = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title with user info
        title_layout = QHBoxLayout()
        title = QLabel("📸 Capture Criminal Mugshots")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        user_label = QLabel(f"Operator: {self.user['username']}")
        user_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(user_label)
        layout.addLayout(title_layout)
        
        # Status label (create early so refresh_criminal_combo can use it)
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Criminal selection group
        selection_group = QGroupBox("Select Criminal")
        selection_layout = QVBoxLayout()
        
        self.criminal_combo = QComboBox()
        self.criminal_combo.setStyleSheet("padding: 8px; font-size: 14px;")
        self.refresh_criminal_combo()
        selection_layout.addWidget(self.criminal_combo)
        
        refresh_combo_btn = QPushButton("🔄 Refresh List")
        refresh_combo_btn.clicked.connect(self.refresh_criminal_combo)
        refresh_combo_btn.setStyleSheet("padding: 6px;")
        selection_layout.addWidget(refresh_combo_btn)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Camera preview group
        preview_group = QGroupBox("Camera Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Camera not started")
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setMaximumSize(640, 480)
        self.preview_label.setStyleSheet("border: 2px solid #ccc; background: #000; color: #fff;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Camera")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        self.start_btn.clicked.connect(self.start_camera)
        btn_layout.addWidget(self.start_btn)
        
        self.capture_btn = QPushButton("📸 Capture Mugshot")
        self.capture_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        self.capture_btn.clicked.connect(self.capture_mugshot)
        self.capture_btn.setEnabled(False)
        btn_layout.addWidget(self.capture_btn)
        
        self.stop_btn = QPushButton("⏹ Stop Camera")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-size: 14px;")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_criminal_combo(self):
        self.criminal_combo.clear()
        self.criminal_combo.addItem("-- Select Criminal --", None)
        
        try:
            criminals = self.db.get_all_criminals()
            for criminal in criminals:
                # criminal[0] = id, criminal[1] = criminal_id, criminal[2] = name
                display_text = f"{criminal[1]} - {criminal[2]}"
                self.criminal_combo.addItem(display_text, criminal[0])
            
            # Update status if label exists
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Status: Loaded {len(criminals)} criminals")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load criminals: {str(e)}")
            logger.error(f"Failed to refresh criminal combo: {e}")
    
    def start_camera(self):
        if self.is_camera_running:
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Error", "Cannot access camera. Check if it's connected.")
                return
            
            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # 30ms = ~33 FPS
            
            self.is_camera_running = True
            self.start_btn.setEnabled(False)
            self.capture_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Camera running")
            
            logger.info(f"Camera started by {self.user['username']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start camera: {str(e)}")
            logger.error(f"Camera start error: {e}")
    
    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            self.stop_camera()
            return
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            
            # Detect faces and draw rectangles
            faces = self.face_engine.detect_faces_opencv(frame)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Convert to Qt format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.preview_label.setPixmap(pixmap)
            
            # Update status with face count
            if len(faces) > 0:
                self.status_label.setText(f"Status: {len(faces)} face(s) detected")
            else:
                self.status_label.setText("Status: No face detected")
    
    def capture_mugshot(self):
        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "Camera not running. Start camera first.")
            return
        
        criminal_id = self.criminal_combo.currentData()
        if not criminal_id:
            QMessageBox.warning(self, "Error", "Please select a criminal first.")
            return
        
        try:
            # Detect face
            faces = self.face_engine.detect_faces_opencv(self.current_frame)
            
            if len(faces) == 0:
                QMessageBox.warning(self, "No Face Detected", 
                                  "No face detected in frame. Position face properly and try again.")
                return
            
            if len(faces) > 1:
                reply = QMessageBox.question(self, "Multiple Faces", 
                                           f"{len(faces)} faces detected. Continue with capture?",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            
            # Create mugshots directory
            os.makedirs('data/mugshots', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            criminal_name = self.criminal_combo.currentText().split(' - ')[0]
            filename = f"mugshot_{criminal_name}_{timestamp}.jpg"
            image_path = os.path.join('data', 'mugshots', filename)
            
            # Save image
            cv2.imwrite(image_path, self.current_frame)
            
            # Extract face encoding (OpenCV-based)
            encoding = self.face_engine.get_face_encoding_from_cv2(self.current_frame)
            
            # Add to database
            self.db.add_mugshot(
                criminal_id=criminal_id,
                image_path=image_path,
                encoding=encoding,
                captured_by=self.user['username'],
                capture_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            QMessageBox.information(self, "Success", 
                                  f"Mugshot captured and saved!\n\n"
                                  f"File: {filename}\n"
                                  f"Faces detected: {len(faces)}")
            
            logger.info(f"Mugshot captured for criminal_id={criminal_id} by {self.user['username']}")
            self.status_label.setText("Status: Mugshot captured successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to capture mugshot: {str(e)}")
            logger.error(f"Mugshot capture error: {e}")
    
    def stop_camera(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.current_frame = None
        self.is_camera_running = False
        self.preview_label.clear()
        self.preview_label.setText("Camera stopped")
        
        self.start_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Camera stopped")
        
        logger.info(f"Camera stopped by {self.user['username']}")
    
    def closeEvent(self, event):
        """Clean up when tab is closed"""
        self.stop_camera()
        event.accept()