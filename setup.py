#!/usr/bin/env python3
"""
Setup script for building OMAC as a standalone macOS application using py2app.
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'packages': ['PyQt6', 'PIL'],  # Include PyQt6 and Pillow packages
    'includes': ['database'],  # Include the database module
    'excludes': [  # Exclude unnecessary modules to reduce bundle size
        'tkinter',
        'unittest',
        'pdb',
        'pydoc',
        'test',
        'distutils',
        'setuptools',
    ],
    'iconfile': None,  # No custom icon for now
    'plist': {
        'CFBundleName': 'OMAC',
        'CFBundleDisplayName': 'OMAC - Action Figure Catalog',
        'CFBundleGetInfoString': 'One \'Mazing ActionFigure Catalog',
        'CFBundleIdentifier': 'com.omac.actionfigurecatalog',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 OMAC Team',
        'LSMinimumSystemVersion': '10.12.0',  # Minimum macOS version
        'LSApplicationCategoryType': 'public.app-category.productivity',
    },
    'resources': [],  # Additional resources if needed
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)