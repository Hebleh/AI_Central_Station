"""
App Card Widget for AI Central Station
  
A simplified PyQt6 widget that displays an individual app as a card with:
- App logo/image (dynamic from assets/ or default colored box)
- Name label
- Launch button
- Update button (disabled if no update script configured)
- Edit button (opens edit dialog)
"""
  
from pathlib import Path
import os
import hashlib
from typing import Optional
  
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFileIconProvider, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QFileInfo, pyqtSignal, QPoint, QRectF
from PyQt6.QtGui import (QPixmap, QColor, QIcon, QPainter, QLinearGradient,
                         QPen, QFont)
  

class AppCard(QFrame):
    """A card widget displaying a single app with Launch and Update buttons."""
    
    # Signal emitted when Edit button is clicked, passing the app_id
    edit_requested = pyqtSignal(str)
    
    def __init__(
        self,
        app_id: str,
        name: str,
        path: Optional[str] = None,
        logo_path: Optional[str] = None,
        launch_script: Optional[str] = None,
        update_script: Optional[str] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        # Step 1: Lock the size to create a visible physical card
        self.setFixedSize(240, 280)
        
        self.app_id = app_id
        self.name = name
        self.path = path
        self.logo_path = logo_path
        self.launch_script = launch_script
        self.update_script = update_script
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the card UI."""
        # Step 1: Force visible background with simple stylesheet
        self.setStyleSheet("AppCard { background-color: #2a2b36; border-radius: 12px; }")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        # Step 2: Cluster elements in center with fixed spacing
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # App logo/image - priority order:
        # 1. Custom Logo Path (if provided and valid)
        # 2. Native .exe icon (if target is an executable)
        # 3. assets/{app_id}.png or .jpg
        # 4. Colored box with first letter
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(120)
        
        logo_loaded = False
        
        # Step 1: Try Custom Logo Path (highest priority)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                pixmap = QPixmap(self.logo_path).scaled(
                    100, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                if not pixmap.isNull():
                    self.logo_label.setPixmap(pixmap)
                    logo_loaded = True
            except Exception:
                pass  # Continue to next fallback
        
        # Step 2: Try to extract icon from .exe if path points to executable or script is .exe
        if not logo_loaded:
            exe_path = None
            if self.path and self.launch_script:
                if os.path.isfile(self.path) and self.path.lower().endswith('.exe'):
                    exe_path = self.path
                elif (self.launch_script.lower().endswith('.exe') and
                      os.path.isfile(os.path.join(self.path, self.launch_script))):
                    exe_path = os.path.join(self.path, self.launch_script)
            
            if exe_path and os.path.exists(exe_path):
                try:
                    # Extract native Windows icon using QFileIconProvider
                    file_info = QFileInfo(exe_path)
                    icon_provider = QFileIconProvider()
                    icon = icon_provider.icon(file_info)
                    pixmap = icon.pixmap(100, 100)
                    if not pixmap.isNull():
                        self.logo_label.setPixmap(pixmap)
                        logo_loaded = True
                except Exception:
                    pass  # Continue to next fallback
        
        # Step 3: Try assets folder (PNG then JPG)
        if not logo_loaded:
            logo_file = None
            for ext in ['.png', '.jpg']:
                potential_path = Path('assets') / f"{self.app_id}{ext}"
                if potential_path.exists():
                    logo_file = str(potential_path)
                    break
            
            if logo_file and os.path.exists(logo_file):
                try:
                    pixmap = QPixmap(logo_file).scaled(
                        100, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.logo_label.setPixmap(pixmap)
                    logo_loaded = True
                except Exception:
                    pass  # Continue to default
        
        # Step 4: Default colored box with first letter
        if not logo_loaded:
            self._set_default_logo()
        
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # App name
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #f8f8f2;
        """)
        main_layout.addWidget(self.name_label)
        
        # Action buttons - stacked layout
        main_layout.addSpacing(5)
        
        # Row 1: Full-width Launch button
        self.launch_button = QPushButton("▶ Launch")
        self.launch_button.setFixedHeight(32)
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #2d2d2d;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #69ff97;
            }
            QPushButton:pressed {
                background-color: #4ed968;
            }
        """)
        self.launch_button.clicked.connect(self.on_launch_clicked)
        main_layout.addWidget(self.launch_button)
        
        # Row 2: Update (2/3) + Menu (1/3)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(8)
        
        self.update_button = QPushButton("🔄 Update")
        self.update_button.setFixedHeight(32)
        if not self.update_script:
            self.update_button.setEnabled(False)
            self.update_button.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: #888888;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 5px 8px;
                }
            """)
        else:
            self.update_button.setStyleSheet("""
                QPushButton {
                    background-color: #8be9fd;
                    color: #2d2d2d;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 5px 8px;
                }
                QPushButton:hover {
                    background-color: #a5f0ff;
                }
                QPushButton:pressed {
                    background-color: #7bd9ee;
                }
            """)
        self.update_button.clicked.connect(self.on_update_clicked)
        row2_layout.addWidget(self.update_button, stretch=2)  # 2/3 of space
        
        # Menu button - fixed square, takes remaining 1/3
        self.menu_button = QPushButton("⋮")
        self.menu_button.setFixedSize(32, 32)
        self.menu_button.setToolTip("Options")
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f8f8f2;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                padding: 2px 4px;
                min-width: 0;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        
        # Create menu with Edit and Open Folder options
        self.options_menu = QMenu(self)
        self.options_menu.setStyleSheet("""
            QMenu {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1px solid #44475a;
                border-radius: 6px;
                padding: 8px 0;
                font-size: 14px;
            }
            QMenu::item {
                padding: 8px 25px 8px 30px;
                background-color: transparent;
                min-width: 150px;
            }
            QMenu::item:selected {
                background-color: #44475a;
            }
            QMenu::separator {
                height: 1px;
                background-color: #6272a4;
                margin: 4px 0;
            }
        """)
        self.edit_action = self.options_menu.addAction("✏️ Edit")
        self.open_folder_action = self.options_menu.addAction("📁 Open Folder")
        
        self.edit_action.triggered.connect(self.on_edit_clicked)
        self.open_folder_action.triggered.connect(self.on_open_folder_clicked)
        
        # Connect to dedicated method instead of lambda to prevent garbage collection issues
        self.menu_button.clicked.connect(self.on_menu_button_clicked)
        row2_layout.addWidget(self.menu_button, stretch=1)  # 1/3 of space
        
        main_layout.addLayout(row2_layout)
    
    
    def _set_default_logo(self):
        """Set default logo - gradient squircle with app's first letter using QPainter."""
        size = 100
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient from top-left to bottom-right
        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0, QColor("#2b2e3b"))
        gradient.setColorAt(1, QColor("#1e1f29"))
        
        # Draw rounded rectangle (squircle-like) with gradient
        rect = QRectF(4, 4, size - 8, size - 8)
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#44475a"), 1))
        painter.drawRoundedRect(rect, 12, 12)
        
        # Draw first letter centered
        first_letter = self.name[0].upper() if self.name else '?'
        font = QFont("Arial", 48, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, first_letter)
        
        painter.end()
        
        self.logo_label.setPixmap(pixmap)
    
    def on_launch_clicked(self):
        """Handle launch button click."""
        if self.launch_script and self.path:
            from src.launcher import launch_app
            launch_app(self.path, self.launch_script)
        else:
            print(f"No launch script configured for {self.name}")
    
    def on_update_clicked(self):
        """Handle update button click."""
        if self.update_script and self.path:
            from src.launcher import run_update
            run_update(self.path, self.update_script)
        else:
            print(f"No update script configured for {self.name}")
    
    def on_edit_clicked(self):
        """Handle edit action - emit signal with app_id."""
        self.edit_requested.emit(self.app_id)
    
    def on_menu_button_clicked(self):
        """Handle 3-dot menu button click - show context menu."""
        try:
            # Calculate position below the center of the button
            # PyQt6 requires QPoint objects, not separate x,y integers
            button_width = self.menu_button.width()
            global_pos = self.menu_button.mapToGlobal(
                QPoint(button_width // 2, self.menu_button.height())
            )
            
            # Show menu at calculated position
            self.options_menu.popup(global_pos)
            
        except Exception as e:
            print(f"[ERROR] Failed to show menu for {self.name}: {e}")
            import traceback
            traceback.print_exc()
    
    def on_open_folder_clicked(self):
        """Handle Open Folder action - open app directory in Windows Explorer."""
        if self.path:
            try:
                os.startfile(self.path)
            except Exception as e:
                print(f"Error opening folder '{self.path}': {e}")
        else:
            print(f"No path configured for {self.name}")
