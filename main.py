"""
AI Central Station - Main Entry Point

A local desktop application for managing, launching, and updating AI applications.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.main_window import MainWindow


def main():
    """Main entry point for AI Central Station."""
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application instance
    app = QApplication(sys.argv)
    app.setApplicationName("AI Central Station")
    app.setOrganizationName("LocalDev")
    
    # Apply global dark theme style
    app.setStyleSheet("""
        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        QMainWindow {
            background-color: #1e1e1e;
        }
        
        QLabel {
            color: #f8f8f2;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()