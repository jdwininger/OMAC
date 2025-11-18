#!/usr/bin/env python3
"""
Theme manager for OMAC application.
Provides light and dark theme support using PyQt6 palettes and stylesheets.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class ThemeManager:
    """Manages application themes (light/dark mode)."""

    LIGHT_THEME = "light"
    DARK_THEME = "dark"
    DRACULA_THEME = "dracula"

    def __init__(self):
        self.current_theme = self.LIGHT_THEME
        self.themes = {
            self.LIGHT_THEME: self._create_light_palette(),
            self.DARK_THEME: self._create_dark_palette(),
            self.DRACULA_THEME: self._create_dracula_palette()
        }

    def _create_light_palette(self):
        """Create a light theme palette."""
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))

        # Base colors (for input fields, etc.)
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 248, 248))

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))

        # Highlight colors (selection)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(51, 153, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))

        # Tooltips
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))

        return palette

    def _create_dark_palette(self):
        """Create a dark theme palette."""
        palette = QPalette()

        # Window colors - dark background
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))

        # Base colors - darker input fields
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))

        # Text colors - light text on dark background
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Button colors - dark buttons
        palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))

        # Highlight colors - blue selection with white text
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Links - lighter blue for dark theme
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 150, 255))

        # Tooltips - dark tooltips with light text
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))

        return palette

    def _create_dracula_palette(self):
        """Create a Dracula theme palette."""
        palette = QPalette()

        # Dracula theme colors
        # Background: #282a36
        # Current line: #44475a
        # Foreground: #f8f8f2
        # Purple: #bd93f9
        # Cyan: #8be9fd
        # Comment: #6272a4

        # Window colors - Dracula background (slightly lighter for better contrast)
        palette.setColor(QPalette.ColorRole.Window, QColor(46, 49, 62))  # Slightly lighter #282a36
        palette.setColor(QPalette.ColorRole.WindowText, QColor(248, 248, 242))  # #f8f8f2

        # Base colors - Dracula current line for input fields
        palette.setColor(QPalette.ColorRole.Base, QColor(68, 71, 90))  # #44475a
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(46, 49, 62))  # #282a36

        # Text colors - Dracula foreground
        palette.setColor(QPalette.ColorRole.Text, QColor(248, 248, 242))  # #f8f8f2
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Button colors - Dracula current line
        palette.setColor(QPalette.ColorRole.Button, QColor(68, 71, 90))  # #44475a
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(248, 248, 242))  # #f8f8f2

        # Highlight colors - Dracula purple selection
        palette.setColor(QPalette.ColorRole.Highlight, QColor(189, 147, 249))  # #bd93f9
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(46, 49, 62))  # #282a36

        # Links - Dracula cyan
        palette.setColor(QPalette.ColorRole.Link, QColor(139, 233, 253))  # #8be9fd

        # Tooltips - Dracula background with foreground text
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(68, 71, 90))  # #44475a
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(248, 248, 242))  # #f8f8f2

        return palette

    def set_theme(self, theme_name):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            app = QApplication.instance()
            if app:
                app.setPalette(self.themes[theme_name])
                # Apply theme-specific stylesheet
                app.setStyleSheet(self.get_theme_stylesheet())
                # Force a style update for all widgets
                for widget in app.allWidgets():
                    widget.update()
        else:
            raise ValueError(f"Unknown theme: {theme_name}")

    def get_current_theme(self):
        """Get the current theme name."""
        return self.current_theme

    def get_available_themes(self):
        """Get list of available theme names."""
        return list(self.themes.keys())

    def get_theme_stylesheet(self):
        """Get theme-specific CSS styles."""
        if self.current_theme == self.DRACULA_THEME:
            return """
                /* Dracula theme specific styles */
                QWidget#menubar {
                    background-color: #44475a;
                    border-bottom: 1px solid #6272a4;
                }
                
                QLabel {
                    color: #f8f8f2;
                }
                
                /* Ensure search label is visible */
                QLabel[style*="font-weight: bold"] {
                    color: #f8f8f2;
                }
            """
        elif self.current_theme == self.DARK_THEME:
            return """
                /* Dark theme specific styles */
                QWidget#menubar {
                    background-color: #2d2d2d;
                    border-bottom: 1px solid #555555;
                }
                
                QLabel {
                    color: #dcdcdc;
                }
            """
        else:  # Light theme
            return """
                /* Light theme specific styles */
                QWidget#menubar {
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #cccccc;
                }
                
                QLabel {
                    color: #000000;
                }
            """