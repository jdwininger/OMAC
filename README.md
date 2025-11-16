# OMAC (One Man Action Figure Collection)

A comprehensive macOS application for cataloging and managing action figure collections, built with SwiftUI and Core Data.

## Features

### Core Functionality
- **Complete CRUD Operations**: Add, view, edit, and delete action figures from your collection
- **Rich Data Model**: Store comprehensive information including:
  - Figure name, manufacturer, and series
  - Condition, packaging type, and physical details
  - Financial tracking (price paid, current value, profit/loss calculation)
  - Dates (purchase, release, addition to collection)
  - Notes and additional details

### Advanced Features
- **Smart Search & Filtering**: Search across multiple fields and filter by manufacturer or series
- **Flexible Sorting**: Sort by name, manufacturer, series, condition, price, value, or date
- **Collection Statistics**: Track total collection value, money invested, and item counts
- **Data Relationships**: Organized hierarchy of Manufacturers → Series → Action Figures

### User Interface
- **Native macOS Design**: Built with SwiftUI for a modern, native feel
- **Split View Layout**: Efficient browsing with master-detail interface
- **Form-Based Input**: Intuitive forms for data entry and editing
- **Visual Data Display**: Clean presentation of figure information and statistics

### Data Management
- **Core Data Integration**: Reliable local database storage
- **CloudKit Ready**: Infrastructure prepared for future cloud sync
- **Data Validation**: Form validation and error handling
- **Sample Data**: Preview data for development and testing

## Technical Stack

- **Language**: Swift 5.0
- **UI Framework**: SwiftUI
- **Database**: Core Data with CloudKit support
- **Architecture**: MVVM pattern
- **Platform**: macOS 14.0+

## Project Structure

```
OMAC/
├── OMACApp.swift                      # Main app entry point
├── Models/                            # Data model folder
├── Views/                            # SwiftUI views
│   ├── ContentView.swift            # Main collection view
│   ├── AddFigureView.swift         # Add new figure form
│   ├── FigureDetailView.swift      # View/edit figure details
│   └── SearchView.swift            # Search and filter interface
├── Managers/                         # Data management
│   ├── PersistenceController.swift # Core Data setup
│   └── DataManager.swift           # CRUD operations & business logic
├── OMAC.xcdatamodeld                # Core Data model
└── Assets.xcassets/                 # App icons and resources
```

## Getting Started

### Prerequisites
- Xcode 15.0 or later
- macOS 14.0 or later

### Installation
1. Clone or download the project
2. Open `OMAC.xcodeproj` in Xcode
3. Build and run the project (⌘+R)

### First Use
1. Launch the app
2. Click "Add Figure" to create your first entry
3. Fill out the form with figure details
4. Save to add to your collection
5. Use search and filter features to organize your collection

## Usage

### Adding Figures
1. Click the "Add Figure" button
2. Fill in required information (Figure Name is mandatory)
3. Optionally add manufacturer, series, condition, and financial data
4. Add notes and additional details as needed
5. Save the figure to your collection

### Managing Data
- **Edit**: Click any figure to view details, then click "Edit"
- **Delete**: In detail view, click "Delete" and confirm
- **Search**: Use the search bar to find specific figures
- **Filter**: Use dropdown menus to filter by manufacturer or series
- **Sort**: Choose sorting criteria and direction in the search view

### Collection Statistics
View real-time statistics including:
- Total number of figures
- Total money invested
- Current collection value
- Profit/loss calculations per figure

## Data Model

### ActionFigure Entity
- Basic info: name, manufacturer, series
- Physical details: height, packaging, condition
- Financial: price paid, current value
- Dates: purchase, release, addition dates
- Additional: SKU, UPC, notes, photo data

### Manufacturer Entity
- Company name and unique identifier
- One-to-many relationship with figures and series

### Series Entity
- Series name, year, and manufacturer
- One-to-many relationship with figures

## Future Enhancements

### Planned Features
- Photo management and gallery view
- Import/export functionality (CSV, JSON)
- Advanced reporting and analytics
- Wishlist and want list management
- Barcode scanning for quick entry
- Market value integration
- Collection sharing and backup via CloudKit

### Potential Improvements
- iOS companion app
- Collection insurance valuation reports
- Integration with online marketplaces
- Social features and community sharing
- Advanced search with regex support

## Development

### Architecture Notes
- Uses MVVM pattern with SwiftUI's @ObservableObject
- Core Data with CloudKit container for future sync
- Separation of concerns with dedicated DataManager
- Preview support throughout for development ease

### Building
```bash
# Open in Xcode
open OMAC.xcodeproj

# Or build from command line
xcodebuild -project OMAC.xcodeproj -scheme OMAC build
```

## License

This project is created as a demonstration application. Feel free to use and modify as needed.

## Support

For questions or issues, please refer to the code documentation or create an issue in the project repository.