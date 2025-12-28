# gui/tabs/batch_tab.py - Batch Processing Tab
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QProgressBar, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import logging

logger = logging.getLogger(__name__)


class BatchProcessingWorker(QThread):
    """Worker thread for batch processing"""
    progress = pyqtSignal(int, str)  # progress %, status message
    finished = pyqtSignal(list)
    
    def __init__(self, image_paths, face_engine, db, user):
        super().__init__()
        self.image_paths = image_paths
        self.engine = face_engine
        self.db = db
        self.user = user
        self.results = []
    
    def run(self):
        """Run batch processing"""
        total = len(self.image_paths)
        known_encodings = self.db.get_mugshot_encodings()
        
        for idx, image_path in enumerate(self.image_paths):
            try:
                filename = os.path.basename(image_path)
                self.progress.emit(int((idx / total) * 100), f"Processing: {filename}")
                
                # Recognize face
                result = self.engine.recognize_face(image_path, known_encodings, tolerance=0.6)
                
                self.results.append({
                    'image': filename,
                    'name': result.get('name', 'Unknown'),
                    'confidence': result.get('confidence', 0.0),
                    'matched': result.get('matched', False),
                    'path': image_path
                })
                
            except Exception as e:
                logger.error(f"Batch processing error for {image_path}: {e}")
                self.results.append({
                    'image': os.path.basename(image_path),
                    'name': 'Error',
                    'confidence': 0.0,
                    'matched': False,
                    'path': image_path
                })
        
        self.progress.emit(100, "Batch processing complete")
        self.finished.emit(self.results)


class BatchProcessingTab(QWidget):
    """Batch processing tab for multiple images"""

    batch_completed = pyqtSignal(dict)
    
    def __init__(self, db, face_engine, user=None):
        super().__init__()
        self.db = db
        self.engine = face_engine
        self.user = user or {'username': 'system', 'role': 'admin'}
        self.worker = None
        self.image_paths = []
        self.results = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title_layout = QHBoxLayout()
        title = QLabel("📁 Batch Face Recognition")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        user_label = QLabel(f"Operator: {self.user['username']}")
        user_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(user_label)
        layout.addLayout(title_layout)
        
        # Instructions
        instructions = QLabel(
            "💡 Select multiple suspect images to process them all at once.\n"
            "   Each image will be compared against the criminal database."
        )
        instructions.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.btn_select = QPushButton("📁 Select Images")
        self.btn_select.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-size: 14px;")
        self.btn_select.clicked.connect(self.select_images)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_process = QPushButton("🔍 Process Batch")
        self.btn_process.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        self.btn_process.clicked.connect(self.process_batch)
        self.btn_process.setEnabled(False)
        btn_layout.addWidget(self.btn_process)
        
        self.btn_export = QPushButton("💾 Export Results")
        self.btn_export.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        btn_layout.addWidget(self.btn_export)
        
        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_clear.clicked.connect(self.clear_results)
        btn_layout.addWidget(self.btn_clear)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.label_status = QLabel("Status: Select images to begin")
        self.label_status.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        layout.addWidget(self.label_status)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Results group
        results_group = QGroupBox("Processing Results")
        results_layout = QVBoxLayout()
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Image", "Match", "Confidence", "Status"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def select_images(self):
        """Select multiple images for batch processing"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Suspect Images for Batch Processing",
            "data/suspects",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*.*)"
        )
        
        if files:
            self.image_paths = files
            self.label_status.setText(f"Status: Selected {len(files)} image(s) - Ready to process")
            self.btn_process.setEnabled(True)
            logger.info(f"Batch: {len(files)} images selected by {self.user['username']}")
    
    def process_batch(self):
        """Process selected images"""
        if not self.image_paths:
            QMessageBox.warning(self, "Error", "No images selected")
            return
        
        # Clear previous results
        self.results = []
        self.table.setRowCount(0)
        
        # Disable buttons
        self.btn_process.setEnabled(False)
        self.btn_select.setEnabled(False)
        self.btn_export.setEnabled(False)
        
        # Show progress
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # Start worker
        self.worker = BatchProcessingWorker(
            self.image_paths, 
            self.engine, 
            self.db,
            self.user
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_batch_finished)
        self.worker.start()
        
        logger.info(f"Batch processing started: {len(self.image_paths)} images by {self.user['username']}")
    
    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress.setValue(value)
        self.label_status.setText(f"Status: {message}")
    
    def on_batch_finished(self, results):
        """Handle batch processing completion"""
        self.results = results
        self.display_results(results)
        
        # Re-enable buttons
        self.btn_process.setEnabled(True)
        self.btn_select.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.progress.setVisible(False)
        
        # Count matches
        matches = sum(1 for r in results if r['matched'])
        
        self.label_status.setText(
            f"Status: Complete - {len(results)} processed, {matches} match(es) found"
        )
        
        logger.info(f"Batch processing complete: {matches}/{len(results)} matches")

        summary = {
        'total': len(results),
        'successful': successful,
        'failed': failed,
        'total_matches': matches
         }
        self.batch_completed.emit(summary) 
        
        QMessageBox.information(
            self, 
            "Batch Complete", 
            f"Processed {len(results)} images\n"
            f"Found {matches} match(es)"
        )
    
    def display_results(self, results):
        """Display results in table"""
        self.table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Image name
            img_item = QTableWidgetItem(result['image'])
            self.table.setItem(row, 0, img_item)
            
            # Match name
            name_item = QTableWidgetItem(result['name'])
            if result['matched']:
                name_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 1, name_item)
            
            # Confidence
            conf_item = QTableWidgetItem(f"{result['confidence']:.1f}%")
            if result['confidence'] >= 80:
                conf_item.setBackground(Qt.green)
            elif result['confidence'] >= 70:
                conf_item.setBackground(Qt.yellow)
            self.table.setItem(row, 2, conf_item)
            
            # Status
            status = "✓ Matched" if result['matched'] else "✗ No Match"
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 3, status_item)
        
        self.table.resizeColumnsToContents()
    
    def export_results(self):
        """Export results to CSV file"""
        if not self.results:
            QMessageBox.warning(self, "Error", "No results to export")
            return
        
        from datetime import datetime
        default_filename = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Batch Results",
            default_filename,
            "CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write("Image,Match,Confidence,Status\n")
                    for result in self.results:
                        status = "Matched" if result['matched'] else "No Match"
                        f.write(
                            f"{result['image']},"
                            f"{result['name']},"
                            f"{result['confidence']:.2f}%,"
                            f"{status}\n"
                        )
                
                QMessageBox.information(self, "Success", f"Results exported to:\n{filepath}")
                logger.info(f"Batch results exported by {self.user['username']}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
                logger.error(f"Export error: {e}")
    
    def clear_results(self):
        """Clear all results"""
        self.image_paths = []
        self.results = []
        self.table.setRowCount(0)
        self.btn_process.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.label_status.setText("Status: Select images to begin")
        self.progress.setValue(0)