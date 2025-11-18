#!/bin/bash
# Cleanup script for OMAC build artifacts.
# This script removes all directories and files created during the build process
# for both Linux AppImage and macOS app builds.

set -e  # Exit on any error

echo "=== OMAC Build Cleanup ==="
echo

# Function to safely remove directory if it exists
safe_remove_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory not found (skipping): $dir"
    fi
}

# Function to safely remove file pattern if files exist
safe_remove_files() {
    local pattern="$1"
    local description="$2"
    if compgen -G "$pattern" > /dev/null; then
        echo "Removing $description: $pattern"
        rm -f $pattern
    else
        echo "$description not found (skipping): $pattern"
    fi
}

echo "Cleaning up build artifacts..."
echo

# PyInstaller/py2app build directories (common to both Linux and macOS builds)
safe_remove_dir "build"
safe_remove_dir "dist"

# Linux AppImage specific directories
safe_remove_dir "AppDir"
safe_remove_dir "tools"
safe_remove_dir "squashfs-root"

# Python package build artifacts
safe_remove_dir "*.egg-info"

# PyInstaller spec files
safe_remove_files "*.spec" "PyInstaller spec files"

# AppImage files
safe_remove_files "*.AppImage" "AppImage files"

# macOS DMG files
safe_remove_files "*.dmg" "DMG files"

# Python cache directories (optional - uncomment if you want to clean these too)
# safe_remove_dir "__pycache__"
# safe_remove_dir ".pytest_cache"

echo
echo "=== Cleanup Complete ==="
echo
echo "Removed build artifacts:"
echo "  - build/          (PyInstaller/py2app build directory)"
echo "  - dist/           (Distribution directory)"
echo "  - AppDir/         (AppImage structure)"
echo "  - tools/          (Downloaded build tools)"
echo "  - squashfs-root/  (Temporary extraction directory)"
echo "  - *.egg-info/     (Python package info)"
echo "  - *.spec          (PyInstaller spec files)"
echo "  - *.AppImage      (Linux AppImage files)"
echo "  - *.dmg           (macOS DMG files)"
echo
echo "Note: This script preserves your source code, virtual environment (.venv/),"
echo "      and user data (backups/, photos/, etc.). Only build artifacts are removed."
echo
echo "To rebuild after cleanup:"
echo "  - Linux AppImage: ./build_linux_appimage.sh"
echo "  - macOS App: ./build_macos_app.sh"
echo "  - macOS App + DMG: ./build_and_package_macos.sh"