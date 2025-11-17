#!/usr/bin/env python3
"""
OMAC - One 'Mazing ActionFigure Catalog

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
from datetime import datetime
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QScrollArea,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QDateEdit, QSplitter, QGroupBox, QListWidget,
    QListWidgetItem, QFrame, QToolBar, QStatusBar, QMenuBar, QMenu,
    QProgressDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QSize, pyqtSignal, QSettings
from PyQt6.QtGui import (
    QAction, QFont, QPixmap, QIcon, QPainter, QPen, QBrush,
    QColor, QPalette
)
from database import DatabaseManager
from merge_collections import MergeCollectionsDialog


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
            with open("manufacturers.txt", "r", encoding="utf-8") as f:
                for line in f:
                    manufacturer = line.strip()
                    if manufacturer:
                        self.saved_manufacturers.add(manufacturer)
        except FileNotFoundError:
            pass  # File doesn't exist yet, that's okay
    
    def load_locations(self):
        """Load locations from saved file."""
        self.saved_locations = set()
        try:
            with open("locations.txt", "r", encoding="utf-8") as f:
                for line in f:
                    location = line.strip()
                    if location:
                        self.saved_locations.add(location)
        except FileNotFoundError:
            pass  # File doesn't exist yet, that's okay
    
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

        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)
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
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet(label_style)
        notes_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        details_layout.addWidget(notes_label, row, 0, Qt.AlignmentFlag.AlignTop)
        details_layout.addWidget(self.notes_edit, row, 1, Qt.AlignmentFlag.AlignLeft)
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
        self.notes_edit.setText(self.figure_data.get('notes', ''))
        
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
            'manufacturer': self.manufacturer_combo.currentText().strip(),
            'year': self.year_spin.value() if self.year_spin.value() > 1900 else None,
            'scale': self.scale_combo.currentText().strip(),
            'condition': self.condition_combo.currentText(),
            'purchase_price': self.purchase_price_spin.value() if self.purchase_price_spin.value() > 0 else None,
            'location': self.location_combo.currentText().strip(),
            'notes': self.notes_edit.toPlainText().strip()
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
                    with open("manufacturers.txt", "a", encoding="utf-8") as f:
                        f.write(f"{manufacturer_name}\n")
                except Exception:
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
                    with open("locations.txt", "a", encoding="utf-8") as f:
                        f.write(f"{location_name}\n")
                except Exception:
                    pass  # Fail silently if can't write to file
            else:
                # Select existing item
                self.location_combo.setCurrentText(location_name)


class OMACMainWindow(QMainWindow):
    """Main application window for OMAC - One 'Mazing ActionFigure Catalog."""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_figure_id = None
        self.init_ui()
        # Temporarily disconnect the resize signal to prevent saving during loading
        self.collection_table.horizontalHeader().sectionResized.disconnect(self.save_column_widths)
        self.load_collection()
        # Reconnect the signal
        self.collection_table.horizontalHeader().sectionResized.connect(self.save_column_widths)
        
        # Load saved column settings (visibility, order, widths)
        self.load_column_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("OMAC - One 'Mazing ActionFigure Catalog")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        self.create_central_widget()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
    def load_column_widths(self):
        """Load saved column width percentages from settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Default column width percentages if no settings exist
        default_percentages = [30.0, 20.0, 20.0, 10.0, 15.0, 5.0]  # Name, Series, Manufacturer, Year, Condition, Photos
        
        # Load saved percentages
        saved_percentages = []
        has_saved_data = False
        
        for col in range(self.collection_table.columnCount()):
            percentage_value = settings.value(f"column_percentage_{col}")
            if percentage_value is not None:
                try:
                    percentage = float(percentage_value)
                    if 0 <= percentage <= 100:
                        saved_percentages.append(percentage)
                        has_saved_data = True
                    else:
                        saved_percentages.append(default_percentages[col] if col < len(default_percentages) else 10.0)
                except (ValueError, TypeError):
                    saved_percentages.append(default_percentages[col] if col < len(default_percentages) else 10.0)
            else:
                saved_percentages.append(default_percentages[col] if col < len(default_percentages) else 10.0)
        
        # Apply the widths based on percentages if we have saved data
        if has_saved_data and saved_percentages:
            # Get available width for columns (table viewport width)
            viewport_width = self.collection_table.viewport().width()
            
            # If viewport width is not yet available (during startup), use a reasonable default
            if viewport_width <= 0:
                viewport_width = 800  # Default table width
            
            # Calculate and set column widths based on percentages
            for col, percentage in enumerate(saved_percentages):
                width = int((percentage / 100.0) * viewport_width)
                if width > 0:
                    self.collection_table.setColumnWidth(col, width)
        else:
            # Fall back to default absolute widths
            default_widths = [200, 150, 150, 80, 120, 80]
            for col in range(self.collection_table.columnCount()):
                width = default_widths[col] if col < len(default_widths) else 100
                self.collection_table.setColumnWidth(col, width)
        
        # Load window geometry
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load window state (for splitter positions, etc.)
        state = settings.value("window_state")
        if state:
            self.restoreState(state)
    
    def save_column_widths(self):
        """Save current column widths as percentages to settings."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Calculate total width of all columns
        total_width = sum(self.collection_table.columnWidth(col) for col in range(self.collection_table.columnCount()))
        
        if total_width > 0:
            # Save column width percentages
            for col in range(self.collection_table.columnCount()):
                width = self.collection_table.columnWidth(col)
                percentage = (width / total_width) * 100.0
                settings.setValue(f"column_percentage_{col}", percentage)
        
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
        """Handle window resize events to maintain column proportions."""
        super().resizeEvent(event)
        
        # Only adjust columns if we have saved percentage data
        settings = QSettings("OMAC", "ActionFigureCatalog")
        has_percentage_data = any(settings.value(f"column_percentage_{col}") is not None 
                                for col in range(self.collection_table.columnCount()))
        
        if has_percentage_data:
            # Load saved percentages and recalculate widths
            saved_percentages = []
            for col in range(self.collection_table.columnCount()):
                percentage_value = settings.value(f"column_percentage_{col}")
                if percentage_value is not None:
                    try:
                        percentage = float(percentage_value)
                        if 0 <= percentage <= 100:
                            saved_percentages.append(percentage)
                        else:
                            saved_percentages.append(10.0)  # fallback
                    except (ValueError, TypeError):
                        saved_percentages.append(10.0)  # fallback
                else:
                    saved_percentages.append(10.0)  # fallback
            
            # Get available width for columns
            viewport_width = self.collection_table.viewport().width()
            if viewport_width > 0:
                # Calculate and set column widths based on percentages
                for col, percentage in enumerate(saved_percentages):
                    width = int((percentage / 100.0) * viewport_width)
                    if width > 0:
                        self.collection_table.setColumnWidth(col, width)
    
    def closeEvent(self, event):
        """Handle application close event."""
        try:
            # Save application state
            self.save_column_widths()
            self.save_column_visibility()
            self.save_column_order()

            # Clean up any running threads or background processes
            # Note: Qt will automatically clean up child widgets and threads

            # Call parent close event
            super().closeEvent(event)

        except Exception as e:
            # Log the error but don't prevent closing
            print(f"Error during application shutdown: {e}")
            super().closeEvent(event)
    
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
    
    def load_column_widths(self):
        """Load saved column widths."""
        settings = QSettings("OMAC", "ActionFigureCatalog")
        
        # Check if we have saved percentage data
        has_percentage_data = any(settings.value(f"column_percentage_{col}") is not None 
                                for col in range(self.collection_table.columnCount()))
        
        if has_percentage_data:
            # Load saved percentages and apply widths
            saved_percentages = []
            for col in range(self.collection_table.columnCount()):
                percentage_value = settings.value(f"column_percentage_{col}")
                if percentage_value is not None:
                    try:
                        percentage = float(percentage_value)
                        if 0 <= percentage <= 100:
                            saved_percentages.append(percentage)
                        else:
                            saved_percentages.append(10.0)  # fallback
                    except (ValueError, TypeError):
                        saved_percentages.append(10.0)  # fallback
                else:
                    saved_percentages.append(10.0)  # fallback
            
            # Get available width for columns
            viewport_width = self.collection_table.viewport().width()
            if viewport_width > 0:
                # Calculate and set column widths based on percentages
                for col, percentage in enumerate(saved_percentages):
                    width = int((percentage / 100.0) * viewport_width)
                    if width > 0:
                        self.collection_table.setColumnWidth(col, width)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        # Create custom menu bar widget for cross-platform compatibility
        self.menubar = QWidget()
        self.menubar.setFixedHeight(25)
        self.menubar.setStyleSheet("""
            QWidget {
                background-color: palette(window);
                border-bottom: 1px solid palette(dark);
            }
        """)
        
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
        
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        toolbar.setObjectName("main_toolbar")  # Set object name to avoid Qt warnings
        self.addToolBar(toolbar)
        
        # Toolbar is now minimal - search moved to sidebar
        
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
        
        sidebar_layout.addStretch()  # Push buttons to top
        sidebar_widget.setLayout(sidebar_layout)
        
        # Collection table
        self.collection_table = QTableWidget()
        self.collection_table.setColumnCount(6)
        self.collection_table.setHorizontalHeaderLabels([
            "Name", "Series", "Manufacturer", "Year", "Condition", "Photos"
        ])
        self.collection_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.collection_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.collection_table.cellDoubleClicked.connect(self.edit_figure)
        
        # Enable column moving and context menu
        header = self.collection_table.horizontalHeader()
        header.setSectionsMovable(True)  # Allow column reordering
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.show_column_context_menu)
        
        # Connect to column resize signal to save widths
        self.collection_table.horizontalHeader().sectionResized.connect(self.save_column_widths)
        # Connect to column move signal to save order
        self.collection_table.horizontalHeader().sectionMoved.connect(self.save_column_order)
        
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
        figures = self.db.get_all_figures()
        
        self.collection_table.setRowCount(len(figures))
        
        for row, figure in enumerate(figures):
            self.collection_table.setItem(row, 0, QTableWidgetItem(figure.get('name', '')))
            self.collection_table.setItem(row, 1, QTableWidgetItem(figure.get('series', '')))
            self.collection_table.setItem(row, 2, QTableWidgetItem(figure.get('manufacturer', '')))
            self.collection_table.setItem(row, 3, QTableWidgetItem(str(figure.get('year', ''))))
            self.collection_table.setItem(row, 4, QTableWidgetItem(figure.get('condition', '')))
            self.collection_table.setItem(row, 5, QTableWidgetItem(str(figure.get('photo_count', 0))))
            
            # Store figure ID in first column
            self.collection_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, figure['id'])
        
        self.collection_table.resizeColumnsToContents()
        self.update_status_bar()
        
    def search_collection(self, search_term: str):
        """Search the collection based on search term."""
        if search_term.strip():
            figures = self.db.search_figures(search_term)
        else:
            figures = self.db.get_all_figures()
            
        self.collection_table.setRowCount(len(figures))
        
        for row, figure in enumerate(figures):
            self.collection_table.setItem(row, 0, QTableWidgetItem(figure.get('name', '')))
            self.collection_table.setItem(row, 1, QTableWidgetItem(figure.get('series', '')))
            self.collection_table.setItem(row, 2, QTableWidgetItem(figure.get('manufacturer', '')))
            self.collection_table.setItem(row, 3, QTableWidgetItem(str(figure.get('year', ''))))
            self.collection_table.setItem(row, 4, QTableWidgetItem(figure.get('condition', '')))
            self.collection_table.setItem(row, 5, QTableWidgetItem(str(figure.get('photo_count', 0))))
            
            # Store figure ID in first column
            self.collection_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, figure['id'])
        
        self.collection_table.resizeColumnsToContents()
        
    def on_selection_changed(self):
        """Handle selection change in collection table."""
        current_row = self.collection_table.currentRow()
        if current_row >= 0:
            item = self.collection_table.item(current_row, 0)
            if item:
                figure_id = item.data(Qt.ItemDataRole.UserRole)
                self.show_figure_details(figure_id)
                
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

        details_text = f"""
        <h3>{figure.get('name', 'Unknown')}</h3>
        <p><b>Series:</b> {figure.get('series', 'N/A')}</p>
        <p><b>Manufacturer:</b> {figure.get('manufacturer', 'N/A')}</p>
        <p><b>Year:</b> {figure.get('year', 'N/A')}</p>
        <p><b>Scale:</b> {figure.get('scale', 'N/A')}</p>
        <p><b>Condition:</b> {figure.get('condition', 'N/A')}</p>
        <p><b>Purchase Price:</b> {purchase_price_str}</p>
        <p><b>Location:</b> {figure.get('location', 'N/A')}</p>
        <p><b>Notes:</b> {figure.get('notes', 'None')}</p>
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
        
    def add_figure(self):
        """Add a new action figure."""
        dialog = ActionFigureDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            form_data = dialog.get_form_data()
            figure_id = self.db.add_figure(form_data)
            
            # Add photos if any were selected
            if dialog.photos:
                # Create photos directory if it doesn't exist
                os.makedirs("photos", exist_ok=True)
                
                for i, photo_path in enumerate(dialog.photos):
                    # Copy photo to local directory
                    filename = f"figure_{figure_id}_{i+1}_{os.path.basename(photo_path)}"
                    new_path = os.path.join("photos", filename)
                    
                    try:
                        import shutil
                        shutil.copy2(photo_path, new_path)
                        is_primary = i == 0  # First photo is primary
                        self.db.add_photo(figure_id, new_path, is_primary=is_primary)
                    except Exception as e:
                        QMessageBox.warning(self, "Photo Error", f"Could not save photo: {str(e)}")
            
            self.load_collection()
            self.status_bar.showMessage("Figure added successfully", 3000)
            
    def edit_figure(self):
        """Edit the selected action figure."""
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
                    # Create photos directory if it doesn't exist
                    os.makedirs("photos", exist_ok=True)
                    
                    for i, photo_path in enumerate(dialog.photos):
                        # Copy photo to local directory
                        filename = f"figure_{self.current_figure_id}_{i+1}_{os.path.basename(photo_path)}"
                        new_path = os.path.join("photos", filename)
                        
                        try:
                            import shutil
                            shutil.copy2(photo_path, new_path)
                            is_primary = i == 0  # First photo is primary
                            self.db.add_photo(self.current_figure_id, new_path, is_primary=is_primary)
                        except Exception as e:
                            QMessageBox.warning(self, "Photo Error", f"Could not save photo: {str(e)}")
                
                self.load_collection()
                self.show_figure_details(self.current_figure_id)
                self.status_bar.showMessage("Figure updated successfully", 3000)
            else:
                QMessageBox.warning(self, "Update Error", "Could not update figure.")
                
    def delete_figure(self):
        """Delete the selected action figure."""
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
                self.load_collection()
                self.details_label.setText("Select a figure to view details")
                # Clear photos
                for i in reversed(range(self.photos_layout.count())):
                    self.photos_layout.itemAt(i).widget().setParent(None)
                self.status_bar.showMessage("Figure deleted successfully", 3000)
            else:
                QMessageBox.warning(self, "Delete Error", "Could not delete figure.")
                
    def export_database(self):
        """Create a complete backup of database and photos."""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate timestamp for backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Show progress dialog
            progress = QProgressDialog("Creating backup...", "Cancel", 0, 4, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Step 1: Export database to CSV
            progress.setLabelText("Exporting database...")
            csv_filename = f"action_figures_{timestamp}.csv"
            csv_path = os.path.join(backup_dir, csv_filename)
            
            figures = self.db.get_all_figures()
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
            
            # Step 2: Create tar archive of photos
            progress.setLabelText("Archiving photos...")
            tar_filename = f"photos_{timestamp}.tar.gz"
            tar_path = os.path.join(backup_dir, tar_filename)
            
            if os.path.exists("photos") and os.listdir("photos"):
                with tarfile.open(tar_path, "w:gz") as tar:
                    tar.add("photos", arcname="photos")
            
            progress.setValue(2)
            if progress.wasCanceled():
                return
            
            # Step 3: Create zip file containing both
            progress.setLabelText("Creating backup archive...")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add CSV file if it exists
                if os.path.exists(csv_path):
                    zipf.write(csv_path, csv_filename)
                
                # Add tar file if it exists
                if os.path.exists(tar_path):
                    zipf.write(tar_path, tar_filename)
                
                # Add a README file with backup info
                readme_content = f"""OMAC Action Figure Collection Backup
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This backup contains:
- Database export: {csv_filename if os.path.exists(csv_path) else 'No figures in collection'}
- Photos archive: {tar_filename if os.path.exists(tar_path) else 'No photos in collection'}

To restore:
1. Extract this zip file
2. Import the CSV file back into OMAC
3. Extract the photos archive to restore photo files
"""
                zipf.writestr("README.txt", readme_content)
            
            progress.setValue(3)
            if progress.wasCanceled():
                return
            
            # Step 4: Clean up temporary files
            progress.setLabelText("Cleaning up...")
            if os.path.exists(csv_path):
                os.remove(csv_path)
            if os.path.exists(tar_path):
                os.remove(tar_path)
            
            progress.setValue(4)
            
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
            backup_file, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", "backups/", 
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
                    if os.path.exists("photos"):
                        shutil.rmtree("photos")
                    os.makedirs("photos")
                    
                    # Extract photos
                    with tarfile.open(tar_file, "r:gz") as tar:
                        tar.extractall(".", filter='data')
                
                progress.setValue(4)
                if progress.wasCanceled():
                    return
                
                # Step 5: Refresh UI
                progress.setLabelText("Refreshing display...")
                self.load_figures()
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
        dialog = MergeCollectionsDialog(self)
        dialog.exec()
        
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
            "OMAC - One 'Mazing ActionFigure Catalog\n\n"
            "A comprehensive database application for managing\n"
            "action figure collections with photo support.\n\n"
            "Built with Python and PyQt6\n"
            "Database: SQLite"
        )


def main():
    """Main function - entry point of the application."""
    try:
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


def on_application_quit():
    """Handle application quit cleanup."""
    try:
        # Any final cleanup can go here
        print("Application shutting down gracefully...")
    except Exception as e:
        print(f"Error during application quit: {e}")


if __name__ == "__main__":
    main()