#!/usr/bin/env python3
"""
OMAC - One 'Mazing Action Catalog

A PyQt6-based desktop application for managing action figure collections
with SQLite database backend and photo management.
"""

import sys
import os
import csv
import tarfile
import zipfile
import tempfile
import shutil
import platform
import socket
import signal
from datetime import datetime
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QScrollArea,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QDateEdit, QSplitter, QGroupBox, QListWidget,
    QListWidgetItem, QFrame, QStatusBar, QMenuBar, QMenu,
    QProgressDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QSize, pyqtSignal, QSettings, QTimer, QSocketNotifier
from PyQt6.QtGui import (
    QAction, QFont, QPixmap, QIcon, QPainter, QPen, QBrush,
    QColor, QPalette
)
from database import DatabaseManager
from merge_collections import MergeCollectionsDialog
from photo_manager import PhotoManager
from collection_view import CollectionView
from theme_manager import ThemeManager


class ImageViewerDialog(QDialog):
    """Dialog to display a full-size image."""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photo Viewer")
        self.resize(600, 600)
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                550, 550, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Image not found or invalid.")
        layout.addWidget(self.image_label)
        self.setLayout(layout)

class PhotoWidget(QLabel):
    """Custom widget for displaying photos with click handling."""
    
    clicked = pyqtSignal(str)  # Signal emits file path when clicked
    
    def __init__(self, file_path: str, size: QSize = QSize(150, 150)):
        super().__init__()
        self.file_path = file_path
        self.size = size
        self.setFixedSize(size)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
            QLabel:hover {
                border-color: #0078d4;
                background-color: #e6f3ff;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_photo()
        
    def load_photo(self):
        """Load and display the photo."""
        if os.path.exists(self.file_path):
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size - QSize(10, 10), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
            else:
                self.setText("Invalid\nImage")
        else:
            self.setText("Image\nNot Found")
    
    def mousePressEvent(self, event):
        """Handle mouse click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.file_path)
        super().mousePressEvent(event)


class TagInputWidget(QWidget):
    """Custom widget for tag input with bubble display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []
        self.init_ui()

    def init_ui(self):
        """Initialize the tag input UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Tag display area
        self.tags_layout = QHBoxLayout()
        self.tags_layout.setSpacing(5)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for tags
        self.tags_scroll = QScrollArea()
        self.tags_scroll.setWidgetResizable(True)
        self.tags_scroll.setMaximumHeight(60)
        self.tags_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tags_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tags_container = QWidget()
        self.tags_container.setLayout(self.tags_layout)
        self.tags_scroll.setWidget(self.tags_container)

        # Input field for new tags
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add a tag... (press Enter or comma to add)")
        self.tag_input.returnPressed.connect(self.add_tag_from_input)
        self.tag_input.textChanged.connect(self.handle_text_changed)

        layout.addWidget(self.tags_scroll)
        layout.addWidget(self.tag_input)

    def add_tag_from_input(self):
        """Add a tag from the input field."""
        text = self.tag_input.text().strip()
        if text and text not in self.tags:
            self.add_tag(text)
            self.tag_input.clear()

    def handle_text_changed(self, text):
        """Handle text changes in the input field."""
        if ',' in text:
            # Split by comma and add each tag
            parts = text.split(',')
            for part in parts[:-1]:  # All parts except the last one
                tag = part.strip()
                if tag and tag not in self.tags:
                    self.add_tag(tag)
            # Keep the remaining text in the input
            self.tag_input.setText(parts[-1].strip())

    def add_tag(self, tag_text):
        """Add a tag to the display."""
        if tag_text in self.tags:
            return

        self.tags.append(tag_text)

        # Create tag bubble
        tag_widget = self.create_tag_bubble(tag_text)
        self.tags_layout.addWidget(tag_widget)

    def create_tag_bubble(self, tag_text):
        """Create a tag bubble widget."""
        # Create a frame for the tag
        tag_frame = QFrame()
        tag_frame.setFrameStyle(QFrame.Shape.Box)
        tag_frame.setLineWidth(1)

        # Get theme colors
        app = QApplication.instance()
        if app:
            palette = app.palette()
            bg_color = palette.color(QPalette.ColorRole.Highlight)
            text_color = palette.color(QPalette.ColorRole.HighlightedText)
        else:
            bg_color = QColor(51, 153, 255)
            text_color = QColor(255, 255, 255)

        # Style the tag
        tag_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color.name()};
                border: 1px solid {bg_color.darker(120).name()};
                border-radius: 10px;
                padding: 2px 6px;
                margin: 2px;
            }}
        """)

        # Layout for tag content
        tag_layout = QHBoxLayout(tag_frame)
        tag_layout.setContentsMargins(4, 2, 4, 2)
        tag_layout.setSpacing(4)

        # Tag text
        tag_label = QLabel(tag_text)
        tag_label.setStyleSheet(f"color: {text_color.name()}; border: none; font-size: 11px;")
        tag_layout.addWidget(tag_label)

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                color: {text_color.name()};
                background: transparent;
                border: none;
                font-size: 14px;
                font-weight: bold;
                padding: 0px 2px;
                margin: 0px;
            }}
            QPushButton:hover {{
                color: {bg_color.lighter(150).name()};
            }}
        """)
        remove_btn.setFixedSize(16, 16)
        remove_btn.clicked.connect(lambda: self.remove_tag(tag_text))
        tag_layout.addWidget(remove_btn)

        return tag_frame

    def remove_tag(self, tag_text):
        """Remove a tag."""
        if tag_text in self.tags:
            self.tags.remove(tag_text)

            # Remove the widget from layout
            for i in range(self.tags_layout.count()):
                item = self.tags_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # Check if this is the tag we want to remove
                    if hasattr(widget, 'layout') and widget.layout():
                        layout = widget.layout()
                        for j in range(layout.count()):
                            sub_item = layout.itemAt(j)
                            if sub_item and sub_item.widget() and isinstance(sub_item.widget(), QLabel):
                                if sub_item.widget().text() == tag_text:
                                    widget.setParent(None)
                                    widget.deleteLater()
                                    return

    def get_tags(self):
        """Get the current tags as a list."""
        return self.tags.copy()

    def set_tags(self, tags):
        """Set the tags from a list."""
        # Clear existing tags
        self.clear_tags()

        # Add new tags
        for tag in tags:
            if tag.strip():
                self.add_tag(tag.strip())

    def clear_tags(self):
        """Clear all tags."""
        self.tags.clear()

        # Remove all tag widgets
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

    def get_tags_as_string(self):
        """Get tags as comma-separated string for storage."""
        return ", ".join(self.tags)


class ActionFigureDialog(QDialog):
    """Dialog for adding/editing action figure entries."""
    
    def __init__(self, parent=None, figure_data: Optional[Dict] = None):
        super().__init__(parent)
        self.figure_data = figure_data
        self.is_edit_mode = figure_data is not None
        self.photos = []
        self.load_manufacturers()  # Load saved manufacturers
        self.load_locations()      # Load saved locations
        self.init_ui()
        
        if self.figure_data:
            self.populate_form()
    
    def load_manufacturers(self):
        """Load manufacturers from saved file."""
        self.saved_manufacturers = set()
        try:
            manufacturers_file = os.path.join(self.parent().data_dir, "manufacturers.txt")
            with open(manufacturers_file, "r", encoding="utf-8") as f:
                for line in f:
                    manufacturer = line.strip()
                    if manufacturer:
                        self.saved_manufacturers.add(manufacturer)
        except (FileNotFoundError, AttributeError):
            pass  # File doesn't exist yet, or no parent data_dir
    
    def load_locations(self):
        """Load locations from saved file."""
        self.saved_locations = set()
        try:
            locations_file = os.path.join(self.parent().data_dir, "locations.txt")
            with open(locations_file, "r", encoding="utf-8") as f:
                for line in f:
                    location = line.strip()
                    if location:
                        self.saved_locations.add(location)
        except (FileNotFoundError, AttributeError):
            pass  # File doesn't exist yet, or no parent data_dir
    
    def init_ui(self):
        """Initialize the dialog UI."""
        title = "Edit Action Figure" if self.is_edit_mode else "Add New Action Figure"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Details tab
        details_tab = QWidget()
        details_layout = QGridLayout()
        details_layout.setColumnStretch(1, 1)  # Make the input column stretch
        
        # Set consistent widget sizes
        input_width = 300
        combo_width = 300

        # Form fields with consistent sizing
        self.name_edit = QLineEdit()
        self.name_edit.setFixedWidth(input_width)

        self.series_edit = QLineEdit()
        self.series_edit.setFixedWidth(input_width)

        self.wave_edit = QLineEdit()
        self.wave_edit.setFixedWidth(input_width)

        self.manufacturer_combo = QComboBox()
        # Start with common manufacturers and add any saved ones
        default_manufacturers = [
            "Hasbro", "Mattel", "Bandai", "Takara Tomy", "Hot Toys", 
            "Sideshow Collectibles", "NECA", "McFarlane Toys", "Mezco Toyz",
            "Good Smile Company", "Kotobukiya", "Diamond Select Toys",
            "Funko", "Threezero", "Prime 1 Studio", "XM Studios"
        ]
        all_manufacturers = set(default_manufacturers)
        all_manufacturers.update(getattr(self, 'saved_manufacturers', set()))
        sorted_manufacturers = sorted(list(all_manufacturers))
        self.manufacturer_combo.addItems(sorted_manufacturers)
        self.manufacturer_combo.setEditable(True)
        self.manufacturer_combo.setFixedWidth(250)
        self.add_manufacturer_btn = QPushButton("Add Manufacturer")
        self.add_manufacturer_btn.setFixedWidth(145)
        self.add_manufacturer_btn.clicked.connect(self.add_manufacturer)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2030)
        self.year_spin.setValue(2024)
        self.year_spin.setFixedWidth(combo_width)

        self.scale_combo = QComboBox()
        self.scale_combo.addItems([
            "1/6 Scale", "1/12 Scale", "6 inch", "7 inch", "3.75 inch",
            "Figma", "Nendoroid", "Hot Toys", "Mezco", "MAFEX", "Other"
        ])
        self.scale_combo.setEditable(True)
        self.scale_combo.setFixedWidth(combo_width)

        self.condition_combo = QComboBox()
        self.condition_combo.addItems([
            "Mint in Package", "Damaged Package", "Opened Package", "Loose"
        ])
        self.condition_combo.setFixedWidth(combo_width)

        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0, 9999.99)
        self.purchase_price_spin.setPrefix("$")
        self.purchase_price_spin.setFixedWidth(combo_width)

        self.location_combo = QComboBox()
        # Start with common locations and add any saved ones
        default_locations = [
            "Jeremy House", "Mike House", "Storage Tub", "Attic", "Living Room", "Basement", ""
        ]
        all_locations = set(default_locations)
        all_locations.update(getattr(self, 'saved_locations', set()))
        sorted_locations = sorted(list(all_locations))
        self.location_combo.addItems(sorted_locations)
        self.location_combo.setEditable(True)
        self.location_combo.setFixedWidth(250)
        self.add_location_btn = QPushButton("Add Location")
        self.add_location_btn.setFixedWidth(145)
        self.add_location_btn.clicked.connect(self.add_location)

        self.notes_edit = TagInputWidget()
        self.notes_edit.setFixedWidth(input_width)

        # Create labels with consistent styling and left alignment
        row = 0
        label_style = "QLabel { text-align: left; font-weight: normal; padding-right: 10px; }"

        # Name field
        name_label = QLabel("Name *:")
        name_label.setStyleSheet(label_style)
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(name_label, row, 0)
        details_layout.addWidget(self.name_edit, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Series field
        series_label = QLabel("Series/Line:")
        series_label.setStyleSheet(label_style)
        series_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(series_label, row, 0)
        details_layout.addWidget(self.series_edit, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Wave field
        wave_label = QLabel("Wave:")
        wave_label.setStyleSheet(label_style)
        wave_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(wave_label, row, 0)
        details_layout.addWidget(self.wave_edit, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Manufacturer field with add button
        manufacturer_label = QLabel("Manufacturer:")
        manufacturer_label.setStyleSheet(label_style)
        manufacturer_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(manufacturer_label, row, 0)
        manufacturer_layout = QHBoxLayout()
        manufacturer_layout.setSpacing(5)
        manufacturer_layout.addWidget(self.manufacturer_combo)
        manufacturer_layout.addWidget(self.add_manufacturer_btn)
        manufacturer_layout.addStretch()
        manufacturer_widget = QWidget()
        manufacturer_widget.setLayout(manufacturer_layout)
        details_layout.addWidget(manufacturer_widget, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Year field
        year_label = QLabel("Year:")
        year_label.setStyleSheet(label_style)
        year_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(year_label, row, 0)
        details_layout.addWidget(self.year_spin, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Scale field
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet(label_style)
        scale_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(scale_label, row, 0)
        details_layout.addWidget(self.scale_combo, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Condition field
        condition_label = QLabel("Condition:")
        condition_label.setStyleSheet(label_style)
        condition_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(condition_label, row, 0)
        details_layout.addWidget(self.condition_combo, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Purchase Price field
        purchase_price_label = QLabel("Purchase Price:")
        purchase_price_label.setStyleSheet(label_style)
        purchase_price_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(purchase_price_label, row, 0)
        details_layout.addWidget(self.purchase_price_spin, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Location field with add button
        location_label = QLabel("Location:")
        location_label.setStyleSheet(label_style)
        location_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(location_label, row, 0)
        location_layout = QHBoxLayout()
        location_layout.setSpacing(5)
        location_layout.addWidget(self.location_combo)
        location_layout.addWidget(self.add_location_btn)
        location_layout.addStretch()
        location_widget = QWidget()
        location_widget.setLayout(location_layout)
        details_layout.addWidget(location_widget, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Notes field
        notes_label = QLabel("Tags:")
        notes_label.setStyleSheet(label_style)
        notes_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        details_layout.addWidget(notes_label, row, 0, Qt.AlignmentFlag.AlignTop)
        details_layout.addWidget(self.notes_edit, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        # Popular tags section
        popular_tags_label = QLabel("Popular Tags:")
        popular_tags_label.setStyleSheet(label_style)
        popular_tags_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        details_layout.addWidget(popular_tags_label, row, 0, Qt.AlignmentFlag.AlignTop)

        # Create popular tags widget
        self.popular_tags_widget = self.create_popular_tags_widget()
        details_layout.addWidget(self.popular_tags_widget, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1
        
        details_tab.setLayout(details_layout)
        tab_widget.addTab(details_tab, "Details")
        
        # Photos tab
        photos_tab = QWidget()
        photos_layout = QVBoxLayout()
        
        # Photo buttons
        photo_buttons_layout = QHBoxLayout()
        self.add_photo_btn = QPushButton("Add Photos")
        self.add_photo_btn.clicked.connect(self.add_photos)
        photo_buttons_layout.addWidget(self.add_photo_btn)
        photo_buttons_layout.addStretch()
        
        photos_layout.addLayout(photo_buttons_layout)
        
        # Photo scroll area
        self.photo_scroll = QScrollArea()
        self.photo_widget = QWidget()
        self.photo_layout = QGridLayout()
        self.photo_widget.setLayout(self.photo_layout)
        self.photo_scroll.setWidget(self.photo_widget)
        self.photo_scroll.setWidgetResizable(True)
        self.photo_scroll.setMinimumHeight(200)
        
        photos_layout.addWidget(self.photo_scroll)
        photos_tab.setLayout(photos_layout)
        tab_widget.addTab(photos_tab, "Photos")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_form(self):
        """Populate form with existing figure data."""
        if not self.figure_data:
            return
            
        self.name_edit.setText(self.figure_data.get('name', ''))
        self.series_edit.setText(self.figure_data.get('series', ''))
        self.wave_edit.setText(self.figure_data.get('wave', ''))
        
        # Handle manufacturer combo box
        manufacturer = self.figure_data.get('manufacturer', '')
        if manufacturer:
            # Check if manufacturer exists in combo box
            index = self.manufacturer_combo.findText(manufacturer)
            if index >= 0:
                self.manufacturer_combo.setCurrentIndex(index)
            else:
                # Add it to the combo box and select it
                self.manufacturer_combo.addItem(manufacturer)
                self.manufacturer_combo.setCurrentText(manufacturer)
        
        if self.figure_data.get('year'):
            self.year_spin.setValue(int(self.figure_data['year']))
            
        self.scale_combo.setCurrentText(self.figure_data.get('scale', ''))
        self.condition_combo.setCurrentText(self.figure_data.get('condition', ''))
        
        if self.figure_data.get('purchase_price'):
            self.purchase_price_spin.setValue(float(self.figure_data['purchase_price']))
            
        self.location_combo.setCurrentText(self.figure_data.get('location', ''))
        
        # Handle tags (notes field now contains comma-separated tags)
        notes_text = self.figure_data.get('notes', '')
        if notes_text:
            # Split by comma and clean up whitespace
            tags = [tag.strip() for tag in notes_text.split(',') if tag.strip()]
            self.notes_edit.set_tags(tags)
        else:
            self.notes_edit.clear_tags()
        
        # Load existing photos if editing
        if self.is_edit_mode and hasattr(self, 'parent') and hasattr(self.parent(), 'db'):
            figure_id = self.figure_data.get('id')
            if figure_id:
                photos = self.parent().db.get_figure_photos(figure_id)
                self.photos = [photo['file_path'] for photo in photos]
                self.update_photo_display()
    
    def add_photos(self):
        """Add photos to the figure."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Photos",
            "",
            "Image Files (*.jpg *.jpeg *.png *.gif *.bmp)"
        )
        
        if file_paths:
            for file_path in file_paths:
                self.photos.append(file_path)
            self.update_photo_display()
    
    def update_photo_display(self):
        """Update the photo display grid."""
        # Clear existing photos
        for i in reversed(range(self.photo_layout.count())):
            self.photo_layout.itemAt(i).widget().setParent(None)
        
        # Add photos in grid
        row, col = 0, 0
        max_cols = 4
        
        for photo_path in self.photos:
            photo_widget = PhotoWidget(photo_path, QSize(100, 100))
            self.photo_layout.addWidget(photo_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def get_form_data(self) -> Dict:
        """Get form data as dictionary."""
        return {
            'name': self.name_edit.text().strip(),
            'series': self.series_edit.text().strip(),
            'wave': self.wave_edit.text().strip(),
            'manufacturer': self.manufacturer_combo.currentText().strip(),
            'year': self.year_spin.value() if self.year_spin.value() > 1900 else None,
            'scale': self.scale_combo.currentText().strip(),
            'condition': self.condition_combo.currentText(),
            'purchase_price': self.purchase_price_spin.value() if self.purchase_price_spin.value() > 0 else None,
            'location': self.location_combo.currentText().strip(),
            'notes': self.notes_edit.get_tags_as_string()
        }
    
    def accept(self):
        """Validate and accept the dialog."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            self.name_edit.setFocus()
            return
            
        super().accept()
    
    def add_manufacturer(self):
        """Add a new manufacturer to the dropdown list."""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(
            self, 
            'Add Manufacturer', 
            'Enter new manufacturer name:'
        )
        
        if ok and text.strip():
            manufacturer_name = text.strip()
            
            # Check if it already exists
            if self.manufacturer_combo.findText(manufacturer_name) == -1:
                # Add to combo box
                self.manufacturer_combo.addItem(manufacturer_name)
                self.manufacturer_combo.setCurrentText(manufacturer_name)
                
                # Save to a simple text file for persistence
                try:
                    manufacturers_file = os.path.join(self.parent().data_dir, "manufacturers.txt")
                    with open(manufacturers_file, "a", encoding="utf-8") as f:
                        f.write(f"{manufacturer_name}\n")
                except (Exception, AttributeError):
                    pass  # Fail silently if can't write to file
            else:
                # Select existing item
                self.manufacturer_combo.setCurrentText(manufacturer_name)
    
    def add_location(self):
        """Add a new location to the dropdown list."""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(
            self, 
            'Add Location', 
            'Enter new location name:'
        )
        
        if ok and text.strip():
            location_name = text.strip()
            
            # Check if it already exists
            if self.location_combo.findText(location_name) == -1:
                # Add to combo box
                self.location_combo.addItem(location_name)
                self.location_combo.setCurrentText(location_name)
                
                # Save to a simple text file for persistence
                try:
                    locations_file = os.path.join(self.parent().data_dir, "locations.txt")
                    with open(locations_file, "a", encoding="utf-8") as f:
                        f.write(f"{location_name}\n")
                except (Exception, AttributeError):
                    pass  # Fail silently if can't write to file
            else:
                # Select existing item
                self.location_combo.setCurrentText(location_name)

    def get_popular_tags(self):
        """Get the most popular tags from existing figures."""
        if not hasattr(self, 'parent') or not hasattr(self.parent(), 'db'):
            return []

        try:
            # Get all figures and extract tags from notes field
            figures = self.parent().db.get_all_figures()
            tag_counts = {}

            for figure in figures:
                notes = figure.get('notes', '')
                if notes:
                    # Split by comma and count each tag
                    tags = [tag.strip() for tag in notes.split(',') if tag.strip()]
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Sort by frequency and return top 10
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            return [tag for tag, count in sorted_tags[:10]]

        except Exception:
            return []

    def create_popular_tags_widget(self):
        """Create a widget displaying popular tags."""
        popular_tags = self.get_popular_tags()

        if not popular_tags:
            no_tags_label = QLabel("No tags found yet")
            no_tags_label.setStyleSheet("color: #6c757d; font-style: italic;")
            return no_tags_label

        # Create a widget to hold the popular tags
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Create flow layout for tags
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(5)
        tags_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for popular tags
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(40)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        tags_container = QWidget()
        tags_container.setLayout(tags_layout)
        scroll_area.setWidget(tags_container)

        # Add popular tags as clickable buttons
        for tag in popular_tags:
            tag_btn = QPushButton(tag)
            tag_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e9ecef;
                    border: 1px solid #ced4da;
                    border-radius: 12px;
                    padding: 4px 8px;
                    font-size: 10px;
                    color: #495057;
                }
                QPushButton:hover {
                    background-color: #dee2e6;
                    border-color: #adb5bd;
                }
            """)
            tag_btn.clicked.connect(lambda checked, t=tag: self.add_popular_tag(t))
            tags_layout.addWidget(tag_btn)

        layout.addWidget(scroll_area)
        return container

    def add_popular_tag(self, tag):
        """Add a popular tag to the current tags."""
        current_tags = self.notes_edit.get_tags()
        if tag not in current_tags:
            self.notes_edit.add_tag(tag)


class OMACMainWindow(QMainWindow):
    """Main application window for OMAC - One 'Mazing Action Catalog."""
    
    def __init__(self):
        super().__init__()
        
        # Set data directory based on platform
        if platform.system() == 'Darwin':  # macOS
            self.data_dir = os.path.expanduser('~/Library/Application Support/OMAC')
            os.makedirs(self.data_dir, exist_ok=True)
            self.photos_dir = os.path.join(self.data_dir, 'photos')
            os.makedirs(self.photos_dir, exist_ok=True)
            db_path = os.path.join(self.data_dir, 'action_figures.db')
        elif platform.system() == 'Linux':  # Linux
            self.data_dir = os.path.expanduser('~/Documents/OMAC')
            os.makedirs(self.data_dir, exist_ok=True)
            self.photos_dir = os.path.join(self.data_dir, 'photos')
            os.makedirs(self.photos_dir, exist_ok=True)
            db_path = os.path.join(self.data_dir, 'action_figures.db')
        else:  # Other platforms (Windows, etc.)
            self.data_dir = '.'
            self.photos_dir = 'photos'
            db_path = 'action_figures.db'
        
        self.db = DatabaseManager(db_path)
        self.photo_manager = PhotoManager(self.photos_dir)
        self.current_figure_id = None
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Sorting state
        self.sort_column = 'name'  # Default sort column
        self.sort_order = 'ASC'    # Default sort order
        
        # Auto-save control
        self.auto_save_enabled = False  # Start with auto-save disabled
        
        self.init_ui()
        # Temporarily disconnect the resize signal to prevent saving during loading
        # Note: Signal is connected in init_ui() table setup
        self.load_collection()
        
        # Column settings will be loaded after window is shown in showEvent
        
        # Load saved theme preference
        self.load_theme_preference()
        
        # Auto-save will be enabled after geometry loading in showEvent
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("OMAC - One 'Mazing Action Catalog")
        # Note: Default geometry is now set in main() after window creation
        # to allow saved geometry to be restored properly
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        self.create_central_widget()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
    def load_column_widths(self):
        """Load saved column widths from settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Load saved column widths
        loaded_any = False
        for col in range(self.collection_table.columnCount()):
            width_value = settings.value(f"column_width_{col}")
            if width_value is not None:
                try:
                    width = int(width_value)
                    if width > 0:
                        self.collection_table.setColumnWidth(col, width)
                        loaded_any = True
                except (ValueError, TypeError):
                    pass
        
        # If no saved widths were loaded, use defaults
        if not loaded_any:
            default_widths = [250, 150, 120, 150, 80, 120, 100]
            for col in range(self.collection_table.columnCount()):
                width = default_widths[col] if col < len(default_widths) else 100
                self.collection_table.setColumnWidth(col, width)
        
        # Load window geometry
        # Note: Geometry is now loaded in main() before window.show()
        # geometry = settings.value("window_geometry")
        # if geometry:
        #     print(f"Loading window geometry: {geometry}")  # Debug info
        #     self.restoreGeometry(geometry)
        # else:
        #     print("No saved window geometry found")  # Debug info
        
        # Load window state (for splitter positions, etc.)
        # Note: State is now loaded in main() before window.show()
        # state = settings.value("window_state")
        # if state:
        #     print(f"Loading window state: {state}")  # Debug info
        #     self.restoreState(state)
        # else:
        #     print("No saved window state found")  # Debug info
    
    def apply_column_percentages(self):
        """Apply saved column percentages to current table viewport width."""
        if not hasattr(self, 'saved_column_percentages') or not self.saved_column_percentages:
            return
            
        # Get available width for columns (table viewport width)
        viewport_width = self.collection_table.viewport().width()
        
        # If viewport width is not available, skip
        if viewport_width <= 0:
            return
        
        # Temporarily disconnect the resize signal to prevent recursive saving
        self.collection_table.horizontalHeader().sectionResized.disconnect(self.save_column_widths)
        
        # Calculate and set column widths based on percentages
        for col, percentage in enumerate(self.saved_column_percentages):
            if col < self.collection_table.columnCount():
                width = int((percentage / 100.0) * viewport_width)
                if width > 0:
                    self.collection_table.setColumnWidth(col, width)
        
    def save_column_widths(self):
        """Save current column widths as absolute values to settings."""
        # Set flag to prevent dynamic resizing during manual column resize
        self._manual_column_resize = True
        
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Save absolute column widths
        for col in range(self.collection_table.columnCount()):
            width = self.collection_table.columnWidth(col)
            settings.setValue(f"column_width_{col}", width)
        
        # Force settings to be written to disk
        settings.sync()
        
        # Clear flag after a short delay
        QTimer.singleShot(100, lambda: setattr(self, '_manual_column_resize', False))
        
        # Save window geometry
        settings.setValue("window_geometry", self.saveGeometry())
        
        # Save window state
        settings.setValue("window_state", self.saveState())
        
        # Save menu bar position if it's detached
        menubar = self.menuBar()
        if menubar and not menubar.isNativeMenuBar():
            # Menu bar is detached, save its geometry
            settings.setValue("menubar_geometry", menubar.geometry())
            settings.setValue("menubar_visible", menubar.isVisible())
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        
        # Save geometry when window is resized (only after initialization)
        if hasattr(self, 'auto_save_enabled') and self.auto_save_enabled:
            self.save_window_geometry_silent()
        
        # Note: Dynamic column resizing disabled to preserve manual column adjustments
    
    def moveEvent(self, event):
        """Handle window move events."""
        super().moveEvent(event)
        # Save geometry when window is moved (only after initialization)
        if hasattr(self, 'auto_save_enabled') and self.auto_save_enabled:
            self.save_window_geometry_silent()
    
    def showEvent(self, event):
        """Handle window show events - load geometry when window is first shown."""
        super().showEvent(event)
        # Load saved geometry when window is first shown
        if not hasattr(self, '_geometry_loaded'):
            self._geometry_loaded = True
            # Use QTimer to ensure the event loop has processed the show
            QTimer.singleShot(0, self.load_window_geometry_and_columns)
    
    def closeEvent(self, event):
        """Handle application close event."""
        try:
            # Save application state
            self.save_column_widths()
            self.save_column_visibility()
            self.save_column_order()
            
            # Save window geometry and state directly
            settings = QSettings("OMAC", "ActionFigureCatalog")
            
            # Save individual geometry components
            settings.setValue("window_x", self.x())
            settings.setValue("window_y", self.y())
            settings.setValue("window_width", self.width())
            settings.setValue("window_height", self.height())
            settings.sync()  # Force immediate write to disk

            # Clean up any running threads or background processes
            # Note: Qt will automatically clean up child widgets and threads

            # Call parent close event
            super().closeEvent(event)

        except Exception as e:
            # Log the error but don't prevent closing
            print(f"Error during application shutdown: {e}")
            super().closeEvent(event)
    
    def save_window_geometry(self):
        """Manually save current window geometry and state."""
        try:
            settings = QSettings("OMAC", "ActionFigureCatalog")
            geometry = self.saveGeometry()
            state = self.saveState()
            
            settings.setValue("window_geometry", geometry)
            settings.setValue("window_state", state)
            settings.sync()  # Force immediate write to disk
            
            # Show confirmation message
            QMessageBox.information(
                self,
                "Window Position Saved",
                "Current window position and size have been saved.\n"
                "They will be restored the next time you start OMAC."
            )
            
            print(f"Window geometry manually saved: {geometry}")
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save window position: {e}"
            )
            print(f"Error saving window geometry: {e}")
    
    def save_window_geometry_silent(self):
        """Silently save current window geometry and state (no user notification)."""
        if not self.auto_save_enabled:
            return  # Skip auto-save during initialization
            
        try:
            settings = QSettings("OMAC", "ActionFigureCatalog")
            # Save individual geometry components
            settings.setValue("window_x", self.x())
            settings.setValue("window_y", self.y())
            settings.setValue("window_width", self.width())
            settings.setValue("window_height", self.height())
            settings.sync()  # Force immediate write to disk
            
            # Also save horizontal scroll position as part of geometry
            self.save_horizontal_scroll_position()
            
            print(f"Window geometry auto-saved: x={self.x()}, y={self.y()}, w={self.width()}, h={self.height()}")
            
        except Exception as e:
            print(f"Error auto-saving window geometry: {e}")
    
    def load_window_geometry(self):
        """Load and restore saved window geometry."""
        try:
            # Temporarily disable auto-save to prevent overwriting during loading
            was_auto_save_enabled = getattr(self, 'auto_save_enabled', False)
            self.auto_save_enabled = False
            
            settings = QSettings("OMAC", "ActionFigureCatalog")
            # Try to load individual geometry components
            x = settings.value("window_x")
            y = settings.value("window_y")
            width = settings.value("window_width")
            height = settings.value("window_height")
            
            if x is not None and y is not None and width is not None and height is not None:
                try:
                    x, y, width, height = int(x), int(y), int(width), int(height)
                    
                    # Set the geometry directly
                    self.setGeometry(x, y, width, height)
                    
                    # Ensure the window is visible on screen
                    screen = QApplication.primaryScreen().availableGeometry()
                    
                    # Check if window is partially or fully off-screen or too small
                    window_rect = self.geometry()
                    if (window_rect.right() < screen.left() or 
                        window_rect.bottom() < screen.top() or 
                        window_rect.left() > screen.right() or 
                        window_rect.top() > screen.bottom() or
                        window_rect.width() < 400 or 
                        window_rect.height() < 300):
                        self.center_on_screen()
                except (ValueError, TypeError) as e:
                    print(f"Error parsing geometry values: {e}")
                    self.center_on_screen()
            else:
                self.center_on_screen()
                
            # Re-enable auto-save
            self.auto_save_enabled = True
                
        except Exception as e:
            print(f"Error loading window geometry: {e}")
            self.center_on_screen()
            # Re-enable auto-save even on error
            self.auto_save_enabled = was_auto_save_enabled
    
    def load_window_geometry_and_columns(self):
        """Load window geometry and column settings after window is shown."""
        # First load geometry
        self.load_window_geometry()
        
        # Then reload column settings with correct table size
        self.load_column_settings()
    
    def center_on_screen(self):
        """Center the window on the primary screen with reasonable default size."""
        screen = QApplication.primaryScreen().availableGeometry()
        default_width = min(1200, screen.width() - 100)
        default_height = min(800, screen.height() - 100)
        
        x = (screen.width() - default_width) // 2
        y = (screen.height() - default_height) // 2
        
        self.setGeometry(x, y, default_width, default_height)
        print(f"Centered window: x={x}, y={y}, w={default_width}, h={default_height}")
    
    def show_column_context_menu(self, position):
        """Show context menu for column management."""
        header = self.collection_table.horizontalHeader()
        column = header.logicalIndexAt(position.x())
        
        if column < 0:
            return
            
        menu = QMenu(self)
        
        # Add show/hide actions for each column
        for col in range(self.collection_table.columnCount()):
            column_name = self.collection_table.horizontalHeaderItem(col).text()
            action = QAction(f"Show {column_name}", self)
            action.setCheckable(True)
            action.setChecked(not self.collection_table.isColumnHidden(col))
            action.setData(col)
            action.triggered.connect(self.toggle_column_visibility)
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Add reset columns action
        reset_action = QAction("Reset Column Layout", self)
        reset_action.triggered.connect(self.reset_column_layout)
        menu.addAction(reset_action)
        
        menu.exec(header.mapToGlobal(position))
    
    def toggle_column_visibility(self):
        """Toggle visibility of a column."""
        action = self.sender()
        if action:
            column = action.data()
            visible = action.isChecked()
            self.collection_table.setColumnHidden(column, not visible)
            self.save_column_visibility()
    
    def reset_column_layout(self):
        """Reset columns to default layout."""
        # Show all columns
        for col in range(self.collection_table.columnCount()):
            self.collection_table.setColumnHidden(col, False)
        
        # Reset column order (move columns back to original positions)
        header = self.collection_table.horizontalHeader()
        for logical_index in range(self.collection_table.columnCount()):
            visual_index = header.visualIndex(logical_index)
            if visual_index != logical_index:
                header.moveSection(visual_index, logical_index)
        
        # Reset column widths to default percentages
        default_percentages = [30.0, 20.0, 20.0, 10.0, 15.0, 5.0]  # Name, Series, Manufacturer, Year, Condition, Photos
        viewport_width = self.collection_table.viewport().width()
        if viewport_width > 0:
            for col, percentage in enumerate(default_percentages):
                width = int((percentage / 100.0) * viewport_width)
                self.collection_table.setColumnWidth(col, width)
        
        # Save the reset state
        self.save_column_visibility()
        self.save_column_order()
        self.save_column_widths()
    
    def save_column_visibility(self):
        """Save column visibility settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        for col in range(self.collection_table.columnCount()):
            visible = not self.collection_table.isColumnHidden(col)
            settings.setValue(f"column_visible_{col}", visible)
    
    def save_column_order(self):
        """Save column order settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        header = self.collection_table.horizontalHeader()
        for logical_index in range(self.collection_table.columnCount()):
            visual_index = header.visualIndex(logical_index)
            settings.setValue(f"column_order_{logical_index}", visual_index)
        settings.sync()
    
    def save_horizontal_scroll_position(self):
        """Save horizontal scroll bar position."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        scroll_position = self.collection_table.horizontalScrollBar().value()
        settings.setValue("horizontal_scroll_position", scroll_position)
        settings.sync()
    
    def load_horizontal_scroll_position(self):
        """Load horizontal scroll bar position."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        scroll_position = settings.value("horizontal_scroll_position", 0, type=int)
        self.collection_table.horizontalScrollBar().setValue(scroll_position)
    
    def load_column_settings(self):
        """Load column visibility, order, and width settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Load column visibility
        for col in range(self.collection_table.columnCount()):
            visible = settings.value(f"column_visible_{col}", True, type=bool)
            self.collection_table.setColumnHidden(col, not visible)
        
        # Load column order
        header = self.collection_table.horizontalHeader()
        # First, collect all the visual positions
        order_map = {}
        for logical_index in range(self.collection_table.columnCount()):
            visual_index = settings.value(f"column_order_{logical_index}", logical_index, type=int)
            order_map[logical_index] = visual_index
        
        # Apply the ordering by moving sections
        # We need to be careful about the order of operations
        for logical_index in range(self.collection_table.columnCount()):
            target_visual = order_map[logical_index]
            current_visual = header.visualIndex(logical_index)
            if current_visual != target_visual:
                # Move this logical index to its target visual position
                header.moveSection(current_visual, target_visual)
        
        # Load column widths (existing functionality)
        self.load_column_widths()
        
        # Load horizontal scroll position
        self.load_horizontal_scroll_position()
    
    # Duplicate load_column_widths definition removed to avoid conflicts; functionality is defined above.
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        # Create custom menu bar widget for cross-platform compatibility
        self.menubar = QWidget()
        self.menubar.setObjectName("menubar")  # For theme-specific styling
        self.menubar.setFixedHeight(25)
        # Note: Styling is now handled by theme_manager.get_theme_stylesheet()
        
        menubar_layout = QHBoxLayout()
        menubar_layout.setContentsMargins(5, 0, 5, 0)
        menubar_layout.setSpacing(10)
        
        # File menu button
        self.file_menu_button = QPushButton("File")
        self.file_menu_button.setFlat(True)
        self.file_menu_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 2px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.file_menu = QMenu(self.file_menu_button)
        self.file_menu_button.setMenu(self.file_menu)
        
        add_action = QAction('&Add Figure', self)
        add_action.setShortcut('Ctrl+N')
        add_action.triggered.connect(self.add_figure)
        self.file_menu.addAction(add_action)
        
        self.file_menu.addSeparator()
        
        export_action = QAction('&Backup Database && Photos', self)
        export_action.triggered.connect(self.export_database)
        self.file_menu.addAction(export_action)
        
        restore_action = QAction('&Restore Database && Photos', self)
        restore_action.triggered.connect(self.restore_database)
        self.file_menu.addAction(restore_action)
        
        merge_action = QAction('&Merge Collections...', self)
        merge_action.triggered.connect(self.merge_collections)
        self.file_menu.addAction(merge_action)
        
        self.file_menu.addSeparator()
        
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        
        # View menu button
        self.view_menu_button = QPushButton("View")
        self.view_menu_button.setFlat(True)
        self.view_menu_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 2px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.view_menu = QMenu(self.view_menu_button)
        self.view_menu_button.setMenu(self.view_menu)
        
        refresh_action = QAction('&Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.load_collection)
        self.view_menu.addAction(refresh_action)
        
        # Theme submenu
        self.view_menu.addSeparator()
        theme_menu = self.view_menu.addMenu('&Theme')
        
        light_theme_action = QAction('&Light Theme', self)
        light_theme_action.triggered.connect(self.switch_to_light_theme)
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('&Dark Theme', self)
        dark_theme_action.triggered.connect(self.switch_to_dark_theme)
        theme_menu.addAction(dark_theme_action)
        
        dracula_theme_action = QAction('&Dracula Theme', self)
        dracula_theme_action.triggered.connect(self.switch_to_dracula_theme)
        theme_menu.addAction(dracula_theme_action)
        
        self.view_menu.addSeparator()
        
        save_geometry_action = QAction('&Save Window Position && Size', self)
        save_geometry_action.setShortcut('Ctrl+S')
        save_geometry_action.triggered.connect(self.save_window_geometry)
        self.view_menu.addAction(save_geometry_action)
        
        # Help menu button
        self.help_menu_button = QPushButton("Help")
        self.help_menu_button.setFlat(True)
        self.help_menu_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 2px 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.help_menu = QMenu(self.help_menu_button)
        self.help_menu_button.setMenu(self.help_menu)
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(about_action)
        
        menubar_layout.addWidget(self.file_menu_button)
        menubar_layout.addWidget(self.view_menu_button)
        menubar_layout.addWidget(self.help_menu_button)
        menubar_layout.addStretch()
        
        self.menubar.setLayout(menubar_layout)
        self.menubar.show()  # Make sure it's visible
        
    def create_central_widget(self):
        """Create the central widget with main content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls and table side by side
        left_panel = QWidget()
        left_layout = QHBoxLayout()  # Horizontal layout for controls + table
        
        # Left sidebar with action buttons and search
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setMaximumWidth(150)  # Limit sidebar width
        
        # Search bar at the top
        search_widget = QWidget()
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(5, 5, 5, 5)
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-weight: bold; margin-bottom: 2px;")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search collection...")
        self.search_edit.textChanged.connect(self.search_collection)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_widget.setLayout(search_layout)
        sidebar_layout.addWidget(search_widget)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("margin: 5px 0px;")
        sidebar_layout.addWidget(separator)
        
        # Action buttons
        self.add_button = QPushButton("Add Figure")
        self.add_button.clicked.connect(self.add_figure)
        self.add_button.setMinimumHeight(35)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        sidebar_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Figure")
        self.edit_button.clicked.connect(self.edit_figure)
        self.edit_button.setMinimumHeight(35)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #0b5a0b;
            }
            QPushButton:pressed {
                background-color: #0a4f0a;
            }
        """)
        sidebar_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Figure")
        self.delete_button.clicked.connect(self.delete_figure)
        self.delete_button.setMinimumHeight(35)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #b91d1f;
            }
            QPushButton:pressed {
                background-color: #9a181a;
            }
        """)
        sidebar_layout.addWidget(self.delete_button)
        
        self.wishlist_button = QPushButton("Wishlist")
        self.wishlist_button.clicked.connect(self.open_wishlist)
        self.wishlist_button.setMinimumHeight(35)
        self.wishlist_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        sidebar_layout.addWidget(self.wishlist_button)
        
        sidebar_layout.addStretch()  # Push buttons to top
        sidebar_widget.setLayout(sidebar_layout)
        
        # Collection table
        self.collection_table = QTableWidget()
        self.collection_table.setColumnCount(7)
        self.collection_table.setHorizontalHeaderLabels([
            "Name", "Series", "Wave", "Manufacturer", "Year", "Condition", "Photos"
        ])
        self.collection_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.collection_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.collection_table.cellDoubleClicked.connect(self.edit_figure)
        
        # Enable sorting
        self.collection_table.setSortingEnabled(True)
        self.collection_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Enable column moving and context menu
        header = self.collection_table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow column reordering
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_column_context_menu)
        
        # Connect to column resize signal to save widths
        self.collection_table.horizontalHeader().sectionResized.connect(self.save_column_widths)
        # Connect to column move signal to save order
        self.collection_table.horizontalHeader().sectionMoved.connect(self.save_column_order)
        # Connect to horizontal scroll bar to save position
        self.collection_table.horizontalScrollBar().valueChanged.connect(self.save_horizontal_scroll_position)
        
        # Initialize collection view manager
        self.collection_view = CollectionView(self.collection_table, self.theme_manager)
        
        # Add sidebar and table to left layout
        left_layout.addWidget(sidebar_widget)
        left_layout.addWidget(self.collection_table)
        left_panel.setLayout(left_layout)
        
        # Right panel - Details and photos
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Details group
        details_group = QGroupBox("Figure Details")
        details_layout = QVBoxLayout()
        
        self.details_label = QLabel("Select a figure to view details")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #000000;
            }
        """)
        
        details_layout.addWidget(self.details_label)
        details_group.setLayout(details_layout)
        
        # Photos group
        photos_group = QGroupBox("Photos")
        photos_layout = QVBoxLayout()
        
        self.photos_scroll = QScrollArea()
        self.photos_widget = QWidget()
        self.photos_layout = QGridLayout()
        self.photos_widget.setLayout(self.photos_layout)
        self.photos_scroll.setWidget(self.photos_widget)
        self.photos_scroll.setWidgetResizable(True)
        self.photos_scroll.setMinimumHeight(200)
        
        photos_layout.addWidget(self.photos_scroll)
        photos_group.setLayout(photos_layout)
        
        right_layout.addWidget(details_group)
        right_layout.addWidget(photos_group)
        right_panel.setLayout(right_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.menubar)  # Add menu bar at the top
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
    def load_collection(self):
        """Load the action figure collection into the table."""
        try:
            figures = self.db.get_all_figures(self.collection_view.get_sort_column_name(), self.collection_view.sort_order)
            self.collection_view.load_figures(figures)
            self.update_status_bar()
            self.update_header_sort_indicator()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load collection: {str(e)}")
            self.status_bar.showMessage("Failed to load collection", 5000)
        
    def search_collection(self, search_term: str):
        """Search the collection based on search term."""
        try:
            if search_term.strip():
                figures = self.db.search_figures(search_term, self.collection_view.get_sort_column_name(), self.collection_view.sort_order)
            else:
                figures = self.db.get_all_figures(self.collection_view.get_sort_column_name(), self.collection_view.sort_order)
                
            self.collection_view.load_figures(figures)
            self.update_header_sort_indicator()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to search collection: {str(e)}")
            self.status_bar.showMessage("Failed to search collection", 5000)
        
    def on_selection_changed(self):
        """Handle selection change in collection table."""
        figure_id = self.collection_view.get_selected_figure_id()
        if figure_id is not None:
            self.show_figure_details(figure_id)
                
    def on_header_clicked(self, logical_index: int):
        """Handle header click for sorting."""
        # Toggle sort order if same column clicked again
        if self.collection_view.sort_column == logical_index:
            self.collection_view.sort_order = 'DESC' if self.collection_view.sort_order == 'ASC' else 'ASC'
        else:
            self.collection_view.sort_column = logical_index
            self.collection_view.sort_order = 'ASC'  # Default to ascending for new column
        
        # Update header to show sort indicator
        self.update_header_sort_indicator()
        
        # Reload collection with new sorting
        self.load_collection()
            
    def update_header_sort_indicator(self):
        """Update the header to show sort indicator for current sort column."""
        header = self.collection_table.horizontalHeader()
        column_names = ['name', 'series', 'wave', 'manufacturer', 'year', 'condition', 'photos']
        
        # Reset all headers to default
        for i in range(len(column_names)):
            current_text = header.model().headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if current_text:
                # Remove any existing sort indicators
                clean_text = current_text.replace(' ↑', '').replace(' ↓', '')
                header.model().setHeaderData(i, Qt.Orientation.Horizontal, clean_text, Qt.ItemDataRole.DisplayRole)
        
        # Add sort indicator to current sort column
        column_index = self.collection_view.sort_column
        if 0 <= column_index < len(column_names):
            current_text = header.model().headerData(column_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if current_text:
                indicator = ' ↑' if self.collection_view.sort_order == 'ASC' else ' ↓'
                header.model().setHeaderData(column_index, Qt.Orientation.Horizontal, current_text + indicator, Qt.ItemDataRole.DisplayRole)
                
    def show_figure_details(self, figure_id: int):
        """Show detailed information for a specific figure."""
        self.current_figure_id = figure_id
        figure = self.db.get_figure(figure_id)
        
        if not figure:
            return
            
        # Update details
        purchase_price = figure.get('purchase_price')
        if purchase_price is None:
            purchase_price_str = "N/A"
        else:
            purchase_price_str = f"${purchase_price:.2f}"

        # Handle tags display
        notes_text = figure.get('notes', '')
        if notes_text:
            # Parse tags from comma-separated string
            tags = [tag.strip() for tag in notes_text.split(',') if tag.strip()]
            tags_html = self.create_tags_html(tags)
            tags_display = f"<p><b>Tags:</b></p>{tags_html}"
        else:
            tags_display = "<p><b>Tags:</b> None</p>"

        details_text = f"""
        <h3>{figure.get('name', 'Unknown')}</h3>
        <p><b>Series:</b> {figure.get('series', 'N/A')}</p>
        <p><b>Manufacturer:</b> {figure.get('manufacturer', 'N/A')}</p>
        <p><b>Year:</b> {figure.get('year', 'N/A')}</p>
        <p><b>Scale:</b> {figure.get('scale', 'N/A')}</p>
        <p><b>Condition:</b> {figure.get('condition', 'N/A')}</p>
        <p><b>Purchase Price:</b> {purchase_price_str}</p>
        <p><b>Location:</b> {figure.get('location', 'N/A')}</p>
        {tags_display}
        """
        
        self.details_label.setText(details_text)
        
        # Load photos
        self.load_figure_photos(figure_id)
        
    def load_figure_photos(self, figure_id: int):
        """Load photos for the selected figure."""
        # Clear existing photos
        for i in reversed(range(self.photos_layout.count())):
            self.photos_layout.itemAt(i).widget().setParent(None)
            
        photos = self.db.get_figure_photos(figure_id)
        
        if not photos:
            no_photos_label = QLabel("No photos available")
            no_photos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_photos_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-style: italic;
                    padding: 20px;
                }
            """)
            self.photos_layout.addWidget(no_photos_label, 0, 0)
            return
            
        # Add photos in grid
        row, col = 0, 0
        max_cols = 3
        
        for photo in photos:
            photo_widget = PhotoWidget(photo['file_path'])
            photo_widget.clicked.connect(self.view_photo)
            self.photos_layout.addWidget(photo_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def view_photo(self, file_path: str):
        """View a photo in full size."""
        viewer = ImageViewerDialog(file_path, self)
        viewer.exec()
        
    def create_tags_html(self, tags):
        """Create HTML for displaying tags as bubbles."""
        if not tags:
            return ""
        
        # Get theme colors for styling
        app = QApplication.instance()
        if app:
            palette = app.palette()
            bg_color = palette.color(QPalette.ColorRole.Highlight).name()
            text_color = palette.color(QPalette.ColorRole.HighlightedText).name()
        else:
            bg_color = "#0078d4"
            text_color = "#ffffff"
        
        tag_html_parts = []
        for tag in tags:
            tag_html = f"""
            <span style="
                display: inline-block;
                background-color: {bg_color};
                color: {text_color};
                border-radius: 12px;
                padding: 4px 8px;
                margin: 2px 4px 2px 0px;
                font-size: 11px;
                font-weight: normal;
                border: 1px solid {bg_color};
            ">{tag}</span>
            """
            tag_html_parts.append(tag_html)
        
        return "".join(tag_html_parts)
        
    def add_figure(self):
        """Add a new action figure."""
        try:
            dialog = ActionFigureDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                form_data = dialog.get_form_data()
                figure_id = self.db.add_figure(form_data)
                
                # Add photos if any were selected
                if dialog.photos:
                    copied_paths = self.photo_manager.copy_photos_to_collection(dialog.photos, figure_id)
                    
                    for i, photo_path in enumerate(copied_paths):
                        is_primary = i == 0  # First photo is primary
                        self.db.add_photo(figure_id, photo_path, is_primary=is_primary)
                
                self.load_collection()
                self.status_bar.showMessage("Figure added successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add figure: {str(e)}")
            self.status_bar.showMessage("Failed to add figure", 5000)
            
    def edit_figure(self):
        """Edit the selected action figure."""
        try:
            if self.current_figure_id is None:
                QMessageBox.warning(self, "No Selection", "Please select a figure to edit.")
                return
                
            figure = self.db.get_figure(self.current_figure_id)
            dialog = ActionFigureDialog(self, figure)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                form_data = dialog.get_form_data()
                success = self.db.update_figure(self.current_figure_id, form_data)
                
                if success:
                    # Handle photos - delete existing photos and add new ones
                    # First, get existing photos
                    existing_photos = self.db.get_figure_photos(self.current_figure_id)
                    
                    # Delete existing photos from database and filesystem
                    for photo in existing_photos:
                        photo_path = photo['file_path']
                        if os.path.exists(photo_path):
                            try:
                                os.remove(photo_path)
                            except Exception:
                                pass  # Continue even if file deletion fails
                        self.db.delete_photo(photo['id'])
                    
                    # Add new photos if any were selected
                    if dialog.photos:
                        copied_paths = self.photo_manager.copy_photos_to_collection(dialog.photos, self.current_figure_id)
                        
                        for i, photo_path in enumerate(copied_paths):
                            is_primary = i == 0  # First photo is primary
                            self.db.add_photo(self.current_figure_id, photo_path, is_primary=is_primary)
                    
                    self.load_collection()
                    self.show_figure_details(self.current_figure_id)
                    self.status_bar.showMessage("Figure updated successfully", 3000)
                else:
                    QMessageBox.warning(self, "Update Error", "Could not update figure.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit figure: {str(e)}")
            self.status_bar.showMessage("Failed to edit figure", 5000)
                
    def delete_figure(self):
        """Delete the selected action figure."""
        try:
            if self.current_figure_id is None:
                QMessageBox.warning(self, "No Selection", "Please select a figure to delete.")
                return
                
            figure = self.db.get_figure(self.current_figure_id)
            if not figure:
                return
                
            reply = QMessageBox.question(
                self,
                "Delete Figure",
                f"Are you sure you want to delete '{figure['name']}'?\n\nThis will also delete all associated photos.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.db.delete_figure(self.current_figure_id)
                if success:
                    self.current_figure_id = None
                    self.collection_view.clear_selection()
                    self.load_collection()
                    self.details_label.setText("Select a figure to view details")
                    # Clear photos
                    for i in reversed(range(self.photos_layout.count())):
                        self.photos_layout.itemAt(i).widget().setParent(None)
                    self.status_bar.showMessage("Figure deleted successfully", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", "Could not delete figure.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete figure: {str(e)}")
            self.status_bar.showMessage("Failed to delete figure", 5000)
                
    def open_wishlist(self):
        """Open the wishlist dialog."""
        from wishlist_dialog import WishlistDialog
        dialog = WishlistDialog(self, db=self.db)
        dialog.exec()
        # Refresh collection in case items were moved from wishlist
        self.load_collection()
                
    def export_database(self):
        """Create a complete backup of database and photos."""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(self.data_dir, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate timestamp for backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Show progress dialog
            progress = QProgressDialog("Creating backup...", "Cancel", 0, 5, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Step 1: Export database to CSV
            progress.setLabelText("Exporting database...")
            csv_filename = f"action_figures_{timestamp}.csv"
            csv_path = os.path.join(backup_dir, csv_filename)
            
            figures = self.db.get_all_figures('name', 'ASC')
            if figures:
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if figures:
                        fieldnames = figures[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(figures)
            
            progress.setValue(1)
            if progress.wasCanceled():
                return
            
            # Step 2: Export photo metadata to CSV
            progress.setLabelText("Exporting photo metadata...")
            photos_csv_filename = f"photos_{timestamp}.csv"
            photos_csv_path = os.path.join(backup_dir, photos_csv_filename)
            
            all_photos = self.db.get_all_photos()
            if all_photos:
                with open(photos_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if all_photos:
                        fieldnames = all_photos[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(all_photos)
            
            progress.setValue(2)
            if progress.wasCanceled():
                return
            
            # Step 3: Create tar archive of photos
            progress.setLabelText("Archiving photos...")
            tar_filename = f"photos_{timestamp}.tar.gz"
            tar_path = os.path.join(backup_dir, tar_filename)
            
            if os.path.exists(self.photos_dir) and os.listdir(self.photos_dir):
                with tarfile.open(tar_path, "w:gz") as tar:
                    tar.add(self.photos_dir, arcname="photos")
            
            progress.setValue(3)
            if progress.wasCanceled():
                return
            
            # Step 4: Create zip file containing everything
            progress.setLabelText("Creating backup archive...")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add figures CSV file if it exists
                if os.path.exists(csv_path):
                    zipf.write(csv_path, csv_filename)
                
                # Add photos CSV file if it exists
                if os.path.exists(photos_csv_path):
                    zipf.write(photos_csv_path, photos_csv_filename)
                
                # Add tar file if it exists
                if os.path.exists(tar_path):
                    zipf.write(tar_path, tar_filename)
                
                # Add a README file with backup info
                readme_content = f"""OMAC Action Figure Collection Backup
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This backup contains:
- Database export: {csv_filename if os.path.exists(csv_path) else 'No figures in collection'}
- Photo metadata: {photos_csv_filename if os.path.exists(photos_csv_path) else 'No photo metadata'}
- Photos archive: {tar_filename if os.path.exists(tar_path) else 'No photos in collection'}

To restore:
1. Extract this zip file
2. Import the CSV file back into OMAC
3. Extract the photos archive to restore photo files
"""
                zipf.writestr("README.txt", readme_content)
            
            progress.setValue(4)
            if progress.wasCanceled():
                return
            
            # Step 5: Clean up temporary files
            progress.setLabelText("Cleaning up...")
            if os.path.exists(csv_path):
                os.remove(csv_path)
            if os.path.exists(photos_csv_path):
                os.remove(photos_csv_path)
            if os.path.exists(tar_path):
                os.remove(tar_path)
            
            progress.setValue(5)
            
            # Show success message
            QMessageBox.information(
                self, "Backup Complete", 
                f"Backup created successfully!\n\nFile: {backup_path}\n\n"
                f"The backup includes your complete collection database and all photos."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Backup Error", 
                f"An error occurred while creating the backup:\n\n{str(e)}"
            )
        
    def restore_database(self):
        """Restore database and photos from a backup archive."""
        try:
            # Show file dialog to select backup file
            backup_dir = os.path.join(self.data_dir, "backups")
            backup_file, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", backup_dir, 
                "Backup Files (*.zip);;All Files (*)"
            )
            
            if not backup_file:
                return
            
            # Validate backup file exists
            if not os.path.exists(backup_file):
                QMessageBox.critical(self, "Restore Error", "Selected backup file does not exist.")
                return
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self, "Confirm Restore",
                "This will replace your current collection with the backup data.\n\n"
                "Do you want to create a backup of your current data first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            # Create backup of current data if requested
            if reply == QMessageBox.StandardButton.Yes:
                self.export_database()
            
            # Show progress dialog
            progress = QProgressDialog("Restoring from backup...", "Cancel", 0, 5, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Step 1: Extract backup to temporary directory
            progress.setLabelText("Extracting backup...")
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    for member in zipf.infolist():
                        member_name = member.filename
                        if os.path.isabs(member_name) or member_name.startswith('..'):
                            raise Exception("Unsafe paths in ZIP file")
                    zipf.extractall(temp_dir)
                
                # Find the extracted files
                csv_file = None
                tar_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith('.csv'):
                        csv_file = os.path.join(temp_dir, file)
                    elif file.endswith('.tar.gz'):
                        tar_file = os.path.join(temp_dir, file)
                
                if not csv_file:
                    raise Exception("No CSV file found in backup")
                
                progress.setValue(1)
                if progress.wasCanceled():
                    return
                
                # Step 2: Clear existing data
                progress.setLabelText("Clearing existing data...")
                self.db.clear_all_data()
                
                progress.setValue(2)
                if progress.wasCanceled():
                    return
                
                # Step 3: Import CSV data
                progress.setLabelText("Importing database...")
                with open(csv_file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Convert string values to appropriate types
                        figure_data = {}
                        for key, value in row.items():
                            if key in ['id', 'year', 'photo_count']:
                                figure_data[key] = int(value) if value else 0
                            elif key in ['purchase_price', 'current_value']:
                                figure_data[key] = float(value) if value else 0.0
                            elif key in ['purchase_date', 'created_at', 'updated_at']:
                                # Keep dates as strings, database will handle them
                                figure_data[key] = value
                            else:
                                figure_data[key] = value
                        
                        # Remove id to let database auto-generate
                        figure_data.pop('id', None)
                        # Update timestamps
                        now = datetime.now().isoformat()
                        figure_data['created_at'] = now
                        figure_data['updated_at'] = now
                        
                        self.db.add_figure(figure_data)
                
                progress.setValue(3)
                if progress.wasCanceled():
                    return
                
                # Step 4: Restore photos
                if tar_file and os.path.exists(tar_file):
                    progress.setLabelText("Restoring photos...")
                    # Clear existing photos directory
                    if os.path.exists(self.photos_dir):
                        shutil.rmtree(self.photos_dir)
                    os.makedirs(self.photos_dir)
                    
                    # Extract photos safely
                    with tarfile.open(tar_file, "r:gz") as tar:
                        def is_within_directory(directory, target):
                            abs_directory = os.path.abspath(directory)
                            abs_target = os.path.abspath(target)
                            return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

                        for member in tar.getmembers():
                            member_path = os.path.join(self.photos_dir, member.name)
                            if not is_within_directory(self.photos_dir, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                        tar.extractall(path=self.photos_dir)
                
                progress.setValue(4)
                if progress.wasCanceled():
                    return
                
                # Step 5: Refresh UI
                progress.setLabelText("Refreshing display...")
                self.load_collection()
                self.update_status_bar()
                
                progress.setValue(5)
            
            # Show success message
            QMessageBox.information(
                self, "Restore Complete", 
                "Database and photos have been successfully restored from backup!\n\n"
                "Your collection has been updated with the backup data."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Restore Error", 
                f"An error occurred while restoring from backup:\n\n{str(e)}"
            )
        
    def merge_collections(self):
        """Merge data from another collection into the current one."""
        from merge_collections import MergeCollectionsDialog
        dialog = MergeCollectionsDialog(self, db=self.db, photos_dir=self.photos_dir)
        dialog.exec()
        
    def update_status_bar(self):
        """Update the status bar with collection statistics."""
        stats = self.db.get_database_stats()
        status_text = (f"Collection: {stats['total_figures']} figures | "
                      f"Photos: {stats['total_photos']} | "
                      f"Total Value: ${stats['total_value']:.2f}")
        self.status_bar.showMessage(status_text)
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About OMAC",
            "OMAC - One 'Mazing Action Catalog\n\n"
            "A comprehensive database application for managing\n"
            "action figure collections with photo support.\n\n"
            "Built with Python and PyQt6\n"
            "Database: SQLite"
        )

    def load_theme_preference(self):
        """Load and apply the saved theme preference."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        theme = settings.value("theme", ThemeManager.LIGHT_THEME)
        try:
            self.theme_manager.set_theme(theme)
            self.collection_view.update_theme()
        except ValueError:
            # Fallback to light theme if invalid theme is saved
            self.theme_manager.set_theme(ThemeManager.LIGHT_THEME)
            self.collection_view.update_theme()

    def save_theme_preference(self):
        """Save the current theme preference."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        settings.setValue("theme", self.theme_manager.get_current_theme())

    def switch_to_light_theme(self):
        """Switch to light theme."""
        self.theme_manager.set_theme(ThemeManager.LIGHT_THEME)
        self.save_theme_preference()
        self.collection_view.update_theme()

    def switch_to_dark_theme(self):
        """Switch to dark theme."""
        self.theme_manager.set_theme(ThemeManager.DARK_THEME)
        self.save_theme_preference()
        self.collection_view.update_theme()

    def switch_to_dracula_theme(self):
        """Switch to Dracula theme."""
        self.theme_manager.set_theme(ThemeManager.DRACULA_THEME)
        self.save_theme_preference()
        self.collection_view.update_theme()


def main():
    """Main function - entry point of the application."""
    try:
        # Set up Unix signal handling for clean shutdown
        setup_unix_signals()
        
        # Create QApplication instance
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("OMAC")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("One 'Mazing ActionFigure Team")

        # Handle cleanup on application exit
        app.aboutToQuit.connect(on_application_quit)

        # Create and show main window
        window = OMACMainWindow()
        
        window.show()

        # Start event loop
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


def setup_unix_signals():
    """Set up Unix signal handling for clean Qt application shutdown."""
    # Create a socket pair for signal handling
    read_socket, write_socket = socket.socketpair()
    
    def signal_handler(signum, frame):
        """Handle Unix signals by writing to the socket."""
        write_socket.send(b'1')
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create a QSocketNotifier to monitor the socket
    notifier = QSocketNotifier(read_socket.fileno(), QSocketNotifier.Type.Read)
    
    def handle_signal():
        """Handle the signal by closing the application."""
        notifier.setEnabled(False)
        read_socket.recv(1)  # Clear the socket
        QApplication.quit()
        notifier.setEnabled(True)
    
    notifier.activated.connect(handle_signal)


def on_application_quit():
    """Handle application quit cleanup."""
    try:
        # Any final cleanup can go here
        print("Application shutting down gracefully...")
    except Exception as e:
        print(f"Error during application quit: {e}")


if __name__ == "__main__":
    main()