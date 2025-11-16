# OMAC - One 'Mazing ActionFigure Catalog

## Project Overview
This is a comprehensive Python desktop application built with PyQt6 for managing action figure collections. Features SQLite database backend, multi-photo support, and cross-platform compatibility (Windows, macOS, Linux).

## Technology Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Database**: SQLite with custom schema
- **Image Processing**: Pillow (PIL)
- **Architecture**: Object-oriented design with MVC pattern
- **Virtual Environment**: Python venv

## Project Setup Completed ✅
- [x] Python virtual environment configured
- [x] PyQt6 and Pillow dependencies installed
- [x] SQLite database schema designed and implemented
- [x] Main application window with collection browser
- [x] Add/Edit dialog with tabbed interface
- [x] Photo management system with upload/display
- [x] Search and filtering capabilities
- [x] Cross-platform compatibility ensured
- [x] Comprehensive documentation completed

## Key Features Implemented

### Database Management
- SQLite database with action_figures and photos tables
- Comprehensive CRUD operations
- Foreign key relationships and data integrity
- Database statistics and performance optimization

### User Interface
- Professional main window with splitter layout
- Table-based collection browser with search
- Tabbed add/edit dialog for figure entry
- Photo gallery with thumbnail display
- Status bar with real-time collection statistics
- Responsive design with proper widget sizing

### Photo Management
- Multiple photo upload per figure
- Automatic photo organization and storage
- Primary photo designation
- Support for common image formats (JPG, PNG, GIF, BMP)
- Custom photo widget with click handling

### Data Features
- Complete figure information tracking
- Purchase price and current value management
- Condition tracking with predefined options
- Notes and location information
- Search across multiple fields
- Collection statistics

## Development Guidelines
- Use PyQt6 widgets and layouts for UI components
- Follow Qt's signal-slot pattern for event handling
- Maintain MVC architecture with separated concerns
- Use DatabaseManager class for all database operations
- Implement proper error handling and user feedback
- Test across different platforms for compatibility
- Use virtual environment for dependency isolation

## Running the Application
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Run application
python main.py
```

## File Structure
```
OMAC/
├── main.py              # Main GUI application
├── database.py          # SQLite database manager
├── requirements.txt     # Python dependencies
├── action_figures.db    # SQLite database (created on first run)
├── photos/              # Photo storage (auto-created)
├── README.md           # Documentation
└── .github/
    └── copilot-instructions.md
```

## Database Schema

### action_figures table
- id (PRIMARY KEY)
- name, series, manufacturer
- year, scale, condition
- purchase_price, current_value
- purchase_date, location, notes
- created_at, updated_at

### photos table
- id (PRIMARY KEY)
- figure_id (FOREIGN KEY)
- file_path, caption
- is_primary (BOOLEAN)
- upload_date

## Extension Points
- Add export/import functionality
- Implement advanced photo viewer
- Add barcode scanning support
- Create custom reporting features
- Integrate online price tracking
- Add backup/restore capabilities