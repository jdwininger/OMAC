#!/bin/bash
# Build script for creating a standalone Linux AppImage for OMAC.
# This script builds the app and packages it into a distributable AppImage file.

set -e  # Exit on any error

echo "=== OMAC Linux AppImage Builder ==="
echo

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Error: This script is designed for Linux and cannot be run on macOS."
    exit 1
fi

# Check if we're on Linux
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "Error: This script is designed for Linux only."
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

# Verify PyInstaller is available (should be installed from requirements.txt)
if ! python -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller not found after pip install. Installing directly..."
    pip install pyinstaller
fi

# Double-check PyInstaller command is available
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller command not found. Please check your Python environment."
    exit 1
fi

echo "Cleaning previous builds..."
rm -rf build dist *.spec *.egg-info
rm -f OMAC.AppImage  # Clean up any existing AppImage

echo "Building Linux executable with PyInstaller..."
pyinstaller --onefile --windowed --name OMAC \
    --add-data "main.py:." \
    --add-data "database.py:." \
    --add-data "wishlist_dialog.py:." \
    --add-data "merge_collections.py:." \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PIL \
    --hidden-import sqlite3 \
    main.py

echo "Creating AppImage structure..."
# Create AppDir structure
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/lib
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy the executable
cp dist/OMAC AppDir/usr/bin/

# Copy required libraries (this is a simplified approach)
# In a production setup, you'd want to use linuxdeploy or similar
cp .venv/lib/python*/site-packages/PyQt6/Qt6/lib/*.so* AppDir/usr/lib/ 2>/dev/null || true
cp .venv/lib/python*/site-packages/PIL/*.so* AppDir/usr/lib/ 2>/dev/null || true

# Create desktop file
cat > AppDir/usr/share/applications/omac.desktop << EOF
[Desktop Entry]
Name=OMAC
Exec=OMAC
Icon=omac
Type=Application
Categories=Utility;
EOF

# Create a simple icon
python3 -c "
from PIL import Image, ImageDraw
import os

# Create a simple 256x256 icon
img = Image.new('RGB', (256, 256), color='blue')
draw = ImageDraw.Draw(img)

# Draw a simple 'O' shape
draw.ellipse([50, 50, 206, 206], fill='white', outline='black', width=5)
draw.ellipse([80, 80, 176, 176], fill='blue')

# Save as PNG
img.save('AppDir/omac.png')
print('Created omac.png icon')
"

# Copy desktop file to AppDir root (required by appimagetool)
cp AppDir/usr/share/applications/omac.desktop AppDir/

echo "Checking for appimagetool..."

# Check for appimagetool in multiple locations
APPIMAGETOOL_PATH=""
TOOLS_DIR="./tools"

# Create tools directory if it doesn't exist
mkdir -p "$TOOLS_DIR"

# Check for appimagetool in ~/Applications first, then tools directory, then system PATH
if [ -f "$HOME/Applications/appimagetool" ]; then
    APPIMAGETOOL_PATH="$HOME/Applications/appimagetool"
elif [ -f "$TOOLS_DIR/appimagetool" ]; then
    APPIMAGETOOL_PATH="$TOOLS_DIR/appimagetool"
elif command -v appimagetool &> /dev/null; then
    APPIMAGETOOL_PATH="appimagetool"
fi

# If not found, download it automatically
if [ -z "$APPIMAGETOOL_PATH" ]; then
    echo "appimagetool not found locally. Downloading automatically..."
    
    # Try to download appimagetool
    APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    
    if command -v curl &> /dev/null; then
        echo "Downloading appimagetool using curl..."
        if curl -L -o "$TOOLS_DIR/appimagetool.AppImage" "$APPIMAGETOOL_URL"; then
            echo "Download successful."
        else
            echo "Download failed. Please check your internet connection or download appimagetool manually."
            echo "Visit: https://github.com/AppImage/AppImageKit/releases"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        echo "Downloading appimagetool using wget..."
        if wget -O "$TOOLS_DIR/appimagetool.AppImage" "$APPIMAGETOOL_URL"; then
            echo "Download successful."
        else
            echo "Download failed. Please check your internet connection or download appimagetool manually."
            echo "Visit: https://github.com/AppImage/AppImageKit/releases"
            exit 1
        fi
    else
        echo "Neither curl nor wget found. Please install one of them or download appimagetool manually."
        echo "Visit: https://github.com/AppImage/AppImageKit/releases"
        exit 1
    fi
    
    # Make it executable and set up
    chmod +x "$TOOLS_DIR/appimagetool.AppImage"
    
    # Extract or use the AppImage directly
    if [ -x "$TOOLS_DIR/appimagetool.AppImage" ]; then
        # Try to extract the AppImage for better compatibility
        if "$TOOLS_DIR/appimagetool.AppImage" --appimage-extract &> /dev/null; then
            # If extraction works, use the extracted binary
            mv squashfs-root/usr/bin/appimagetool "$TOOLS_DIR/appimagetool"
            rm -rf squashfs-root
            chmod +x "$TOOLS_DIR/appimagetool"
            APPIMAGETOOL_PATH="$TOOLS_DIR/appimagetool"
        else
            # Fall back to using the AppImage directly
            ln -sf appimagetool.AppImage "$TOOLS_DIR/appimagetool"
            APPIMAGETOOL_PATH="$TOOLS_DIR/appimagetool"
        fi
    else
        echo "Failed to make appimagetool executable."
        exit 1
    fi
fi

echo "Using appimagetool: $APPIMAGETOOL_PATH"
echo "Creating AppImage..."
"$APPIMAGETOOL_PATH" AppDir OMAC.AppImage

echo
echo "=== Build Complete ==="
echo "AppImage created: OMAC.AppImage"
ls -lh OMAC.AppImage
echo
echo "Notes:"
echo "- The first run may take longer as it creates the database in ~/Documents/OMAC/"
echo "- Make sure the AppImage has execute permissions: chmod +x OMAC.AppImage"
echo "- Compatible with most Linux distributions"