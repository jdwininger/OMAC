# OMAC - One 'Mazing ActionFigure Catalog

A comprehensive desktop application for managing action figure collections with photo support, built with Python and PyQt6.

## Features

### 🎯 Core Functionality
- **Complete Collection Management**: Add, edit, delete, and organize your action figures
- **Multi-Photo Support**: Upload and manage multiple photos per figure
- **Advanced Search**: Find figures by name, series, or manufacturer
- **Data Backup & Restore**: Create complete backups and restore from them
- **Unique Menu Layout**: Traditional menu bar at the top with File, View, and Help menus
- **Theme Support**: Switch between light and dark themes
- **SQLite Database**: Reliable local database storage
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Data Tracking
- Figure name, series, and manufacturer
- Year of release and scale information
- Condition tracking (Mint in Package, Loose, etc.)
- Purchase price
- Storage location
- Detailed notes for each figure

### 📸 Photo Management
- Multiple photos per figure
- Primary photo selection
- Photo gallery view
- Automatic photo organization
- Support for JPG, PNG, GIF, and BMP formats

### 🔍 Collection Overview
- Table view with sortable columns
- Real-time search and filtering
- Collection statistics in status bar
- Detailed figure information panel

## Requirements

- Python 3.8 or higher
- PyQt6
- Pillow (for image processing)
- SQLite (included with Python)

## Installation

1. **Clone or download the project**
   ```bash
   cd /path/to/OMAC
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Building a Standalone macOS App

To create a standalone macOS application bundle that can be distributed to other users:

1. **Ensure you have the build dependencies installed**
   ```bash
   pip install py2app
   ```

2. **Run the build script**
   ```bash
   ./build_macos_app.sh
   ```

3. **Find the application bundle**
   - The app will be created in `dist/OMAC.app` (274MB)
   - Double-click to run it like any other macOS application

4. **Optional: Create a distributable .dmg file**
   ```bash
   hdiutil create -volname 'OMAC' -srcfolder dist/OMAC.app -ov -format UDZO OMAC.dmg
   ```
   - Creates `OMAC.dmg` (113MB compressed)

**Notes:**
- The first run of the built app may take longer as it creates the database
- The app bundle includes all necessary dependencies and is self-contained
- Built apps are signed and ready for distribution
- Compatible with macOS 10.15+ (argv_emulation disabled for modern macOS compatibility)
- No Python installation required on target systems

**Distribution Files:**
- `dist/OMAC.app` - macOS application bundle
- `OMAC.dmg` - Compressed disk image for easy distribution

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
OMAC/
├── main.py              # Main application window and GUI
├── database.py          # SQLite database manager
├── requirements.txt     # Python dependencies
├── action_figures.db    # SQLite database (created on first run)
├── photos/              # Photo storage directory (created automatically)
├── README.md           # This file
└── .github/
    └── copilot-instructions.md
```

## User Guide

### Adding Action Figures

1. **Click "Add Figure"** in the toolbar or use Ctrl+N
2. **Fill in the Details tab**:
   - Name (required)
   - Series/Line, Manufacturer
   - Year, Scale, Condition
   - Purchase price
   - Storage location
   - Additional notes
3. **Add Photos** in the Photos tab:
   - Click "Add Photos" to select multiple images
   - Photos are automatically copied to the photos directory
   - First photo becomes the primary image
4. **Click Save** to add the figure to your collection

### Managing Your Collection

- **Search**: Use the search box in the left sidebar to find figures
- **Add**: Click the "Add Figure" button in the left sidebar
- **Edit**: Select a figure and click "Edit Figure" in the left sidebar, or double-click a figure
- **Delete**: Select a figure and click "Delete Figure" in the sidebar
- **View Details**: Click any figure to see detailed information and photos
- **Backup**: Create complete backups via File → Backup Database & Photos menu
- **Restore**: Restore from backup via File → Restore Database & Photos menu
- **Theme**: Switch between light and dark themes via View → Theme menu

### Photo Features

- **Multiple Photos**: Add unlimited photos per figure
- **Primary Photo**: First uploaded photo becomes primary (shown in collection)
- **Photo Viewer**: Click photos to view (expandable in future versions)
- **Automatic Storage**: Photos are copied to local photos directory

### Backup & Restore

- **Complete Backup**: File → Backup Database & Photos creates a dated zip file
- **Backup Contents**: Includes CSV export of database and compressed photos archive
- **Automatic Organization**: Backups are stored in the `backups/` directory
- **Restore from GUI**: File → Restore Database & Photos to restore from backup
- **Restore Process**: Automatically extracts and imports backup data
- **Safety Option**: Choose to backup current data before restoring
- **README Included**: Each backup contains restoration instructions

## Database Schema

### Action Figures Table
- ID, Name, Series, Manufacturer
- Year, Scale, Condition
- Purchase Price, Location, Notes
- Created/Updated timestamps

### Photos Table
- ID, Figure ID (foreign key)
- File Path, Caption
- Primary Photo flag
- Upload Date

## Development

### Running in Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Run the application
python main.py
```

### Architecture

- **main.py**: PyQt6 GUI application with main window and dialogs
- **database.py**: SQLite database operations and management
- **Object-Oriented Design**: Clean separation of UI and data layers
- **Signal-Slot Pattern**: Qt's event handling for responsive UI

### Key Components

1. **OMACMainWindow**: Main application window
2. **ActionFigureDialog**: Add/edit dialog with tabbed interface
3. **PhotoWidget**: Custom widget for photo display and interaction
4. **DatabaseManager**: Complete SQLite database operations

## Future Enhancements

- **Export/Import**: CSV export and import functionality
- **Advanced Photo Viewer**: Full-screen image viewer with zoom
- **Backup/Restore**: Database backup and restore features
- **Statistics**: Advanced collection analytics and reporting
- **Barcode Scanning**: UPC/EAN barcode support for quick entry
- **Online Integration**: Price tracking and market value updates
- **Custom Fields**: User-defined fields and categories

## Troubleshooting

### Common Issues

1. **Photo not displaying**: Check if image file still exists in photos directory
2. **Database errors**: Ensure write permissions in application directory
3. **Import errors**: Verify all dependencies are installed in virtual environment

### Data Location

- **Database**: `action_figures.db` in application directory
- **Photos**: `photos/` subdirectory
- **Backup recommended**: Copy both database and photos directory

## License

This project is created for personal use and collection management.

---

**Start building your action figure database today!** 🎭