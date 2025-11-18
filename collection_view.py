"""
Collection view management for OMAC.
"""
from typing import List, Dict, Optional
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt


class CollectionView:
    """Manages the collection table display."""
    
    COLUMN_NAMES = ['name', 'series', 'wave', 'manufacturer', 'year', 'condition', 'photo_count']
    
    def __init__(self, table_widget: QTableWidget):
        self.table = table_widget
        self.sort_column = 0  # Default to name column
        self.sort_order = "ASC"
        self.setup_table()
    
    def setup_table(self):
        """Set up the table structure and headers."""
        headers = ["Name", "Series", "Wave", "Manufacturer", "Year", "Condition", "Photos"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column resize modes - make all columns interactively resizable
        header = self.table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        
        # Set reasonable default widths
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 150)  # Series
        header.resizeSection(2, 100)  # Wave
        header.resizeSection(3, 150)  # Manufacturer
        header.resizeSection(4, 80)   # Year
        header.resizeSection(5, 120)  # Condition
        header.resizeSection(6, 80)   # Photos
    
    def load_figures(self, figures: List[Dict]) -> None:
        """
        Load figures into the table.
        
        Args:
            figures: List of figure dictionaries
        """
        self.table.setRowCount(len(figures))
        
        for row, figure in enumerate(figures):
            self.table.setItem(row, 0, QTableWidgetItem(figure.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(figure.get('series', '')))
            self.table.setItem(row, 2, QTableWidgetItem(figure.get('wave', '')))
            self.table.setItem(row, 3, QTableWidgetItem(figure.get('manufacturer', '')))
            self.table.setItem(row, 4, QTableWidgetItem(str(figure.get('year', ''))))
            self.table.setItem(row, 5, QTableWidgetItem(figure.get('condition', '')))
            self.table.setItem(row, 6, QTableWidgetItem(str(figure.get('photo_count', 0))))
            
            # Store figure ID in first column
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, figure['id'])
        
        self.table.resizeColumnsToContents()
    
    def get_selected_figure_id(self) -> Optional[int]:
        """
        Get the ID of the currently selected figure.
        
        Returns:
            Figure ID or None if no selection
        """
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def clear_selection(self) -> None:
        """Clear the current table selection."""
        self.table.clearSelection()
    
    def set_sort_column(self, column: int, order: str) -> None:
        """
        Set the sort column and order.
        
        Args:
            column: Column index to sort by
            order: Sort order ("ASC" or "DESC")
        """
        self.sort_column = column
        self.sort_order = order
    
    def get_sort_info(self) -> tuple[int, str]:
        """
        Get current sort column and order.
        
        Returns:
            Tuple of (column, order)
        """
        return self.sort_column, self.sort_order
    
    def get_sort_column_name(self) -> str:
        """
        Get the current sort column name for database queries.
        
        Returns:
            Column name string
        """
        if 0 <= self.sort_column < len(self.COLUMN_NAMES):
            return self.COLUMN_NAMES[self.sort_column]
        return 'name'  # Default fallback