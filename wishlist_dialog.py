"""
Wishlist management dialog for OMAC.

Allows users to manage their wishlist of desired action figures.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from database import DatabaseManager
from typing import Dict, List, Optional


class WishlistDialog(QDialog):
    """Dialog for managing the wishlist."""

    item_moved_to_collection = pyqtSignal(dict)  # Emitted when item is moved to collection

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wishlist Management")
        self.setModal(True)
        self.resize(1000, 700)

        self.db = DatabaseManager()
        self.current_item_id = None

        self.init_ui()
        self.load_wishlist()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()

        # Left side - Wishlist table
        self.left_widget = QFrame()
        left_layout = QVBoxLayout()

        # Wishlist table
        table_group = QGroupBox("Wishlist Items")
        table_layout = QVBoxLayout()

        self.wishlist_table = QTableWidget()
        self.wishlist_table.setColumnCount(6)
        self.wishlist_table.setHorizontalHeaderLabels(["Name", "Series", "Wave", "Manufacturer", "Priority", "Target Price"])
        self.wishlist_table.horizontalHeader().setStretchLastSection(True)
        self.wishlist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.wishlist_table.itemSelectionChanged.connect(self.on_item_selected)

        table_layout.addWidget(self.wishlist_table)
        table_group.setLayout(table_layout)
        left_layout.addWidget(table_group)

        # Action buttons (will be in full-width bar below splitter)
        self.add_btn = QPushButton("Add Item")
        self.add_btn.clicked.connect(self.add_item)

        self.edit_btn = QPushButton("Edit Item")
        self.edit_btn.clicked.connect(self.edit_item)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete Item")
        self.delete_btn.clicked.connect(self.delete_item)
        self.delete_btn.setEnabled(False)

        self.move_to_collection_btn = QPushButton("Move to Collection")
        self.move_to_collection_btn.clicked.connect(self.move_to_collection)
        self.move_to_collection_btn.setEnabled(False)
        self.move_to_collection_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")

        self.left_widget.setLayout(left_layout)

        # Right side - Item details
        self.right_widget = QFrame()
        right_layout = QVBoxLayout()

        details_group = QGroupBox("Item Details")
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Figure name")
        self.name_edit.setMinimumWidth(250)
        form_layout.addRow("Name:", self.name_edit)

        self.series_edit = QLineEdit()
        self.series_edit.setPlaceholderText("Series name")
        self.series_edit.setMinimumWidth(250)
        form_layout.addRow("Series:", self.series_edit)

        self.wave_edit = QLineEdit()
        self.wave_edit.setPlaceholderText("Wave (e.g., Wave 1, Series 1)")
        self.wave_edit.setMinimumWidth(250)
        form_layout.addRow("Wave:", self.wave_edit)

        self.manufacturer_edit = QLineEdit()
        self.manufacturer_edit.setPlaceholderText("Manufacturer")
        self.manufacturer_edit.setMinimumWidth(250)
        form_layout.addRow("Manufacturer:", self.manufacturer_edit)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(2024)
        form_layout.addRow("Year:", self.year_spin)

        self.scale_edit = QLineEdit()
        self.scale_edit.setPlaceholderText("Scale (e.g., 1/6, 1/12)")
        self.scale_edit.setMinimumWidth(250)
        form_layout.addRow("Scale:", self.scale_edit)

        self.target_price_spin = QDoubleSpinBox()
        self.target_price_spin.setRange(0, 10000)
        self.target_price_spin.setPrefix("$")
        self.target_price_spin.setDecimals(2)
        form_layout.addRow("Target Price:", self.target_price_spin)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])
        self.priority_combo.setCurrentText("medium")
        form_layout.addRow("Priority:", self.priority_combo)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)

        details_group.setLayout(form_layout)
        right_layout.addWidget(details_group)

        # Form buttons
        form_buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_item)
        self.save_btn.setEnabled(False)
        form_buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        form_buttons_layout.addWidget(self.cancel_btn)

        right_layout.addLayout(form_buttons_layout)

        right_layout.addStretch()
        self.right_widget.setLayout(right_layout)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([500, 400])

        layout.addWidget(self.splitter)

        # Full-width button bar with close button on the right
        button_bar_layout = QHBoxLayout()
        
        # Left side buttons (invisible spacers to align with left panel buttons)
        button_bar_layout.addWidget(self.add_btn)
        button_bar_layout.addWidget(self.edit_btn)
        button_bar_layout.addWidget(self.delete_btn)
        button_bar_layout.addWidget(self.move_to_collection_btn)
        
        # Stretch to push close button to the right
        button_bar_layout.addStretch()
        
        # Close button on the right
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_bar_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_bar_layout)

        self.setLayout(layout)

    def load_wishlist(self):
        """Load wishlist items into the table."""
        items = self.db.get_all_wishlist_items()

        self.wishlist_table.setRowCount(len(items))

        for row, item in enumerate(items):
            self.wishlist_table.setItem(row, 0, QTableWidgetItem(item.get('name', '')))
            self.wishlist_table.setItem(row, 1, QTableWidgetItem(item.get('series', '')))
            self.wishlist_table.setItem(row, 2, QTableWidgetItem(item.get('wave', '')))
            self.wishlist_table.setItem(row, 3, QTableWidgetItem(item.get('manufacturer', '')))
            self.wishlist_table.setItem(row, 4, QTableWidgetItem(item.get('priority', 'medium')))

            target_price = item.get('target_price', 0)
            price_text = f"${target_price:.2f}" if target_price else ""
            self.wishlist_table.setItem(row, 5, QTableWidgetItem(price_text))

            # Store the item ID in the row
            self.wishlist_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, item['id'])

    def on_item_selected(self):
        """Handle item selection in the table."""
        selected_rows = set()
        for item in self.wishlist_table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) == 1:
            row = list(selected_rows)[0]
            item_id = self.wishlist_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

            # Load item details
            items = self.db.get_all_wishlist_items()
            item = next((i for i in items if i['id'] == item_id), None)

            if item:
                self.current_item_id = item_id
                self.load_item_details(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.move_to_collection_btn.setEnabled(True)
        else:
            self.clear_item_details()
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.move_to_collection_btn.setEnabled(False)

    def load_item_details(self, item: Dict):
        """Load item details into the form."""
        self.name_edit.setText(item.get('name', ''))
        self.series_edit.setText(item.get('series', ''))
        self.wave_edit.setText(item.get('wave', ''))
        self.manufacturer_edit.setText(item.get('manufacturer', ''))
        self.year_spin.setValue(item.get('year', 2024) or 2024)
        self.scale_edit.setText(item.get('scale', ''))
        self.target_price_spin.setValue(item.get('target_price', 0) or 0)
        self.priority_combo.setCurrentText(item.get('priority', 'medium'))
        self.notes_edit.setText(item.get('notes', ''))

    def clear_item_details(self):
        """Clear the item details form."""
        self.current_item_id = None
        self.name_edit.clear()
        self.series_edit.clear()
        self.wave_edit.clear()
        self.manufacturer_edit.clear()
        self.year_spin.setValue(2024)
        self.scale_edit.clear()
        self.target_price_spin.setValue(0)
        self.priority_combo.setCurrentText("medium")
        self.notes_edit.clear()

    def add_item(self):
        """Start adding a new item."""
        self.clear_item_details()
        self.save_btn.setEnabled(True)
        self.name_edit.setFocus()

    def edit_item(self):
        """Start editing the selected item."""
        self.save_btn.setEnabled(True)
        self.name_edit.setFocus()

    def save_item(self):
        """Save the current item."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return

        item_data = {
            'name': self.name_edit.text().strip(),
            'series': self.series_edit.text().strip(),
            'wave': self.wave_edit.text().strip(),
            'manufacturer': self.manufacturer_edit.text().strip(),
            'year': self.year_spin.value(),
            'scale': self.scale_edit.text().strip(),
            'target_price': self.target_price_spin.value(),
            'priority': self.priority_combo.currentText(),
            'notes': self.notes_edit.toPlainText().strip()
        }

        try:
            if self.current_item_id:
                # Update existing item
                self.db.update_wishlist_item(self.current_item_id, item_data)
            else:
                # Add new item
                self.db.add_wishlist_item(item_data)

            self.load_wishlist()
            self.clear_item_details()
            self.save_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save item: {str(e)}")

    def cancel_edit(self):
        """Cancel editing."""
        self.clear_item_details()
        self.save_btn.setEnabled(False)

    def delete_item(self):
        """Delete the selected item."""
        if not self.current_item_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this wishlist item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_wishlist_item(self.current_item_id)
                self.load_wishlist()
                self.clear_item_details()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.move_to_collection_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

    def move_to_collection(self):
        """Move the selected item to the main collection."""
        if not self.current_item_id:
            return

        # Get current item data
        items = self.db.get_all_wishlist_items()
        item = next((i for i in items if i['id'] == self.current_item_id), None)

        if not item:
            return

        # Show dialog to add acquisition details
        from main import ActionFigureDialog

        # Pre-populate with wishlist data
        figure_data = {
            'name': item.get('name', ''),
            'series': item.get('series', ''),
            'wave': item.get('wave', ''),
            'manufacturer': item.get('manufacturer', ''),
            'year': item.get('year'),
            'scale': item.get('scale', ''),
            'notes': item.get('notes', '')
        }

        dialog = ActionFigureDialog(self, figure_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            acquired_data = dialog.get_form_data()

            try:
                # Move to collection
                figure_id = self.db.move_wishlist_to_collection(self.current_item_id, acquired_data)

                # Emit signal for main window to refresh
                self.item_moved_to_collection.emit(acquired_data)

                # Refresh wishlist
                self.load_wishlist()
                self.clear_item_details()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.move_to_collection_btn.setEnabled(False)

                QMessageBox.information(self, "Success", "Item moved to collection!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to move item: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to move item: {str(e)}")