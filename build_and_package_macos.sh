#!/bin/bash
"""
Build script for creating a standalone macOS application bundle and DMG for OMAC.
This script builds the app and packages it into a distributable DMG file.
"""

set -e  # Exit on any error

echo "=== OMAC macOS App Builder & Packager ==="
echo

# Check if we're on Linux
if [[ "$(uname -s)" == "Linux" ]]; then
    echo "Error: This script is designed for macOS and cannot be run on Linux."
    exit 1
fi

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This build script is designed for macOS only."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run:"
    echo "python3 -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build dist *.egg-info
rm -f OMAC.dmg  # Clean up any existing DMG

echo "Building macOS application bundle..."
python setup.py py2app

echo
echo "=== Build Complete ==="
echo "Application bundle created in: dist/OMAC.app"
echo

# Check if build was successful
if [ ! -d "dist/OMAC.app" ]; then
    echo "Error: Application bundle was not created successfully."
    exit 1
fi

echo "Creating distributable DMG file..."
echo "This may take a moment..."

# Create DMG with compression
hdiutil create -volname 'OMAC' -srcfolder dist/OMAC.app -ov -format UDZO OMAC.dmg

echo
echo "=== Packaging Complete ==="
echo "DMG file created: OMAC.dmg"
echo

# Get file size for info
if command -v du >/dev/null 2>&1; then
    dmg_size=$(du -h OMAC.dmg | cut -f1)
    echo "DMG file size: $dmg_size"
fi

echo
echo "Distribution files:"
echo "  - Application bundle: dist/OMAC.app"
echo "  - Distributable DMG: OMAC.dmg"
echo
echo "To test the application:"
echo "open dist/OMAC.app"
echo
echo "To distribute:"
echo "Share the OMAC.dmg file with other macOS users."
echo
echo "Notes:"
echo "- Compatible with macOS 10.15+"
echo "- First run may take longer as it creates the database"
echo "- The DMG is compressed for smaller file size and faster downloads"