"""
Real-time Recognition Tab - Live webcam face recognition
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QGroupBox, QSpinBox, QCheckBox,
                              QListWidget, QListWidgetItem, QComboBox, QFileDialog,
                              QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import cv2
import numpy as np
from datetime import datetime


class CameraThread(QThread):
    """Thread for camera capture and face recognition"""
    frame_ready = pyqtSignal(np.ndarray, list)  # frame, detections
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_index, face_engine, recognition_enabled=True):
        super().__init__()
        self.camera_index = camera_index
        self.face_engine = face_engine
        self.recognition_enabled = recognition_enabled
        self._is_running = True
        self.skip_frames = 2  # Process every Nth frame
        self.frame_count = 0
        
    def run(self):
        """Capture and process frames"""
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            self.error_occurred.emit("Failed to open camera")
            return
            
        while self._is_running:
            ret, frame = cap.read()
            
            if not ret:
                self.error_occurred.emit("Failed to read frame")
                break
                
            detections = []
            
            # Process only every Nth frame for performance
            if self.recognition_enabled and self.frame_count % self.skip_frames == 0:
                try:
                    # Detect faces
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = self.face_engine.detect_faces(rgb_frame)
                    
                    # Recognize each face
                    for face_location in face_locations:
                        top, right, bottom, left = face_location
                        
                        # Extract face
                        face_image = rgb_frame[top:bottom, left:right]
                        
                        # Recognize
                        matches = self.face_engine.recognize_face_from_array(face_image)
                        
                        detection = {
                            'location': (left, top, right, bottom),
                            'matches': matches
                        }
                        detections.append(detection)
                        
                except Exception as e:
                    pass  # Continue even if recognition fails
                    
            self.frame_count += 1
            self.frame_ready.emit(frame, detections)
            
            # Small delay to reduce CPU usage
            self.msleep(30)
            
        cap.release()
        
    def stop(self):
        """Stop the thread"""
        self._is_running = False


class RealtimeRecognitionTab(QWidget):
    """Real-time face recognition tab"""
    
    def __init__(self, db, face_engine, user):
        super().__init__()
        self.face_engine = face_engine
        self.db = db
        self.user = user
        self.camera_thread = None
        self.detection_log = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QHBoxLayout()
        
        # Left panel - Camera feed
        left_layout = QVBoxLayout()
        
        camera_group = QGroupBox("Live Camera Feed")
        camera_layout = QVBoxLayout()
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid #555; background: black;")
        self.video_label.setText("Camera stopped")
        
        camera_layout.addWidget(self.video_label)
        camera_group.setLayout(camera_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.combo_camera = QComboBox()
        self.combo_camera.addItems(["Camera 0", "Camera 1", "Camera 2"])
        
        self.btn_start = QPushButton("▶️ Start Camera")
        self.btn_stop = QPushButton("⏹️ Stop Camera")
        self.btn_stop.setEnabled(False)
        self.btn_capture = QPushButton("📷 Capture")
        self.btn_capture.setEnabled(False)
        
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_capture.clicked.connect(self.capture_frame)
        
        controls_layout.addWidget(QLabel("Camera:"))
        controls_layout.addWidget(self.combo_camera)
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_capture)
        controls_layout.addStretch()
        
        # Settings
        settings_group = QGroupBox("Recognition Settings")
        settings_layout = QVBoxLayout()
        
        self.chk_recognition = QCheckBox("Enable Face Recognition")
        self.chk_recognition.setChecked(True)
        
        self.chk_save_matches = QCheckBox("Auto-save Matches to Database")
        self.chk_save_matches.setChecked(False)
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Min Confidence:"))
        self.spin_confidence = QSpinBox()
        self.spin_confidence.setRange(50, 99)
        self.spin_confidence.setValue(70)
        self.spin_confidence.setSuffix("%")
        confidence_layout.addWidget(self.spin_confidence)
        confidence_layout.addStretch()
        
        settings_layout.addWidget(self.chk_recognition)
        settings_layout.addWidget(self.chk_save_matches)
        settings_layout.addLayout(confidence_layout)
        settings_group.setLayout(settings_layout)
        
        left_layout.addWidget(camera_group, 1)
        left_layout.addLayout(controls_layout)
        left_layout.addWidget(settings_group)
        
        # Right panel - Detection log
        right_layout = QVBoxLayout()
        
        log_group = QGroupBox("Detection Log")
        log_layout = QVBoxLayout()
        
        self.detection_list = QListWidget()
        
        btn_log_layout = QHBoxLayout()
        self.btn_clear_log = QPushButton("🗑️ Clear Log")
        self.btn_export_log = QPushButton("📄 Export Log")
        
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_export_log.clicked.connect(self.export_log)
        
        btn_log_layout.addWidget(self.btn_clear_log)
        btn_log_layout.addWidget(self.btn_export_log)
        
        self.lbl_stats = QLabel("Detections: 0 | Matches: 0")
        
        log_layout.addWidget(self.detection_list)
        log_layout.addLayout(btn_log_layout)
        log_layout.addWidget(self.lbl_stats)
        log_group.setLayout(log_layout)
        
        right_layout.addWidget(log_group)
        
        # Add panels to main layout
        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)
        
        self.setLayout(layout)
        
    def start_camera(self):
        """Start camera capture"""
        camera_index = self.combo_camera.currentIndex()
        recognition_enabled = self.chk_recognition.isChecked()
        
        self.camera_thread = CameraThread(
            camera_index,
            self.face_engine,
            recognition_enabled
        )
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error_occurred.connect(self.camera_error)
        self.camera_thread.start()
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_capture.setEnabled(True)
        self.combo_camera.setEnabled(False)
        
    def stop_camera(self):
        """Stop camera capture"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            
        self.video_label.clear()
        self.video_label.setText("Camera stopped")
        
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_capture.setEnabled(False)
        self.combo_camera.setEnabled(True)
        
    def update_frame(self, frame, detections):
        """Update video frame with detection boxes"""
        display_frame = frame.copy()
        
        min_confidence = self.spin_confidence.value() / 100.0
        
        # Draw detection boxes
        for detection in detections:
            left, top, right, bottom = detection['location']
            matches = detection['matches']
            
            if matches and matches[0]['confidence'] >= min_confidence:
                # Match found
                color = (0, 255, 0)  # Green
                name = matches[0]['name']
                confidence = matches[0]['confidence']
                label = f"{name} ({confidence:.1%})"
                
                # Log detection
                self.log_detection(name, confidence)
                
                # Save to database if enabled
                if self.chk_save_matches.isChecked():
                    self.save_match(matches[0])
                    
            else:
                # No match or low confidence
                color = (255, 255, 0)  # Yellow
                label = "Unknown"
                
            # Draw rectangle
            cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Draw label text
            cv2.putText(
                display_frame,
                label,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_DUPLEX,
                0.6,
                (0, 0, 0),
                1
            )
            
        # Convert to QImage and display
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
        
    def log_detection(self, name, confidence):
        """Log a detection"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {name} - {confidence:.1%}"
        
        # Add to list
        item = QListWidgetItem(log_entry)
        self.detection_list.insertItem(0, item)
        
        # Keep only last 100 entries
        if self.detection_list.count() > 100:
            self.detection_list.takeItem(self.detection_list.count() - 1)
            
        # Update stats
        self.update_stats()
        
    def update_stats(self):
        """Update detection statistics"""
        total = self.detection_list.count()
        matches = sum(1 for i in range(total) if "Unknown" not in self.detection_list.item(i).text())
        self.lbl_stats.setText(f"Detections: {total} | Matches: {matches}")
        
    def save_match(self, match):
        """Save match to database"""
        # This would save a capture frame - simplified here
        pass
        
    def capture_frame(self):
        """Capture current frame"""
        # Get current pixmap and save
        pixmap = self.video_label.pixmap()
        if pixmap:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Capture",
                f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                "Images (*.jpg)"
            )
            if filename:
                pixmap.save(filename)
                
    def clear_log(self):
        """Clear detection log"""
        self.detection_list.clear()
        self.update_stats()
        
    def export_log(self):
        """Export log to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Detection Log",
            f"detection_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("Detection Log\n")
                f.write("=" * 50 + "\n\n")
                
                for i in range(self.detection_list.count()):
                    f.write(self.detection_list.item(i).text() + "\n")
                    
    def camera_error(self, error_msg):
        """Handle camera errors"""
        QMessageBox.critical(self, "Camera Error", error_msg)
        self.stop_camera()

    def stop_recognition(self):
        """Stop recognition (called from main window on close)"""
        self.stop_camera()