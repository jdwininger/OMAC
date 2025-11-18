#!/usr/bin/env python3
"""
Quick test script to verify theme switching functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from theme_manager import ThemeManager

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()

        self.setWindowTitle("Theme Test")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        light_button = QPushButton("Light Theme")
        light_button.clicked.connect(self.set_light_theme)
        layout.addWidget(light_button)

        dark_button = QPushButton("Dark Theme")
        dark_button.clicked.connect(self.set_dark_theme)
        layout.addWidget(dark_button)

        dracula_button = QPushButton("Dracula Theme")
        dracula_button.clicked.connect(self.set_dracula_theme)
        layout.addWidget(dracula_button)

        central_widget.setLayout(layout)

    def set_light_theme(self):
        self.theme_manager.set_theme(ThemeManager.LIGHT_THEME)
        print("Switched to light theme")

    def set_dark_theme(self):
        self.theme_manager.set_theme(ThemeManager.DARK_THEME)
        print("Switched to dark theme")

    def set_dracula_theme(self):
        self.theme_manager.set_theme(ThemeManager.DRACULA_THEME)
        print("Switched to Dracula theme")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())