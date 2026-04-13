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
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFileIconProvider
)
from PyQt6.QtCore import Qt, QFileInfo, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QIcon
  

class AppCard(QWidget):
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
        
        self.app_id = app_id
        self.name = name
        self.path = path
        self.logo_path = logo_path
        self.launch_script = launch_script
        self.update_script = update_script
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the card UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Set card styling
        self.setStyleSheet("""
            AppCard {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }
            AppCard:hover {
                border-color: #50fa7b;
            }
        """)
        
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
        
        # Spacer
        main_layout.addStretch()
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Launch button
        self.launch_button = QPushButton("▶ Launch")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #2d2d2d;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #69ff97;
            }
            QPushButton:pressed {
                background-color: #4ed968;
            }
        """)
        self.launch_button.clicked.connect(self.on_launch_clicked)
        buttons_layout.addWidget(self.launch_button)
        
        # Update button - disable if no update script configured
        self.update_button = QPushButton("🔄 Update")
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
                    padding: 8px 16px;
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
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #a5f0ff;
                }
                QPushButton:pressed {
                    background-color: #7bd9ee;
                }
            """)
        self.update_button.clicked.connect(self.on_update_clicked)
        buttons_layout.addWidget(self.update_button)
        
        # Edit button
        self.edit_button = QPushButton("✏️")
        self.edit_button.setToolTip("Edit App")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3d59a1;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                padding: 8px 12px;
                min-width: 36px;
            }
            QPushButton:hover {
                background-color: #4b7bec;
            }
            QPushButton:pressed {
                background-color: #2d4a8f;
            }
        """)
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _extract_exe_icon(self, exe_path: str) -> QPixmap:
        """Extract icon from Windows executable using pywin32.
        
        Args:
            exe_path: Path to the .exe file
            
        Returns:
            QPixmap containing the extracted icon, or null pixmap if failed
        """
        try:
            import win32gui
            from PIL import Image
            import io
            
            # Extract large icon (index 0) from executable
            hicon, _ = win32gui.ExtractIconEx(exe_path, 0)
            
            if hicon and len(hicon) > 0:
                # Get icon info to retrieve bitmap handle
                icon_info = win32gui.GetIconInfo(hicon[0])
                bmp_handle = icon_info['bmBitmap']
                
                # Get bitmap info
                bmp_info = win32gui.GetObject(bmp_handle)
                width = bmp_info['bmWidth']
                height = bmp_info['bmHeight']
                
                # Create DIB from icon
                ico_x = win32gui.GetIconInfo(hicon[0])['bxLeft']
                ico_y = win32gui.GetIconInfo(hicon[0])['byTop']
                
                # Alternative: Use GetIconInfo and create bitmap
                dc = win32gui.GetDC(0)
                mem_dc = win32gui.CreateCompatibleDC(dc)
                new_bmp = win32gui.CreateCompatibleBitmap(dc, width, height)
                old_bmp = win32gui.SelectObject(mem_dc, new_bmp)
                
                # Draw icon to memory DC
                win32gui.DrawIconEx(mem_dc, 0, 0, hicon[0], width, height, 0, None, win32gui.DI_NORMAL)
                
                # Get bitmap bits
                bmpinfo = {
                    'bmBits': win32gui.GetBitmapBits(new_bmp),
                    'bmWidth': width,
                    'bmHeight': height,
                    'bmWidthBytes': ((width * 24 + 31) // 32) * 4
                }
                
                # Convert to PIL Image (BGR format)
                image_data = bmpinfo['bmBits']
                pil_image = Image.frombuffer(
                    'RGB', (width, height), image_data, 'raw', 'BGRX', 0, 1
                )
                
                # Cleanup
                win32gui.SelectObject(mem_dc, old_bmp)
                win32gui.DeleteObject(new_bmp)
                win32gui.DeleteDC(mem_dc)
                win32gui.ReleaseDC(0, dc)
                win32gui.DestroyIcon(hicon[0])
                
                # Convert PIL Image to QPixmap
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                return pixmap
                
        except ImportError:
            print("pywin32 or Pillow not installed for icon extraction")
        except Exception as e:
            print(f"Failed to extract icon from {exe_path}: {e}")
        
        return QPixmap()  # Return null pixmap on failure
    
    def _set_default_logo(self):
        """Set default logo - colored box with app's first letter."""
        first_letter = self.name[0].upper() if self.name else '?'
        # Generate a consistent color based on the app_id
        hash_val = int(hashlib.md5(self.app_id.encode()).hexdigest()[:6], 16)
        r = (hash_val >> 16) & 0xFF
        g = (hash_val >> 8) & 0xFF
        b = hash_val & 0xFF
        
        self.logo_label.setText(first_letter)
        self.logo_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: white;
            background-color: #{r:02x}{g:02x}{b:02x};
            border-radius: 50px;
            padding: 10px;
        """)
    
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
        """Handle edit button click - emit signal with app_id."""
        self.edit_requested.emit(self.app_id)
