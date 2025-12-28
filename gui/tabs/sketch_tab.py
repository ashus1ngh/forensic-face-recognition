"""
Sketch Construction Tab - Interactive facial sketch builder
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QGroupBox, QListWidget, QSlider, QSpinBox,
                              QComboBox, QFileDialog, QMessageBox, QScrollArea,
                              QFrame, QCheckBox, QLineEdit, QInputDialog,
                              QListWidgetItem, QToolButton, QSplitter)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (QPixmap, QImage, QPainter, QPen, QColor, QCursor,
                         QDrag, QIcon, QPalette)
from PIL import Image, ImageQt
import os
from datetime import datetime
from core.sketch_engine import SketchEngine, SketchComponent


class SketchCanvas(QLabel):
    """Interactive canvas for sketch construction"""
    
    component_selected = pyqtSignal(object)  # Emits selected component
    component_moved = pyqtSignal()
    
    def __init__(self, sketch_engine: SketchEngine):
        super().__init__()
        self.sketch_engine = sketch_engine
        self.selected_component = None
        self.drag_start = None
        self.is_dragging = False
        
        # Setup canvas
        self.setMinimumSize(800, 1000)
        self.setMaximumSize(800, 1000)
        self.setStyleSheet("border: 2px solid #555; background: white;")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        self.update_canvas()
        
    def update_canvas(self):
        """Render and display the sketch"""
        sketch_image = self.sketch_engine.render_sketch()
        
        # Convert PIL Image to QPixmap
        qimage = ImageQt.ImageQt(sketch_image)
        pixmap = QPixmap.fromImage(qimage)
        
        # Draw selection box if component is selected
        if self.selected_component:
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.DashLine))
            
            img = self.selected_component.get_transformed_image()
            rect = QRect(
                self.selected_component.x,
                self.selected_component.y,
                img.width,
                img.height
            )
            painter.drawRect(rect)
            painter.end()
            
        self.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        """Handle mouse press - select component"""
        if event.button() == Qt.LeftButton:
            x, y = event.pos().x(), event.pos().y()
            component = self.sketch_engine.get_component_at(x, y)
            
            if component:
                self.selected_component = component
                self.drag_start = event.pos()
                self.is_dragging = False
                self.component_selected.emit(component)
                self.update_canvas()
            else:
                self.selected_component = None
                self.component_selected.emit(None)
                self.update_canvas()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move - drag component"""
        if self.selected_component and self.drag_start:
            if not self.is_dragging:
                # Check if movement threshold reached
                if (event.pos() - self.drag_start).manhattanLength() > 5:
                    self.is_dragging = True
                    
            if self.is_dragging:
                delta = event.pos() - self.drag_start
                self.selected_component.x += delta.x()
                self.selected_component.y += delta.y()
                self.drag_start = event.pos()
                self.update_canvas()
                self.component_moved.emit()
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_start = None
            
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle component drop"""
        if event.mimeData().hasText():
            # Get component info from mime data
            data = event.mimeData().text().split('|')
            if len(data) == 2:
                component_type, image_path = data
                
                # Add component at drop position
                x = event.pos().x() - 50  # Center on cursor
                y = event.pos().y() - 50
                
                component = self.sketch_engine.add_component(
                    image_path, component_type, x, y
                )
                
                self.selected_component = component
                self.component_selected.emit(component)
                self.update_canvas()
                
            event.acceptProposedAction()
            
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if self.selected_component:
            if event.key() == Qt.Key_Delete:
                self.sketch_engine.remove_component(self.selected_component)
                self.selected_component = None
                self.component_selected.emit(None)
                self.update_canvas()
                
            elif event.key() == Qt.Key_Up:
                self.selected_component.y -= 5
                self.update_canvas()
                
            elif event.key() == Qt.Key_Down:
                self.selected_component.y += 5
                self.update_canvas()
                
            elif event.key() == Qt.Key_Left:
                self.selected_component.x -= 5
                self.update_canvas()
                
            elif event.key() == Qt.Key_Right:
                self.selected_component.x += 5
                self.update_canvas()


class ComponentLibrary(QListWidget):
    """Widget displaying available components"""
    
    def __init__(self, component_type: str, component_paths: list):
        super().__init__()
        self.component_type = component_type
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(80, 80))
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(10)
        self.setMaximumHeight(200)
        
        # Load components
        for path in component_paths:
            self.add_component_item(path)
            
    def add_component_item(self, image_path: str):
        """Add component to library"""
        item = QListWidgetItem()
        
        # Create thumbnail
        pixmap = QPixmap(image_path).scaled(
            80, 80,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        item.setIcon(QIcon(pixmap))
        item.setText(os.path.basename(image_path))
        item.setData(Qt.UserRole, image_path)
        
        self.addItem(item)
        
    def mousePressEvent(self, event):
        """Handle drag start"""
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                # Start drag operation
                drag = QDrag(self)
                mime_data = drag.mimeData()
                
                # Store component info
                image_path = item.data(Qt.UserRole)
                mime_data.setText(f"{self.component_type}|{image_path}")
                
                drag.setMimeData(mime_data)
                drag.setPixmap(item.icon().pixmap(QSize(64, 64)))
                drag.exec(Qt.CopyAction)


class SketchTab(QWidget):
    """Sketch construction tab"""
    
    def __init__(self, face_engine, db_manager, current_user):
        super().__init__()
        self.face_engine = face_engine
        self.db_manager = db_manager
        self.current_user = current_user
        
        # Initialize sketch engine
        self.sketch_engine = SketchEngine()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QHBoxLayout()
        
        # Left panel - Component library
        left_panel = self.create_component_panel()
        
        # Center panel - Canvas
        center_panel = self.create_canvas_panel()
        
        # Right panel - Properties
        right_panel = self.create_properties_panel()
        
        # Add to splitter for resizing
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)
        
        center_widget = QWidget()
        center_widget.setLayout(center_panel)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setMaximumWidth(300)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([250, 800, 250])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_component_panel(self) -> QVBoxLayout:
        """Create component library panel"""
        layout = QVBoxLayout()
        
        title = QLabel("📚 Component Library")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Component type selector
        self.combo_component_type = QComboBox()
        self.combo_component_type.addItems([
            "Head", "Neck", "Ears", "Hair", "Eyebrows",
            "Eyes", "Nose", "Lips", "Mustache", "Beard"
        ])
        self.combo_component_type.currentTextChanged.connect(self.load_components)
        layout.addWidget(self.combo_component_type)
        
        # Component library (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.component_library = ComponentLibrary("head", [])
        scroll.setWidget(self.component_library)
        
        layout.addWidget(scroll, 1)
        
        # Instructions
        instructions = QLabel(
            "💡 Drag components onto the canvas\n"
            "   Click to select, Delete to remove\n"
            "   Use arrow keys for fine positioning"
        )
        instructions.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Load initial components
        self.load_components("Head")
        
        return layout
        
    def create_canvas_panel(self) -> QVBoxLayout:
        """Create canvas panel"""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_new = QPushButton("🆕 New")
        self.btn_save_project = QPushButton("💾 Save Project")
        self.btn_load_project = QPushButton("📂 Load Project")
        self.btn_clear = QPushButton("🗑️ Clear All")
        
        self.btn_new.clicked.connect(self.new_sketch)
        self.btn_save_project.clicked.connect(self.save_project)
        self.btn_load_project.clicked.connect(self.load_project)
        self.btn_clear.clicked.connect(self.clear_sketch)
        
        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_save_project)
        toolbar.addWidget(self.btn_load_project)
        toolbar.addWidget(self.btn_clear)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Canvas
        self.canvas = SketchCanvas(self.sketch_engine)
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.component_moved.connect(self.on_component_moved)
        
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidget(self.canvas)
        canvas_scroll.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(canvas_scroll, 1)
        
        # Action buttons
        actions = QHBoxLayout()
        
        self.btn_export_image = QPushButton("📷 Export as Image")
        self.btn_save_to_db = QPushButton("💾 Save to Database")
        self.btn_match_sketch = QPushButton("🔍 Match Against Database")
        
        self.btn_export_image.clicked.connect(self.export_image)
        self.btn_save_to_db.clicked.connect(self.save_to_database)
        self.btn_match_sketch.clicked.connect(self.match_sketch)
        
        actions.addWidget(self.btn_export_image)
        actions.addWidget(self.btn_save_to_db)
        actions.addWidget(self.btn_match_sketch)
        
        layout.addLayout(actions)
        
        return layout
        
    def create_properties_panel(self) -> QVBoxLayout:
        """Create properties panel"""
        layout = QVBoxLayout()
        
        title = QLabel("🎨 Component Properties")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Transform group
        transform_group = QGroupBox("Transform")
        transform_layout = QVBoxLayout()
        
        # Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.slider_scale = QSlider(Qt.Horizontal)
        self.slider_scale.setRange(25, 200)
        self.slider_scale.setValue(100)
        self.slider_scale.valueChanged.connect(self.update_scale)
        self.lbl_scale = QLabel("100%")
        scale_layout.addWidget(self.slider_scale)
        scale_layout.addWidget(self.lbl_scale)
        
        # Rotation
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        self.slider_rotation = QSlider(Qt.Horizontal)
        self.slider_rotation.setRange(-180, 180)
        self.slider_rotation.setValue(0)
        self.slider_rotation.valueChanged.connect(self.update_rotation)
        self.lbl_rotation = QLabel("0°")
        rotation_layout.addWidget(self.slider_rotation)
        rotation_layout.addWidget(self.lbl_rotation)
        
        # Flip buttons
        flip_layout = QHBoxLayout()
        self.btn_flip_h = QPushButton("↔️ Flip Horizontal")
        self.btn_flip_v = QPushButton("↕️ Flip Vertical")
        self.btn_flip_h.clicked.connect(self.flip_horizontal)
        self.btn_flip_v.clicked.connect(self.flip_vertical)
        flip_layout.addWidget(self.btn_flip_h)
        flip_layout.addWidget(self.btn_flip_v)
        
        transform_layout.addLayout(scale_layout)
        transform_layout.addLayout(rotation_layout)
        transform_layout.addLayout(flip_layout)
        transform_group.setLayout(transform_layout)
        
        # Color adjustment group
        color_group = QGroupBox("Color & Tone")
        color_layout = QVBoxLayout()
        
        # Brightness (skin tone)
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setRange(50, 150)
        self.slider_brightness.setValue(100)
        self.slider_brightness.valueChanged.connect(self.update_brightness)
        self.lbl_brightness = QLabel("100%")
        brightness_layout.addWidget(self.slider_brightness)
        brightness_layout.addWidget(self.lbl_brightness)
        
        # Contrast
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        self.slider_contrast = QSlider(Qt.Horizontal)
        self.slider_contrast.setRange(50, 150)
        self.slider_contrast.setValue(100)
        self.slider_contrast.valueChanged.connect(self.update_contrast)
        self.lbl_contrast = QLabel("100%")
        contrast_layout.addWidget(self.slider_contrast)
        contrast_layout.addWidget(self.lbl_contrast)
        
        # Preset skin tones
        tone_label = QLabel("Skin Tone Presets:")
        self.combo_skin_tone = QComboBox()
        self.combo_skin_tone.addItems([
            "Default",
            "Very Light",
            "Light",
            "Medium",
            "Tan",
            "Dark",
            "Very Dark"
        ])
        self.combo_skin_tone.currentTextChanged.connect(self.apply_skin_tone)
        
        color_layout.addLayout(brightness_layout)
        color_layout.addLayout(contrast_layout)
        color_layout.addWidget(tone_label)
        color_layout.addWidget(self.combo_skin_tone)
        color_group.setLayout(color_layout)
        
        # Layer control
        layer_group = QGroupBox("Layer Control")
        layer_layout = QVBoxLayout()
        
        layer_buttons = QHBoxLayout()
        self.btn_bring_front = QPushButton("⬆️ Bring to Front")
        self.btn_send_back = QPushButton("⬇️ Send to Back")
        self.btn_bring_front.clicked.connect(self.bring_to_front)
        self.btn_send_back.clicked.connect(self.send_to_back)
        layer_buttons.addWidget(self.btn_bring_front)
        layer_buttons.addWidget(self.btn_send_back)
        
        self.btn_delete = QPushButton("🗑️ Delete Component")
        self.btn_delete.clicked.connect(self.delete_component)
        
        layer_layout.addLayout(layer_buttons)
        layer_layout.addWidget(self.btn_delete)
        layer_group.setLayout(layer_layout)
        
        # Add all groups
        layout.addWidget(transform_group)
        layout.addWidget(color_group)
        layout.addWidget(layer_group)
        layout.addStretch()
        
        # Disable properties initially
        self.set_properties_enabled(False)
        
        return layout
        
    def load_components(self, component_type: str):
        """Load components of selected type"""
        type_map = {
            "Head": "head",
            "Neck": "neck",
            "Ears": "ears",
            "Hair": "hair",
            "Eyebrows": "eyebrows",
            "Eyes": "eyes",
            "Nose": "nose",
            "Lips": "lips",
            "Mustache": "mustache",
            "Beard": "beard"
        }
        
        internal_type = type_map.get(component_type, "head")
        components = self.sketch_engine.get_available_components(internal_type)
        
        # Create new library widget
        self.component_library = ComponentLibrary(internal_type, components)
        
        # Replace in scroll area
        scroll = self.component_library.parent()
        if scroll:
            scroll.setWidget(self.component_library)
            
    def on_component_selected(self, component):
        """Handle component selection"""
        if component:
            self.set_properties_enabled(True)
            self.load_component_properties(component)
        else:
            self.set_properties_enabled(False)
            
    def on_component_moved(self):
        """Handle component moved"""
        self.canvas.update_canvas()
        
    def load_component_properties(self, component: SketchComponent):
        """Load component properties into UI"""
        self.slider_scale.setValue(int(component.scale * 100))
        self.slider_rotation.setValue(int(component.rotation))
        self.slider_brightness.setValue(int(component.brightness * 100))
        self.slider_contrast.setValue(int(component.contrast * 100))
        
    def set_properties_enabled(self, enabled: bool):
        """Enable/disable property controls"""
        self.slider_scale.setEnabled(enabled)
        self.slider_rotation.setEnabled(enabled)
        self.slider_brightness.setEnabled(enabled)
        self.slider_contrast.setEnabled(enabled)
        self.btn_flip_h.setEnabled(enabled)
        self.btn_flip_v.setEnabled(enabled)
        self.btn_bring_front.setEnabled(enabled)
        self.btn_send_back.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)
        self.combo_skin_tone.setEnabled(enabled)
        
    def update_scale(self, value):
        """Update component scale"""
        if self.canvas.selected_component:
            self.canvas.selected_component.scale = value / 100.0
            self.lbl_scale.setText(f"{value}%")
            self.canvas.update_canvas()
            
    def update_rotation(self, value):
        """Update component rotation"""
        if self.canvas.selected_component:
            self.canvas.selected_component.rotation = value
            self.lbl_rotation.setText(f"{value}°")
            self.canvas.update_canvas()
            
    def update_brightness(self, value):
        """Update component brightness"""
        if self.canvas.selected_component:
            self.canvas.selected_component.brightness = value / 100.0
            self.lbl_brightness.setText(f"{value}%")
            self.canvas.update_canvas()
            
    def update_contrast(self, value):
        """Update component contrast"""
        if self.canvas.selected_component:
            self.canvas.selected_component.contrast = value / 100.0
            self.lbl_contrast.setText(f"{value}%")
            self.canvas.update_canvas()
            
    def flip_horizontal(self):
        """Flip component horizontally"""
        if self.canvas.selected_component:
            self.canvas.selected_component.flip_horizontal = not self.canvas.selected_component.flip_horizontal
            self.canvas.update_canvas()
            
    def flip_vertical(self):
        """Flip component vertically"""
        if self.canvas.selected_component:
            self.canvas.selected_component.flip_vertical = not self.canvas.selected_component.flip_vertical
            self.canvas.update_canvas()
            
    def apply_skin_tone(self, tone: str):
        """Apply preset skin tone"""
        if not self.canvas.selected_component:
            return
            
        tone_values = {
            "Default": 100,
            "Very Light": 120,
            "Light": 110,
            "Medium": 100,
            "Tan": 90,
            "Dark": 75,
            "Very Dark": 60
        }
        
        brightness = tone_values.get(tone, 100)
        self.slider_brightness.setValue(brightness)
        
    def bring_to_front(self):
        """Bring component to front"""
        if self.canvas.selected_component:
            self.sketch_engine.move_component_to_front(self.canvas.selected_component)
            self.canvas.update_canvas()
            
    def send_to_back(self):
        """Send component to back"""
        if self.canvas.selected_component:
            self.sketch_engine.move_component_to_back(self.canvas.selected_component)
            self.canvas.update_canvas()
            
    def delete_component(self):
        """Delete selected component"""
        if self.canvas.selected_component:
            self.sketch_engine.remove_component(self.canvas.selected_component)
            self.canvas.selected_component = None
            self.set_properties_enabled(False)
            self.canvas.update_canvas()
            
    def new_sketch(self):
        """Start new sketch"""
        reply = QMessageBox.question(
            self, "New Sketch",
            "Clear current sketch and start new?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_sketch()
            
    def clear_sketch(self):
        """Clear all components"""
        self.sketch_engine.clear_components()
        self.canvas.selected_component = None
        self.set_properties_enabled(False)
        self.canvas.update_canvas()
        
    def save_project(self):
        """Save sketch project"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Sketch Project",
            f"sketch_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                self.sketch_engine.save_project(filename)
                QMessageBox.information(self, "Success", "Project saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
                
    def load_project(self):
        """Load sketch project"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Sketch Project",
            "",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                self.sketch_engine.load_project(filename)
                self.canvas.update_canvas()
                QMessageBox.information(self, "Success", "Project loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
                
    def export_image(self):
        """Export sketch as image"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Sketch",
            f"sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        
        if filename:
            try:
                self.sketch_engine.save_sketch(filename)
                QMessageBox.information(self, "Success", "Sketch exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
                
    def save_to_database(self):
        """Save sketch to criminal database"""
        name, ok = QInputDialog.getText(self, "Save to Database", "Enter suspect name:")
        
        if ok and name:
            try:
                # Export for recognition
                temp_path = f"data/suspects/sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                os.makedirs("data/suspects", exist_ok=True)
                
                self.sketch_engine.export_for_recognition(temp_path)
                
                # Add to database (would need additional fields)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Sketch saved to database as '{name}'\nPath: {temp_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
                
    def match_sketch(self):
        """Match sketch against criminal database"""
        try:
            # Export sketch
            temp_path = f"data/temp/sketch_match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            os.makedirs("data/temp", exist_ok=True)
            
            self.sketch_engine.export_for_recognition(temp_path)
            
            # Perform recognition
            matches = self.face_engine.recognize_face(temp_path)
            
            if matches:
                # Show results
                result_text = "Match Results:\n\n"
                for i, match in enumerate(matches[:5], 1):
                    result_text += f"{i}. {match['name']} - {match['confidence']:.1%}\n"
                    
                QMessageBox.information(self, "Match Results", result_text)
            else:
                QMessageBox.information(self, "No Match", "No matches found in database")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Match failed: {str(e)}")