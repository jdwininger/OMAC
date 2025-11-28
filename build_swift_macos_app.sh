#!/bin/bash
"""
Build script for creating a macOS application bundle for the Swift version of OMAC.
"""

set -e  # Exit on any error

echo "=== One 'Mazing Action Catalog Swift macOS App Bundle Builder ==="
echo

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This build script is designed for macOS only."
    exit 1
fi

# Navigate to the Swift project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWIFT_DIR="$SCRIPT_DIR/OMAC-Swift"

if [ ! -d "$SWIFT_DIR" ]; then
    echo "Error: OMAC-Swift directory not found at $SWIFT_DIR"
    exit 1
fi

cd "$SWIFT_DIR"

echo "Building Swift application in release mode..."
swift build --configuration release

echo "Creating app bundle structure..."
APP_NAME="OMAC"
DISPLAY_NAME="OMAC"
APP_BUNDLE="$SCRIPT_DIR/${DISPLAY_NAME}.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean previous bundle
rm -rf "$APP_BUNDLE"

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

echo "Copying executable..."
EXECUTABLE_PATH=".build/release/$APP_NAME"
if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "Error: Executable not found at $EXECUTABLE_PATH"
    exit 1
fi

cp "$EXECUTABLE_PATH" "$MACOS_DIR/"

echo "Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.omac.actionfigures</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$DISPLAY_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$DISPLAY_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2025 OMAC. All rights reserved.</string>
    <key>NSMainStoryboardFile</key>
    <string>Main</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

echo "Setting executable permissions..."
chmod +x "$MACOS_DIR/$APP_NAME"

echo
echo "=== Build Complete ==="
echo "Application bundle created at: $APP_BUNDLE"
echo
echo "To run the app:"
echo "open \"$APP_BUNDLE\""
echo
echo "Or double-click the OMAC.app file in Finder"
echo