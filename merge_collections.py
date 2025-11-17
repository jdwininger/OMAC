#!/usr/bin/env python3
"""
Merge Collections Dialog for OMAC

Allows merging data from another OMAC collection into the current one,
with intelligent conflict resolution and duplicate handling.
"""

import os
import csv
import zipfile
import tarfile
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QListWidget, QListWidgetItem, QTextEdit, QCheckBox,
    QRadioButton, QButtonGroup, QProgressBar, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QFrame,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

from database import DatabaseManager


class MergeAnalysis:
    """Analyzes data for merging and identifies conflicts."""

    def __init__(self, source_data: Dict, target_db: DatabaseManager):
        self.source_figures = source_data.get('figures', [])
        self.source_photos = source_data.get('photos', [])
        self.target_db = target_db
        self.conflicts = []
        self.new_figures = []
        self.photo_conflicts = []

    def analyze(self) -> Dict:
        """Analyze the merge and return conflict information."""
        # Get existing figures for comparison
        existing_figures = self.target_db.get_all_figures()
        existing_figure_keys = set()

        # Create lookup keys for existing figures (name + series + manufacturer)
        for fig in existing_figures:
            key = (fig['name'].lower().strip(), fig.get('series', '').lower().strip(),
                   fig.get('manufacturer', '').lower().strip())
            existing_figure_keys.add(key)

        # Analyze each source figure
        for source_fig in self.source_figures:
            source_key = (source_fig['name'].lower().strip(),
                         source_fig.get('series', '').lower().strip(),
                         source_fig.get('manufacturer', '').lower().strip())

            if source_key in existing_figure_keys:
                # Find the matching existing figure
                matching_figure = None
                for existing_fig in existing_figures:
                    existing_key = (existing_fig['name'].lower().strip(),
                                   existing_fig.get('series', '').lower().strip(),
                                   existing_fig.get('manufacturer', '').lower().strip())
                    if existing_key == source_key:
                        matching_figure = existing_fig
                        break

                if matching_figure:
                    self.conflicts.append({
                        'type': 'figure_conflict',
                        'source': source_fig,
                        'target': matching_figure,
                        'resolution': 'skip'  # default
                    })
            else:
                self.new_figures.append(source_fig)

        # Analyze photo conflicts (same filenames)
        existing_photos = self.target_db.get_all_photos()
        existing_photo_files = set()

        for photo in existing_photos:
            if 'file_path' in photo:
                existing_photo_files.add(os.path.basename(photo['file_path']))

        for photo in self.source_photos:
            if 'file_path' in photo:
                filename = os.path.basename(photo['file_path'])
                if filename in existing_photo_files:
                    self.photo_conflicts.append({
                        'filename': filename,
                        'source_path': photo['file_path'],
                        'resolution': 'rename'  # default: rename incoming file
                    })

        return {
            'total_source_figures': len(self.source_figures),
            'new_figures': len(self.new_figures),
            'figure_conflicts': len(self.conflicts),
            'total_source_photos': len(self.source_photos),
            'photo_conflicts': len(self.photo_conflicts)
        }


class MergeWorker(QThread):
    """Worker thread for performing the merge operation."""

    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(dict)  # results
    error = pyqtSignal(str)

    def __init__(self, source_data: Dict, analysis: MergeAnalysis, options: Dict):
        super().__init__()
        self.source_data = source_data
        self.analysis = analysis
        self.options = options

    def run(self):
        """Perform the merge operation."""
        try:
            self.progress.emit("Starting merge...", 0)

            # Process new figures
            added_figures = 0
            if self.analysis.new_figures:
                self.progress.emit(f"Adding {len(self.analysis.new_figures)} new figures...", 20)
                for figure in self.analysis.new_figures:
                    # Prepare figure data
                    figure_data = figure.copy()
                    figure_data.pop('id', None)  # Remove ID for auto-generation
                    now = datetime.now().isoformat()
                    figure_data['created_at'] = now
                    figure_data['updated_at'] = now

                    self.analysis.target_db.add_figure(figure_data)
                    added_figures += 1

            # Process conflicts based on resolution strategy
            updated_figures = 0
            self.progress.emit("Processing figure conflicts...", 40)
            for conflict in self.analysis.conflicts:
                resolution = conflict.get('resolution', 'skip')

                if resolution == 'update':
                    # Update existing figure with source data
                    figure_data = conflict['source'].copy()
                    figure_data['id'] = conflict['target']['id']  # Keep target ID
                    figure_data['updated_at'] = datetime.now().isoformat()
                    self.analysis.target_db.update_figure(figure_data)
                    updated_figures += 1
                elif resolution == 'merge_photos':
                    # Add source photos to existing figure
                    self._merge_photos_for_figure(conflict['target']['id'], conflict['source'])
                    updated_figures += 1

            # Process photos
            added_photos = 0
            self.progress.emit("Processing photos...", 60)

            # Create photos directory if needed
            photos_dir = "photos"
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)

            # Copy source photos with conflict resolution
            for photo in self.source_data.get('photos', []):
                if 'file_path' in photo and os.path.exists(photo['file_path']):
                    filename = os.path.basename(photo['file_path'])

                    # Check for conflicts and resolve
                    final_filename = self._resolve_photo_filename(filename)

                    # Copy the photo
                    dest_path = os.path.join(photos_dir, final_filename)
                    shutil.copy2(photo['file_path'], dest_path)

                    # Find the figure ID for this photo
                    figure_id = self._find_figure_id_for_photo(photo, self.source_data.get('figures', []))

                    if figure_id:
                        # Add to database
                        photo_data = {
                            'figure_id': figure_id,
                            'file_path': dest_path,
                            'caption': photo.get('caption', ''),
                            'is_primary': photo.get('is_primary', False)
                        }
                        self.analysis.target_db.add_photo(photo_data)
                        added_photos += 1

            self.progress.emit("Finalizing merge...", 90)

            results = {
                'added_figures': added_figures,
                'updated_figures': updated_figures,
                'added_photos': added_photos,
                'skipped_conflicts': len([c for c in self.analysis.conflicts if c.get('resolution') == 'skip'])
            }

            self.progress.emit("Merge complete!", 100)
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def _resolve_photo_filename(self, filename: str) -> str:
        """Resolve photo filename conflicts."""
        base, ext = os.path.splitext(filename)
        counter = 1
        candidate = filename

        while os.path.exists(os.path.join("photos", candidate)):
            candidate = f"{base}_{counter}{ext}"
            counter += 1

        return candidate

    def _find_figure_id_for_photo(self, photo: Dict, source_figures: List[Dict]) -> Optional[int]:
        """Find the figure ID for a photo based on the merged data."""
        # This is a simplified approach - in a real implementation,
        # you'd need to match photos to figures more intelligently
        if 'figure_id' in photo:
            # Try to find the corresponding merged figure
            for source_fig in source_figures:
                if source_fig.get('id') == photo['figure_id']:
                    # Find the merged figure by name/series/manufacturer match
                    target_figures = self.analysis.target_db.get_all_figures()
                    for target_fig in target_figures:
                        if (target_fig['name'].lower().strip() == source_fig['name'].lower().strip() and
                            target_fig.get('series', '').lower().strip() == source_fig.get('series', '').lower().strip() and
                            target_fig.get('manufacturer', '').lower().strip() == source_fig.get('manufacturer', '').lower().strip()):
                            return target_fig['id']
        return None

    def _merge_photos_for_figure(self, figure_id: int, source_figure: Dict):
        """Merge photos from source figure to existing figure."""
        # This would add photos from the source figure to the target figure
        # Implementation depends on how photos are linked in the source data
        pass


class MergeCollectionsDialog(QDialog):
    """Dialog for merging collections from another source."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Collections")
        self.setModal(True)
        self.resize(800, 600)

        self.source_data = None
        self.analysis = None
        self.merge_worker = None

        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()

        # Source selection
        source_group = QGroupBox("Step 1: Select Source Collection")
        source_layout = QVBoxLayout()

        self.source_info = QLabel("No source selected")
        self.source_info.setStyleSheet("border: 1px solid #ccc; padding: 10px; border-radius: 5px;")
        source_layout.addWidget(self.source_info)

        select_layout = QHBoxLayout()
        self.select_backup_btn = QPushButton("Select OMAC Backup (.zip)")
        self.select_backup_btn.clicked.connect(self.select_backup_file)
        select_layout.addWidget(self.select_backup_btn)

        self.select_csv_btn = QPushButton("Select CSV File")
        self.select_csv_btn.clicked.connect(self.select_csv_file)
        select_layout.addWidget(self.select_csv_btn)

        source_layout.addLayout(select_layout)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # Analysis results
        analysis_group = QGroupBox("Step 2: Analysis Results")
        analysis_layout = QVBoxLayout()

        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(150)
        analysis_layout.addWidget(self.analysis_text)

        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Merge options
        options_group = QGroupBox("Step 3: Merge Options")
        options_layout = QVBoxLayout()

        # Figure conflict resolution
        conflict_layout = QHBoxLayout()
        conflict_layout.addWidget(QLabel("When figures conflict:"))

        self.conflict_group = QButtonGroup(self)
        self.skip_radio = QRadioButton("Skip (don't import)")
        self.skip_radio.setChecked(True)
        self.conflict_group.addButton(self.skip_radio)

        self.update_radio = QRadioButton("Update existing")
        self.conflict_group.addButton(self.update_radio)

        self.merge_radio = QRadioButton("Merge photos only")
        self.conflict_group.addButton(self.merge_radio)

        conflict_layout.addWidget(self.skip_radio)
        conflict_layout.addWidget(self.update_radio)
        conflict_layout.addWidget(self.merge_radio)
        conflict_layout.addStretch()

        options_layout.addLayout(conflict_layout)

        # Photo conflict resolution
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(QLabel("When photo filenames conflict:"))

        self.photo_rename_check = QCheckBox("Automatically rename incoming photos")
        self.photo_rename_check.setChecked(True)
        photo_layout.addWidget(self.photo_rename_check)
        photo_layout.addStretch()

        options_layout.addLayout(photo_layout)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress and control
        progress_group = QGroupBox("Step 4: Perform Merge")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        progress_layout.addWidget(self.progress_label)

        button_layout = QHBoxLayout()
        self.merge_btn = QPushButton("Start Merge")
        self.merge_btn.clicked.connect(self.start_merge)
        self.merge_btn.setEnabled(False)
        self.merge_btn.setStyleSheet("QPushButton { font-weight: bold; background-color: #4CAF50; color: white; }")
        button_layout.addWidget(self.merge_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        progress_layout.addLayout(button_layout)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        self.setLayout(layout)

    def select_backup_file(self):
        """Select an OMAC backup ZIP file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select OMAC Backup", "",
            "OMAC Backup Files (*.zip);;All Files (*)"
        )

        if file_path:
            self.load_backup_file(file_path)

    def select_csv_file(self):
        """Select a CSV file for import."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.load_csv_file(file_path)

    def load_backup_file(self, zip_path: str):
        """Load data from an OMAC backup ZIP file."""
        try:
            self.source_info.setText(f"Loading backup: {os.path.basename(zip_path)}")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract ZIP
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zipf.extractall(temp_dir)

                # Find CSV and TAR files
                csv_file = None
                tar_file = None
                for file in os.listdir(temp_dir):
                    if file.endswith('.csv'):
                        csv_file = os.path.join(temp_dir, file)
                    elif file.endswith('.tar.gz'):
                        tar_file = os.path.join(temp_dir, file)

                if not csv_file:
                    raise Exception("No CSV file found in backup")

                # Load figures from CSV
                figures = []
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        figures.append(row)

                # Load photos from TAR if available
                photos = []
                if tar_file:
                    # Extract photos to temp location
                    photo_temp_dir = os.path.join(temp_dir, 'photos')
                    os.makedirs(photo_temp_dir)

                    with tarfile.open(tar_file, "r:gz") as tar:
                        tar.extractall(photo_temp_dir, filter='data')

                    # Build photo list
                    for root, dirs, files in os.walk(photo_temp_dir):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                                photos.append({
                                    'file_path': os.path.join(root, file),
                                    'filename': file
                                })

                self.source_data = {
                    'figures': figures,
                    'photos': photos,
                    'source_type': 'backup',
                    'source_path': zip_path
                }

                self.source_info.setText(
                    f"✅ Loaded backup: {len(figures)} figures, {len(photos)} photos\n"
                    f"File: {os.path.basename(zip_path)}"
                )

                self.analyze_data()

        except Exception as e:
            self.source_info.setText(f"❌ Error loading backup: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load backup file:\n\n{str(e)}")

    def load_csv_file(self, csv_path: str):
        """Load data from a CSV file."""
        try:
            self.source_info.setText(f"Loading CSV: {os.path.basename(csv_path)}")

            figures = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    figures.append(row)

            self.source_data = {
                'figures': figures,
                'photos': [],  # CSV import doesn't include photos
                'source_type': 'csv',
                'source_path': csv_path
            }

            self.source_info.setText(
                f"✅ Loaded CSV: {len(figures)} figures\n"
                f"File: {os.path.basename(csv_path)}\n"
                f"Note: Photos cannot be imported from CSV files"
            )

            self.analyze_data()

        except Exception as e:
            self.source_info.setText(f"❌ Error loading CSV: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load CSV file:\n\n{str(e)}")

    def analyze_data(self):
        """Analyze the loaded data for conflicts."""
        if not self.source_data:
            return

        self.analysis = MergeAnalysis(self.source_data, DatabaseManager())
        results = self.analysis.analyze()

        analysis_text = f"""📊 Merge Analysis Results:

Source Data:
• {results['total_source_figures']} figures in source
• {results['total_source_photos']} photos in source

Merge Preview:
• {results['new_figures']} new figures will be added
• {results['figure_conflicts']} figure conflicts detected
• {results['photo_conflicts']} photo filename conflicts

Conflicts will be resolved according to your selected options."""

        self.analysis_text.setText(analysis_text)
        self.merge_btn.setEnabled(True)

    def start_merge(self):
        """Start the merge operation."""
        if not self.source_data or not self.analysis:
            return

        # Confirm merge
        reply = QMessageBox.question(
            self, "Confirm Merge",
            f"This will merge {len(self.analysis.new_figures)} new figures and "
            f"{len(self.analysis.conflicts)} conflicting figures into your collection.\n\n"
            f"Photo conflicts: {len(self.analysis.photo_conflicts)}\n\n"
            "Continue with merge?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Set conflict resolutions based on UI
        for conflict in self.analysis.conflicts:
            if self.update_radio.isChecked():
                conflict['resolution'] = 'update'
            elif self.merge_radio.isChecked():
                conflict['resolution'] = 'merge_photos'
            else:
                conflict['resolution'] = 'skip'

        # Prepare merge options
        options = {
            'photo_rename_conflicts': self.photo_rename_check.isChecked()
        }

        # Start merge worker
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.merge_btn.setEnabled(False)

        self.merge_worker = MergeWorker(self.source_data, self.analysis, options)
        self.merge_worker.progress.connect(self.update_progress)
        self.merge_worker.finished.connect(self.merge_finished)
        self.merge_worker.error.connect(self.merge_error)
        self.merge_worker.start()

    def update_progress(self, message: str, percentage: int):
        """Update progress display."""
        self.progress_label.setText(message)
        self.progress_bar.setValue(percentage)

    def merge_finished(self, results: Dict):
        """Handle merge completion."""
        self.progress_bar.setVisible(False)
        self.merge_btn.setEnabled(True)

        success_msg = f"""✅ Merge completed successfully!

Results:
• {results['added_figures']} new figures added
• {results['updated_figures']} figures updated
• {results['added_photos']} photos added
• {results['skipped_conflicts']} conflicts skipped

Your collection has been updated."""

        QMessageBox.information(self, "Merge Complete", success_msg)

        # Refresh parent window if available
        if hasattr(self.parent(), 'load_figures') and hasattr(self.parent(), 'update_status_bar'):
            self.parent().load_figures()
            self.parent().update_status_bar()

        # Reset dialog
        self.source_data = None
        self.analysis = None
        self.source_info.setText("No source selected")
        self.analysis_text.clear()
        self.merge_btn.setEnabled(False)

    def merge_error(self, error_msg: str):
        """Handle merge error."""
        self.progress_bar.setVisible(False)
        self.merge_btn.setEnabled(True)
        QMessageBox.critical(self, "Merge Error", f"Merge failed:\n\n{error_msg}")