# OMAC - Swift Version

One 'Mazing Action Catalog - Native macOS Application

## Overview

This is a Swift/SwiftUI port of the One 'Mazing Action Catalog action figure collection manager, originally built with Python and PyQt6. This version leverages native macOS technologies for better performance and integration.

## Features

- **Native macOS UI**: Built with SwiftUI for a modern, responsive interface
- **Core Data**: Robust data persistence with automatic migrations
- **Photo Management**: Native photo handling with upload, gallery view, and primary photo selection
- **Wishlist Functionality**: Track desired figures with priority levels and target prices
- **Import/Export**: CSV import/export for data migration and backup
- **Search & Sort**: Fast searching and multiple sorting options (Name, Series, Wave, Manufacturer, Year, Condition)
- **Collection Statistics**: Real-time collection analytics including wishlist counts
- **Modern Swift**: Leveraging Swift 5.9+ features and SwiftUI best practices

## Architecture

### Models
- `ActionFigure`: Core data model for action figures
- `Photo`: Photo attachment model with file management

### Views
- `ContentView`: Main application layout with sidebar/detail and toolbar
- `CollectionSidebar`: Collection list with search, sorting, and statistics
- `FigureDetailView`: Detailed figure information with photo management
- `AddEditFigureView`: Form for adding/editing figures
- `PhotoGalleryView`: Photo management with grid layout and operations
- `PhotoViewerView`: Full-screen photo viewer with editing capabilities
- `WishlistView`: Wishlist management interface
- `AddEditWishlistView`: Form for wishlist items

### View Models
- `CollectionViewModel`: Manages collection data, photos, and wishlist operations

### Services
- `PersistenceController`: Core Data setup and management
- `PhotoManager`: Photo file operations and management
- `DataImportExport`: CSV import/export functionality

## Requirements

- **macOS 13.0+**
- **Xcode 15.0+**
- **Swift 5.9+**

## Building

1. Open `OMAC.xcodeproj` in Xcode
2. Select your target device/simulator
3. Build and run (⌘R)

## Data Migration

The Swift version uses Core Data instead of SQLite. To migrate data from the Python version:

1. In the Python version, use the export feature to create a CSV file
2. In the Swift version, click "Import/Export" in the toolbar
3. Select "Import from CSV" and choose your exported file
4. Your collection data will be imported automatically

A sample CSV file (`sample_collection.csv`) is included to demonstrate the expected format.

## Development Status

This Swift port includes comprehensive functionality:

- ✅ **Basic SwiftUI project structure** with proper architecture
- ✅ **Core Data models** for ActionFigure, Photo, and WishlistItem
- ✅ **Collection sidebar** with search, sorting, and statistics
- ✅ **Figure detail view** with comprehensive information display
- ✅ **Add/edit functionality** for figures and wishlist items
- ✅ **Photo management system** with gallery, upload, and primary photo selection
- ✅ **Wishlist functionality** with priority levels and collection integration
- ✅ **Import/export functionality** with CSV support and backup/restore
- ✅ **Modern Swift patterns** with MVVM architecture and SwiftUI best practices
- 🔄 **Advanced photo features** (planned for future update)

## Contributing

This Swift port is developed on the `swift-macos` branch. See the main README for contribution guidelines.