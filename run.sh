#!/bin/bash
# OMAC - One 'Mazing Action Catalog Runner Script
#
# This script sets up the environment and runs the OMAC application.
# It handles virtual environment activation, environment variables, and platform detection.

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Environment Variables
export OMAC_HOME="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Virtual environment path
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON=""
VENV_PIP=""

# Detect platform and set platform-specific variables
case "$(uname -s)" in
    Darwin)
        # macOS
        export OMAC_PLATFORM="macos"
        export OMAC_DATA_DIR="$HOME/Library/Application Support/OMAC"
        VENV_PYTHON="$VENV_DIR/bin/python"
        VENV_PIP="$VENV_DIR/bin/pip"
        ;;
    Linux)
        # Linux
        export OMAC_PLATFORM="linux"
        export OMAC_DATA_DIR="$SCRIPT_DIR"  # Current directory for Linux
        VENV_PYTHON="$VENV_DIR/bin/python"
        VENV_PIP="$VENV_DIR/bin/pip"
        ;;
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        # Windows (Git Bash, MSYS2, etc.)
        export OMAC_PLATFORM="windows"
        export OMAC_DATA_DIR="$HOME/Documents/OMAC"
        VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
        VENV_PIP="$VENV_DIR/Scripts/pip.exe"
        ;;
    *)
        echo "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Create data directories if they don't exist
export OMAC_PHOTOS_DIR="$OMAC_DATA_DIR/photos"
mkdir -p "$OMAC_DATA_DIR"
mkdir -p "$OMAC_PHOTOS_DIR"

# Database path
export OMAC_DATABASE="$OMAC_DATA_DIR/action_figures.db"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Please run: python quickstart.py"
    echo "Or manually create venv and install requirements.txt"
    exit 1
fi

# Check if virtual environment Python exists
if [ ! -x "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment Python not found at: $VENV_PYTHON"
    echo "Please recreate the virtual environment"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
if ! "$VENV_PYTHON" -c "import PyQt6" 2>/dev/null; then
    echo "❌ PyQt6 not found in virtual environment"
    echo "Please run: $VENV_PIP install -r requirements.txt"
    exit 1
fi

if ! "$VENV_PYTHON" -c "import PIL" 2>/dev/null; then
    echo "❌ Pillow (PIL) not found in virtual environment"
    echo "Please run: $VENV_PIP install -r requirements.txt"
    exit 1
fi

# Set Qt platform plugin path for Linux (if needed)
if [ "$OMAC_PLATFORM" = "linux" ]; then
    export QT_QPA_PLATFORM_PLUGIN_PATH="$("$VENV_PYTHON" -c "import PyQt6.QtCore; import os; print(os.path.join(os.path.dirname(PyQt6.QtCore.__file__), 'Qt6', 'plugins', 'platforms'))")"
fi

# Display environment information
echo "🚀 Starting OMAC - One 'Mazing Action Catalog"
echo "📁 Script Directory: $SCRIPT_DIR"
echo "🏠 Data Directory: $OMAC_DATA_DIR"
echo "📸 Photos Directory: $OMAC_PHOTOS_DIR"
echo "💾 Database: $OMAC_DATABASE"
echo "🐍 Python: $VENV_PYTHON"
echo "🖥️  Platform: $OMAC_PLATFORM"
echo ""

# Change to script directory and run the application
cd "$SCRIPT_DIR"
echo "🎯 Launching application..."
exec "$VENV_PYTHON" main.py "$@"