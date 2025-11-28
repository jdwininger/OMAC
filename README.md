# OMAC - One 'Mazing Action Catalog

A comprehensive desktop application for managing action figure collections with photo support, built with Python and PyQt6.

## Features

### 🎯 Core Functionality
- **Complete Collection Management**: Add, edit, delete, and organize your action figures
- **Wishlist Management**: Track desired figures and easily move them to your collection when acquired
- **Multi-Photo Support**: Upload and manage multiple photos per figure
- **Advanced Search**: Find figures by name, series, or manufacturer
- **Column Sorting**: Click any column header to sort ascending/descending (Name, Series, Wave, Manufacturer, Year, Condition, Photos)
- **Customizable Table View**: Show/hide columns and rearrange column order
- **Data Backup & Restore**: Create complete backups and restore from them
- **Merge Collections**: Combine collections from other OMAC installations or CSV files
- **Unique Menu Layout**: Traditional menu bar at the top with File, View, and Help menus
- **SQLite Database**: Reliable local database storage
- **Cross-Platform**: Works on Windows, macOS, and Linux with platform-appropriate data storage

### Data Tracking
- Figure name, series, wave, and manufacturer
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

### 🎯 Wishlist Management
- Track desired action figures you want to acquire
- Add wishlist items with name, series, wave, manufacturer, and target price
- Set priority levels (Low, Medium, High) for wishlist items
- Move items from wishlist to main collection when acquired
- Dedicated wishlist dialog with full CRUD operations
- Seamless integration with existing add figure workflow

### 🔍 Collection Overview
- Table view with sortable columns
- Real-time search and filtering
- Collection statistics in status bar
- Detailed figure information panel

## Requirements

- **Python 3.8 or higher**
- **PyQt6** - GUI framework
- **Pillow** - Image processing for photos
- **SQLite** - Database (included with Python)
- **py2app** - For building standalone macOS applications (optional, only needed for macOS builds)
- **PyInstaller** - For building standalone Linux AppImages (automatically downloaded during Linux builds)

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

4. **Run the application**
   ```bash
   python main.py
   ```

**First Run Notes:**
- The application will create its data directory automatically based on your platform
- Database and photo directories are created on first use
- Manufacturer and location preferences are saved automatically

## Building a Standalone macOS App

To create a standalone macOS application bundle that can be distributed to other users:

### Prerequisites
- macOS system (scripts include OS checks and will display an error on Linux/other systems)
- Python virtual environment with dependencies installed
- py2app (included in requirements.txt)

### Option 1: Build App Bundle + DMG (Recommended)
```bash
./build_and_package_macos.sh
```
This creates both the application bundle and a compressed DMG file for distribution.

### Option 2: Build App Bundle Only
```bash
./build_macos_app.sh
```

### Distribution Files Created
- **Application bundle**: `dist/OMAC.app` (~274MB) - The runnable application
- **Distributable DMG**: `OMAC.dmg` (~113MB) - Compressed disk image for sharing

### Usage
- **Test locally**: Double-click `dist/OMAC.app`
- **Distribute**: Share the `OMAC.dmg` file with other macOS users

**Notes:**
- Scripts include OS detection and will exit with an error message if run on Linux
- The first run of the built app may take longer as it creates the database
- The app bundle includes all necessary dependencies and is self-contained
- Built apps are signed and ready for distribution
- Compatible with macOS 10.15+ (argv_emulation disabled for modern macOS compatibility)
- No Python installation required on target systems

## Building a Standalone Linux AppImage

To create a standalone Linux AppImage that can be distributed to other users:

### Prerequisites
- Linux system (scripts include OS checks and will display an error on macOS/other systems)
- Python virtual environment with dependencies installed
- Internet connection (for automatic PyInstaller and appimagetool download)

### Build AppImage
```bash
./build_linux_appimage.sh
```
This creates a standalone AppImage file for distribution. The script will automatically download and install PyInstaller and appimagetool if they're not already available on your system.

### Distribution Files Created
- **AppImage**: `OMAC.AppImage` (~150MB) - Portable Linux application
- **AppDir**: `AppDir/` - Application directory structure (if appimagetool not available)

### Usage
- **Make executable**: `chmod +x OMAC.AppImage`
- **Test locally**: `./OMAC.AppImage`
- **Distribute**: Share the `OMAC.AppImage` file with other Linux users

**Notes:**
- Scripts include OS detection and will exit with an error message if run on macOS
- The script automatically downloads PyInstaller and appimagetool if not found (requires internet connection)
- The first run may take longer as it creates the database in `~/Documents/OMAC/`
- The AppImage includes all necessary dependencies and is self-contained
- Compatible with most Linux distributions (Ubuntu, Fedora, etc.)
- No Python installation required on target systems

## Usage

Run the application:
```bash
python main.py
```

**Data Storage Locations:**
- **macOS**: `~/Library/Application Support/OMAC/`
- **Linux**: `~/Documents/OMAC/`
- **Windows/Other**: Current application directory

The application automatically detects your operating system and stores data in the appropriate location.

## Project Structure

```
OMAC/
├── main.py                    # Main application window and GUI
├── database.py                # SQLite database manager
├── merge_collections.py       # Collection merging functionality
├── wishlist_dialog.py         # Wishlist management dialog
├── quickstart.py              # Quick start utility
├── manufacturers.txt          # Saved manufacturer list (created automatically)
├── locations.txt              # Saved location list (created automatically)
├── requirements.txt           # Python dependencies
├── setup.py                   # Py2app configuration for macOS builds
├── build_macos_app.sh         # Script to build macOS app bundle
├── build_and_package_macos.sh # Script to build app bundle + DMG
├── build_linux_appimage.sh    # Script to build Linux AppImage
├── README.md                  # This file
├── action_figures.db          # SQLite database (created on first run)
├── photos/                    # Photo storage directory (created automatically)
├── backups/                   # Backup storage directory (created automatically)
├── build/                     # Build artifacts (created during macOS builds)
├── tools/                     # Build tools directory (created automatically)
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
- **Column Management**: Right-click table headers to show/hide columns and reset layout
- **Column Reordering**: Drag column headers to rearrange column order
- **Theme**: Switch between light and dark themes via View menu

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

### Merge Collections

- **Combine Collections**: File → Merge Collections to import from another OMAC backup or CSV file
- **Intelligent Conflict Resolution**: Choose how to handle duplicate figures (skip, update, or merge photos)
- **Photo Conflict Handling**: Automatically rename incoming photos with conflicting filenames
- **Analysis Preview**: See exactly what will be merged before proceeding
- **Progress Tracking**: Monitor merge progress with detailed status updates
- **Safe Operation**: No data loss - conflicts are handled according to your preferences

## Database Schema

### Action Figures Table
- ID, Name, Series, Wave, Manufacturer
- Year, Scale, Condition
- Purchase Price, Location, Notes
- Created/Updated timestamps

### Wishlist Table
- ID, Name, Series, Wave, Manufacturer
- Year, Scale, Target Price, Priority
- Notes, Created/Updated timestamps

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
- **wishlist_dialog.py**: Dedicated wishlist management interface
- **Platform-Aware Storage**: Automatic data directory detection (macOS Application Support, Linux Documents, etc.)
- **Object-Oriented Design**: Clean separation of UI and data layers
- **Signal-Slot Pattern**: Qt's event handling for responsive UI

### Key Components

1. **OMACMainWindow**: Main application window with platform-aware data storage
2. **ActionFigureDialog**: Add/edit dialog with tabbed interface and photo management
3. **WishlistDialog**: Dedicated dialog for wishlist management and collection integration
4. **PhotoWidget**: Custom widget for photo display and interaction
5. **DatabaseManager**: Complete SQLite database operations
6. **MergeCollectionsDialog**: Collection merging and import functionality

## Future Enhancements

- **Advanced Photo Viewer**: Full-screen image viewer with zoom and slideshow
- **Statistics Dashboard**: Advanced collection analytics and reporting
- **Barcode Scanning**: UPC/EAN barcode support for quick entry
- **Online Integration**: Price tracking and market value updates
- **Custom Fields**: User-defined fields and categories
- **Export Formats**: Additional export formats beyond CSV
- **Cloud Backup**: Optional cloud storage integration
- **Mobile Companion**: Web interface for mobile access
- **Windows Portable App**: Standalone executable for Windows distribution

## Troubleshooting

### Common Issues

1. **Photo not displaying**: Check if image file still exists in photos directory
2. **Database errors**: Ensure write permissions in application directory
3. **Import errors**: Verify all dependencies are installed in virtual environment

### Data Location

One 'Mazing Action Catalog automatically stores your data in platform-appropriate locations:

- **macOS**: `~/Library/Application Support/OMAC/`
- **Linux**: `~/Documents/OMAC/`
- **Windows/Other**: Current application directory

**Data includes:**
- `action_figures.db` - SQLite database
- `photos/` - Photo storage directory
- `backups/` - Backup files directory
- `manufacturers.txt` - Saved manufacturer preferences
- `locations.txt` - Saved location preferences

**Backup recommended**: Copy the entire data directory to preserve all your collection data.

## License

This project is created for personal use and collection management.

---

**Start building your action figure database today!** 🎭