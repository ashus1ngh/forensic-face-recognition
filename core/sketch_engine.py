"""
Sketch Construction Engine - Manages facial sketch composition
"""

from PIL import Image, ImageDraw, ImageEnhance, ImageQt
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np


class SketchComponent:
    """Represents a single sketch component (eyebrow, nose, etc.)"""
    
    def __init__(self, image_path: str, component_type: str):
        self.image_path = image_path
        self.component_type = component_type
        self.image = Image.open(image_path).convert('RGBA')
        
        # Transform properties
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.rotation = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # Color adjustments
        self.brightness = 1.0  # For skin tone
        self.contrast = 1.0
        
        # Z-order (layering)
        self.z_order = self._get_default_z_order()
        
    def _get_default_z_order(self) -> int:
        """Get default layer order for component type"""
        z_orders = {
            'head': 0,
            'neck': 1,
            'ears': 2,
            'face_shape': 3,
            'hair': 10,
            'eyebrows': 8,
            'eyes': 7,
            'nose': 6,
            'lips': 5,
            'mustache': 9,
            'beard': 4
        }
        return z_orders.get(self.component_type, 5)
        
    def get_transformed_image(self) -> Image.Image:
        """Get the image with all transformations applied"""
        img = self.image.copy()
        
        # Apply flips
        if self.flip_horizontal:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flip_vertical:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
        # Apply rotation
        if self.rotation != 0:
            img = img.rotate(self.rotation, expand=True, resample=Image.BICUBIC)
            
        # Apply scale
        if self.scale != 1.0:
            new_size = (int(img.width * self.scale), int(img.height * self.scale))
            img = img.resize(new_size, Image.LANCZOS)
            
        # Apply brightness/contrast (for skin tone)
        if self.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness)
            
        if self.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast)
            
        return img
        
    def to_dict(self) -> dict:
        """Serialize component to dictionary"""
        return {
            'image_path': self.image_path,
            'component_type': self.component_type,
            'x': self.x,
            'y': self.y,
            'scale': self.scale,
            'rotation': self.rotation,
            'flip_horizontal': self.flip_horizontal,
            'flip_vertical': self.flip_vertical,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'z_order': self.z_order
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'SketchComponent':
        """Deserialize component from dictionary"""
        component = SketchComponent(data['image_path'], data['component_type'])
        component.x = data['x']
        component.y = data['y']
        component.scale = data['scale']
        component.rotation = data['rotation']
        component.flip_horizontal = data['flip_horizontal']
        component.flip_vertical = data['flip_vertical']
        component.brightness = data['brightness']
        component.contrast = data['contrast']
        component.z_order = data['z_order']
        return component


class SketchEngine:
    """Manages sketch composition and rendering"""
    
    def __init__(self, components_path: str = "data/sketch_components"):
        self.components_path = components_path
        self.canvas_size = (800, 1000)  # Width x Height
        self.components: List[SketchComponent] = []
        self.component_library = self._load_component_library()
        
    def _load_component_library(self) -> Dict[str, List[str]]:
        """Load all available components from disk"""
        library = {
            'eyebrows': [],
            'eyes': [],
            'hair': [],
            'nose': [],
            'lips': [],
            'mustache': [],
            'beard': [],
            'head': [],
            'ears': [],
            'neck': []
        }
        
        if not os.path.exists(self.components_path):
            os.makedirs(self.components_path, exist_ok=True)
            # Create subdirectories
            for component_type in library.keys():
                os.makedirs(os.path.join(self.components_path, component_type), exist_ok=True)
            return library
            
        for component_type in library.keys():
            component_dir = os.path.join(self.components_path, component_type)
            if os.path.exists(component_dir):
                files = [f for f in os.listdir(component_dir) 
                        if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                library[component_type] = [
                    os.path.join(component_dir, f) for f in sorted(files)
                ]
                
        return library
        
    def add_component(self, image_path: str, component_type: str, 
                     x: int = 0, y: int = 0) -> SketchComponent:
        """Add a component to the sketch"""
        component = SketchComponent(image_path, component_type)
        component.x = x
        component.y = y
        self.components.append(component)
        return component
        
    def remove_component(self, component: SketchComponent):
        """Remove a component from the sketch"""
        if component in self.components:
            self.components.remove(component)
            
    def clear_components(self):
        """Remove all components"""
        self.components.clear()
        
    def get_component_at(self, x: int, y: int) -> Optional[SketchComponent]:
        """Get the topmost component at given coordinates"""
        # Sort by z_order (highest first)
        sorted_components = sorted(self.components, key=lambda c: c.z_order, reverse=True)
        
        for component in sorted_components:
            img = component.get_transformed_image()
            
            # Check if point is within component bounds
            if (component.x <= x <= component.x + img.width and
                component.y <= y <= component.y + img.height):
                
                # Check if pixel is not transparent
                relative_x = x - component.x
                relative_y = y - component.y
                
                if (0 <= relative_x < img.width and 0 <= relative_y < img.height):
                    pixel = img.getpixel((relative_x, relative_y))
                    if len(pixel) == 4 and pixel[3] > 128:  # Check alpha
                        return component
                        
        return None
        
    def render_sketch(self, background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Image.Image:
        """Render the complete sketch"""
        # Create canvas
        canvas = Image.new('RGBA', self.canvas_size, background_color)
        
        # Sort components by z_order (lowest first, so they're drawn bottom-up)
        sorted_components = sorted(self.components, key=lambda c: c.z_order)
        
        # Composite each component
        for component in sorted_components:
            img = component.get_transformed_image()
            
            # Paste component at its position
            canvas.paste(img, (component.x, component.y), img)
            
        return canvas
        
    def save_sketch(self, output_path: str, background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)):
        """Save the rendered sketch to file"""
        sketch = self.render_sketch(background_color)
        
        # Convert RGBA to RGB if saving as JPEG
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            rgb_sketch = Image.new('RGB', sketch.size, (255, 255, 255))
            rgb_sketch.paste(sketch, mask=sketch.split()[3])  # Use alpha as mask
            rgb_sketch.save(output_path, quality=95)
        else:
            sketch.save(output_path)
            
    def save_project(self, project_path: str):
        """Save the sketch project (components and their properties)"""
        project_data = {
            'version': '1.0',
            'canvas_size': self.canvas_size,
            'components': [c.to_dict() for c in self.components],
            'created_date': datetime.now().isoformat()
        }
        
        with open(project_path, 'w') as f:
            json.dump(project_data, f, indent=2)
            
    def load_project(self, project_path: str):
        """Load a sketch project"""
        with open(project_path, 'r') as f:
            project_data = json.load(f)
            
        self.canvas_size = tuple(project_data['canvas_size'])
        self.components = [SketchComponent.from_dict(c) for c in project_data['components']]
        
    def export_for_recognition(self, output_path: str) -> str:
        """Export sketch optimized for face recognition"""
        # Render sketch
        sketch = self.render_sketch()
        
        # Convert to RGB
        rgb_sketch = Image.new('RGB', sketch.size, (255, 255, 255))
        rgb_sketch.paste(sketch, mask=sketch.split()[3])
        
        # Crop to face area (remove excess white space)
        rgb_sketch = self._auto_crop_face(rgb_sketch)
        
        # Resize to standard recognition size (if needed)
        # Most face recognition works best with consistent sizes
        rgb_sketch = rgb_sketch.resize((600, 800), Image.LANCZOS)
        
        # Save
        rgb_sketch.save(output_path, quality=95)
        
        return output_path
        
    def _auto_crop_face(self, image: Image.Image) -> Image.Image:
        """Automatically crop to face area"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Find non-white pixels
        mask = np.any(img_array < 250, axis=2)
        
        if not mask.any():
            return image
            
        # Find bounding box
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        if not rows.any() or not cols.any():
            return image
            
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        
        # Add padding
        padding = 50
        ymin = max(0, ymin - padding)
        ymax = min(image.height, ymax + padding)
        xmin = max(0, xmin - padding)
        xmax = min(image.width, xmax + padding)
        
        return image.crop((xmin, ymin, xmax, ymax))
        
    def get_available_components(self, component_type: str) -> List[str]:
        """Get list of available components of a specific type"""
        return self.component_library.get(component_type, [])
        
    def move_component_to_front(self, component: SketchComponent):
        """Move component to front (highest z-order)"""
        max_z = max([c.z_order for c in self.components], default=0)
        component.z_order = max_z + 1
        
    def move_component_to_back(self, component: SketchComponent):
        """Move component to back (lowest z-order)"""
        min_z = min([c.z_order for c in self.components], default=0)
        component.z_order = min_z - 1