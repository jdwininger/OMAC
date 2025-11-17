#!/bin/bash
"""
Build script for creating a standalone macOS application bundle for OMAC.
"""

set -e  # Exit on any error

echo "=== OMAC macOS App Builder ==="
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

echo "Building macOS application bundle..."
python setup.py py2app

echo
echo "=== Build Complete ==="
echo "Application bundle created in: dist/OMAC.app"
echo
echo "To run the app:"
echo "open dist/OMAC.app"
echo
echo "To create a distributable .dmg file, you can use:"
echo "hdiutil create -volname 'OMAC' -srcfolder dist/OMAC.app -ov -format UDZO OMAC.dmg"
echo
echo "Note: The first run may take longer as it creates the database."
echo "Note: Compatible with macOS 10.15+ (argv_emulation disabled for modern macOS compatibility)"