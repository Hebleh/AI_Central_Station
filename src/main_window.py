"""
Main Window for AI Central Station
  
A simplified PyQt6 window that:
- Loads apps from data/apps.json
- Creates a card for each app
- Displays cards in a grid layout
"""
  
import json
import os
from pathlib import Path
from typing import List, Optional
from PyQt6.QtCore import QTimer, QEvent
  
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QScrollArea, QPushButton, QDialog,
    QDialogButtonBox, QMessageBox, QFileDialog, QListWidget, QListWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, QPoint
  
from .data_models import App
from .app_card import AppCard
from .launcher import run_all_updates
  

class MainWindow(QMainWindow):
    """Main application window for AI Central Station."""
    
    def __init__(self):
        super().__init__()
        
        # Load apps from JSON
        self.apps: List[App] = []
        self.app_cards: dict[str, AppCard] = {}
        self.edit_app_id: Optional[str] = None  # Track if we're editing an existing app
        
        # Setup UI first
        self.setup_ui()
        
        # Load and display apps
        self.load_apps_from_json()
        
        # Window settings
        self.setWindowTitle("AI Central Station")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)
    
    def setup_ui(self):
        """Set up the main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header section
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 AI Central Station")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #f8f8f2;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add New App button
        self.add_app_button = QPushButton("➕ Add New App")
        self.add_app_button.setStyleSheet("""
            QPushButton {
                background-color: #bd93f9;
                color: #2d2d2d;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c6aef5;
            }
            QPushButton:pressed {
                background-color: #a87dc9;
            }
        """)
        self.add_app_button.clicked.connect(self.show_add_app_dialog)
        header_layout.addWidget(self.add_app_button)
        
        # Sort Grid button (subdued style, fixed height)
        self.sort_grid_button = QPushButton("↕️ Sort Grid")
        self.sort_grid_button.setFixedHeight(36)
        self.sort_grid_button.setStyleSheet("""
            QPushButton {
                background-color: #44475a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #5a5e75;
            }
            QPushButton:pressed {
                background-color: #3d4052;
            }
        """)
        self.sort_grid_button.clicked.connect(self.show_sort_grid_dialog)
        header_layout.addWidget(self.sort_grid_button)
        
        # Update All Split Button
        update_split_layout = QHBoxLayout()
        update_split_layout.setSpacing(0)
        update_split_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Update button (left side - green with rounded left corners)
        self.update_all_button = QPushButton("🔄 Update All")
        self.update_all_button.setFixedHeight(36)
        self.update_all_button.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #2d2d2d;
                border: none;
                border-radius: 6px 0px 0px 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #69ff8e;
            }
            QPushButton:pressed {
                background-color: #3fd165;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
                color: #808080;
            }
        """)
        self.update_all_button.clicked.connect(self.on_update_all_clicked)
        self.update_all_button.setEnabled(False)  # Disabled by default
        update_split_layout.addWidget(self.update_all_button)
        
        # Menu button (right side - darker green with rounded right corners)
        self.update_menu_btn = QPushButton("⋮")
        self.update_menu_btn.setFixedHeight(36)
        self.update_menu_btn.setFixedSize(30, 36)
        self.update_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #3fd165;
                color: #2d2d2d;
                border: none;
                border-radius: 0px 6px 6px 0px;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #35c05a;
            }
        """)
        
        # Create menu for the split button
        update_menu = QMenu(self.update_menu_btn)
        sort_updates_action = update_menu.addAction("Sort Update Sequence")
        sort_updates_action.triggered.connect(self.show_sort_updates_dialog)
        self.update_menu_btn.setMenu(update_menu)
        
        update_split_layout.addWidget(self.update_menu_btn)
        header_layout.addLayout(update_split_layout)
        
        main_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("color: #f8f8f2; font-size: 14px;")
        search_layout.addWidget(search_label)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search apps by name...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #f8f8f2;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #50fa7b;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_apps)
        search_layout.addWidget(self.search_bar)
        
        main_layout.addLayout(search_layout)
        
        # Scrollable grid for app cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            background-color: transparent;
            border: none;
            QScrollBar:vertical {
                border: none;
                background: #21222c;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #44475a;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6272a4;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        self.cards_container = QWidget()
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.cards_container)
        
        main_layout.addWidget(self.scroll_area)
    
    def load_apps_from_json(self):
        """Load apps from data/apps.json and create cards."""
        json_path = Path(__file__).parent.parent / "data" / "apps.json"
        try:
            # Create empty apps.json if it doesn't exist (for fresh installs)
            if not json_path.exists():
                json_path.parent.mkdir(parents=True, exist_ok=True)
                with open(json_path, 'w') as f:
                    json.dump([], f, indent=2)
                print(f"Created new {json_path}")
                self.apps = []
                return
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            self.apps = [App(**app_data) for app_data in data]
            
            # Clear existing cards
            for card in self.app_cards.values():
                card.deleteLater()
            self.app_cards.clear()
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Create new cards
            for i, app in enumerate(self.apps):
                card = AppCard(
                    app_id=app.id,
                    name=app.name,
                    path=app.path,
                    logo_path=app.logo_path,
                    launch_script=app.launch_script,
                    update_script=app.update_script
                )
                card.edit_requested.connect(self.show_add_app_dialog)
                card.delete_requested.connect(self.delete_app)
                self.app_cards[app.id] = card
                self.grid_layout.addWidget(card, i // 3, i % 3)
            
            # Update Update All button state
            apps_with_updates = [a for a in self.apps if a.update_script and a.update_script.strip()]
            self.update_all_button.setEnabled(len(apps_with_updates) > 0)
            
        except Exception as e:
            print(f"Error loading apps: {e}")
    
    def filter_apps(self, search_text: str):
        """Filter visible cards based on search text."""
        search_text = search_text.lower()
        for app_id, card in self.app_cards.items():
            if search_text == "":
                card.setVisible(True)
            else:
                card.setVisible(search_text in app_id.lower() or search_text in card.name.lower())
    
    def show_sort_grid_dialog(self):
        """Show dialog to reorder apps in the grid visually."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Sort Grid Order")
        dialog.setMinimumSize(400, 500)
        dialog.setStyleSheet("background-color: #2d2d2d;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # QListWidget with drag and drop
        list_widget = QListWidget()
        list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #21222c;
                color: #f8f8f2;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #bd93f9;
                color: #2d2d2d;
            }
        """)
        
        # Populate with all apps
        for app in self.apps:
            item = QListWidgetItem(f"{app.name} ({app.id})")
            item.setData(Qt.ItemDataRole.UserRole, app.id)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        
        def on_save():
            # Get new order from QListWidget
            new_order = []
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                app_id = item.data(Qt.ItemDataRole.UserRole)
                new_order.append(app_id)
            
            # Reorder self.apps to match
            apps_dict = {app.id: app for app in self.apps}
            self.apps = [apps_dict[aid] for aid in new_order if aid in apps_dict]
            
            # Save to JSON
            json_path = Path(__file__).parent.parent / "data" / "apps.json"
            try:
                data = [app.model_dump() for app in self.apps]
                with open(json_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Re-render grid
                self.render_grid()
                QMessageBox.information(dialog, "Success", "Grid order updated!")
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save order: {e}")
        
        button_box.accepted.connect(on_save)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def show_sort_updates_dialog(self):
        """Show dialog to reorder update sequence (only apps with update scripts)."""
        # Filter apps with valid update scripts
        apps_with_updates = [app for app in self.apps if app.update_script and app.update_script.strip()]
        
        if not apps_with_updates:
            QMessageBox.information(self, "Info", "No apps with update scripts found.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Sort Update Sequence")
        dialog.setMinimumSize(400, 500)
        dialog.setStyleSheet("background-color: #2d2d2d;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        info_label = QLabel("Drag to reorder update sequence. Lower items run first.")
        info_label.setStyleSheet("color: #f8f8f2; font-size: 12px;")
        layout.addWidget(info_label)
        
        # QListWidget with drag and drop
        list_widget = QListWidget()
        list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #21222c;
                color: #f8f8f2;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #ff79c6;
                color: #2d2d2d;
            }
        """)
        
        # Sort apps by current update_order and populate
        sorted_apps = sorted(apps_with_updates, key=lambda x: x.update_order)
        for app in sorted_apps:
            item = QListWidgetItem(app.name)
            item.setData(Qt.ItemDataRole.UserRole, app.id)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        
        def on_save():
            # Update update_order based on new position in list
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                app_id = item.data(Qt.ItemDataRole.UserRole)
                # Find app in self.apps and update its order
                for app in self.apps:
                    if app.id == app_id:
                        app.update_order = i  # 0-indexed position
                        break
            
            # Save to JSON
            json_path = Path(__file__).parent.parent / "data" / "apps.json"
            try:
                data = [app.model_dump() for app in self.apps]
                with open(json_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                QMessageBox.information(dialog, "Success", "Update sequence updated!")
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save order: {e}")
        
        button_box.accepted.connect(on_save)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def show_add_app_dialog(self, edit_app_id: Optional[str] = None):
        """Show dialog to add a new app."""
        if edit_app_id:
            self.edit_app_id = edit_app_id
        else:
            self.edit_app_id = None
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New App" if not edit_app_id else "Edit App")
        dialog.setMinimumWidth(550)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet("background-color: #2d2d2d;")
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        
        # Create QGridLayout for form fields
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setHorizontalSpacing(15)
        
        # Create all widgets first
        launch_label = QLabel("App File / Launch Script:")
        launch_input = QLineEdit()
        launch_input.setPlaceholderText("start.bat or .exe filename")
        launch_browse_btn = QPushButton("Browse...")
        launch_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        
        name_label = QLabel("App Name:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Auto-populated from folder name")
        
        path_label = QLabel("Installation Path:")
        path_input = QLineEdit()
        path_input.setPlaceholderText("C:\\path\\to\\app")
        path_browse_btn = QPushButton("Browse...")
        path_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        
        update_label = QLabel("Update Script (optional):")
        update_input = QLineEdit()
        update_input.setPlaceholderText("update.bat or .exe filename")
        update_browse_btn = QPushButton("Browse...")
        update_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        
        logo_label = QLabel("Logo (optional):")
        logo_input = QLineEdit()
        logo_input.setPlaceholderText("Path to .ico, .png, .jpg image")
        logo_browse_btn = QPushButton("Browse...")
        logo_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        
        # Add widgets to grid (Row, Column)
        form_layout.addWidget(launch_label, 0, 0)
        form_layout.addWidget(launch_input, 0, 1)
        form_layout.addWidget(launch_browse_btn, 0, 2)
        
        form_layout.addWidget(name_label, 1, 0)
        form_layout.addWidget(name_input, 1, 1, 1, 2)  # Span columns 1-2
        
        form_layout.addWidget(path_label, 2, 0)
        form_layout.addWidget(path_input, 2, 1)
        form_layout.addWidget(path_browse_btn, 2, 2)
        
        form_layout.addWidget(update_label, 3, 0)
        form_layout.addWidget(update_input, 3, 1)
        form_layout.addWidget(update_browse_btn, 3, 2)
        
        form_layout.addWidget(logo_label, 4, 0)
        form_layout.addWidget(logo_input, 4, 1)
        form_layout.addWidget(logo_browse_btn, 4, 2)
        
        # Force column stretching: Column 1 (inputs) stretches, others fixed
        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(2, 0)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()  # Push buttons to bottom
        
        # Auto-populate app name when path changes
        def auto_populate_name():
            path_text = path_input.text().strip()
            if path_text and not name_input.text():  # Only populate if name is empty
                folder_name = Path(path_text).name
                name_input.setText(folder_name)
        
        # Connect browse buttons (all inputs now defined)
        launch_browse_btn.clicked.connect(lambda: self.browse_script(path_input, launch_input))
        path_browse_btn.clicked.connect(lambda: self.browse_directory(path_input))
        update_browse_btn.clicked.connect(lambda: self.browse_update_script(path_input, update_input))
        logo_browse_btn.clicked.connect(lambda: self.browse_logo(path_input, logo_input))
        path_input.textChanged.connect(auto_populate_name)
        
        # Button row (right-aligned with stretch)
        button_row = QHBoxLayout()
        button_row.addStretch()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setStyleSheet(self._get_button_style("#50fa7b"))
        cancel_btn.setStyleSheet(self._get_button_style("#ff5555"))
        button_row.addWidget(save_btn)
        button_row.addWidget(cancel_btn)
        main_layout.addLayout(button_row)
        
        # Connect custom buttons
        save_btn.clicked.connect(lambda: self.save_app(
            dialog, name_input, path_input, launch_input, update_input, logo_input
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        # Populate if editing
        if edit_app_id:
            self._populate_edit_dialog(
                edit_app_id, name_input, path_input, launch_input, update_input, logo_input
            )
        
        dialog.exec()
    
    def browse_directory(self, path_input: QLineEdit):
        """Open directory browser for installation path."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            path_input.text() or str(Path.home())
        )
        if directory:
            path_input.setText(directory)
    
    def browse_script(self, path_input: QLineEdit, script_input: QLineEdit):
        """Open file browser for scripts and auto-populate both path and filename."""
        # Start in current path if available, otherwise home
        start_dir = path_input.text() if path_input.text() else str(Path.home())
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Script",
            directory=start_dir,
            filter="Scripts (*.bat *.exe *.cmd);;All Files (*)"
        )
        if filename:
            # Split into directory and filename
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)
            # Update both fields
            path_input.setText(dir_path)
            script_input.setText(file_name)
    
    def browse_update_script(self, path_input: QLineEdit, script_input: QLineEdit):
        """Open file browser for update script, starting in Installation Path directory."""
        # Always start in the Installation Path if it exists
        start_dir = path_input.text() if path_input.text() and os.path.isdir(path_input.text()) else str(Path.home())
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Update Script",
            directory=start_dir,
            filter="Scripts (*.bat *.exe *.cmd);;All Files (*)"
        )
        if filename:
            # Split into directory and filename
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)
            # Update both fields (in case user changed to different folder)
            path_input.setText(dir_path)
            script_input.setText(file_name)
    
    def browse_logo(self, path_input: QLineEdit, logo_input: QLineEdit):
        """Open file browser for image files."""
        # Smart browsing: start in Installation Path if valid directory exists
        start_dir = path_input.text() if path_input.text() and os.path.isdir(path_input.text()) else str(Path.home())
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo Image",
            start_dir,
            "Images (*.ico *.png *.jpg *.jpeg);;All Files (*)"
        )
        if filename:
            logo_input.setText(filename)
    
    def _populate_edit_dialog(self, app_id: str, name_input, path_input, launch_input, update_input, logo_input):
        """Load existing app data into dialog inputs."""
        try:
            json_path = Path(__file__).parent.parent / "data" / "apps.json"
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for app in data:
                if app['id'] == app_id:
                    name_input.setText(app.get('name', ''))
                    path_input.setText(app.get('path', ''))
                    launch_input.setText(app.get('launch_script', ''))
                    update_input.setText(app.get('update_script') or '')
                    logo_input.setText(app.get('logo_path') or '')
                    break
        except Exception as e:
            print(f"Error loading app data: {e}")
    
    def save_app(self, dialog, name_input, path_input, launch_input, update_input, logo_input):
        """Route to add or edit based on context."""
        if self.edit_app_id:
            self.save_app_edit(dialog, name_input, path_input, launch_input, update_input, logo_input)
        else:
            self.save_new_app(dialog, name_input, path_input, launch_input, update_input, logo_input)
    
    def save_new_app(self, dialog, name_input, path_input, launch_input, update_input, logo_input):
        """Validate and save new app to apps.json."""
        # Get values
        raw_name = name_input.text().strip()
        path = path_input.text().strip()
        
        # Optional Name: if empty, extract from folder name
        if not raw_name:
            if path:
                raw_name = os.path.basename(path.rstrip("\\/"))
            else:
                QMessageBox.warning(dialog, "Validation Error", "Name or Installation Path is required.")
                return
        
        # Auto-generate ID from name (lowercase, spaces to underscores)
        app_id = raw_name.lower().replace(" ", "_")
        name = raw_name
        path = path_input.text().strip()
        launch_script = launch_input.text().strip()
        update_script = update_input.text().strip() or None
        logo_path = logo_input.text().strip() or None
        
        # Validation
        if not path:
            QMessageBox.warning(dialog, "Validation Error", "Name is required.")
            return
        if not path:
            QMessageBox.warning(dialog, "Validation Error", "Installation Path is required.")
            return
        if not launch_script:
            QMessageBox.warning(dialog, "Validation Error", "Launch Script is required.")
            return
        
        # Check for duplicate ID
        json_path = Path(__file__).parent.parent / "data" / "apps.json"
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            existing_ids = [app['id'] for app in data]
            if app_id in existing_ids:
                QMessageBox.warning(dialog, "Validation Error", f"An app with ID '{app_id}' already exists. Please use a unique ID.")
                return
        except Exception as e:
            print(f"Error checking existing apps: {e}")
            return
        
        # Create new app entry
        new_app = {
            "id": app_id,
            "name": name,
            "path": path,
            "launch_script": launch_script,
            "update_script": update_script,
            "logo_path": logo_path
        }
        
        try:
            data.append(new_app)
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(dialog, "Success", f"App '{name}' added successfully!")
            dialog.accept()
            
            # Refresh the main window
            self.refresh_apps()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to save app: {e}")
    
    def save_app_edit(self, dialog, name_input, path_input, launch_input, update_input, logo_input):
        """Validate and update existing app in apps.json."""
        # Get values
        app_id = self.edit_app_id  # ID is fixed when editing
        name = name_input.text().strip()
        path = path_input.text().strip()
        launch_script = launch_input.text().strip()
        update_script = update_input.text().strip() or None
        logo_path = logo_input.text().strip() or None
        
        # Validation
        if not name:
            QMessageBox.warning(dialog, "Validation Error", "Name is required.")
            return
        if not path:
            QMessageBox.warning(dialog, "Validation Error", "Installation Path is required.")
            return
        if not launch_script:
            QMessageBox.warning(dialog, "Validation Error", "Launch Script is required.")
            return
        
        json_path = Path(__file__).parent.parent / "data" / "apps.json"
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Find and update existing entry by ID
            updated = False
            for i, app in enumerate(data):
                if app['id'] == app_id:
                    data[i] = {
                        "id": app_id,
                        "name": name,
                        "path": path,
                        "launch_script": launch_script,
                        "update_script": update_script,
                        "logo_path": logo_path
                    }
                    updated = True
                    break
            
            if not updated:
                QMessageBox.warning(dialog, "Error", f"App with ID '{app_id}' not found.")
                return
            
            # Write back to JSON
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(dialog, "Success", f"App '{name}' updated successfully!")
            dialog.accept()
            self.refresh_apps()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to update app: {e}")
    
    def on_update_all_clicked(self):
        """Handle Update All button click."""
        if not self.apps:
            return
        run_all_updates(self.apps)
    
    def delete_app(self, app_id: str):
        """Delete an app from the launcher with confirmation dialog."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to remove "{self.app_cards[app_id].name}" from the launcher?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove app from list
                self.apps = [a for a in self.apps if a.id != app_id]
                
                # Save updated apps to JSON
                json_path = Path('data/apps.json')
                apps_data = [app.model_dump() for app in self.apps]
                with open(json_path, 'w') as f:
                    json.dump(apps_data, f, indent=2)
                
                # Remove the card from the dictionary
                if app_id in self.app_cards:
                    del self.app_cards[app_id]
                
                # Refresh the grid to visually remove the card
                self.render_grid()
                
                print(f"App '{app_id}' deleted successfully")
                
            except Exception as e:
                print(f"Error deleting app {app_id}: {e}")
                import traceback
                traceback.print_exc()
    
    def resizeEvent(self, event):
        """Handle window resize - trigger responsive grid reflow with debounce."""
        super().resizeEvent(event)
        # Use QTimer to debounce rapid resize events
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self.render_grid)
        
        self._resize_timer.stop()
        self._resize_timer.start(100)  # 100ms debounce
    
    def render_grid(self):
        """Render apps in a responsive grid based on available width."""
        if not hasattr(self, 'grid_layout') or not hasattr(self, 'app_cards'):
            return
        
        # Calculate columns: card_width (240) + spacing (15) = 255 per column
        # Use scroll area width minus margins
        available_width = self.cards_container.width() - 40  # Account for margins
        columns = max(1, available_width // 260)
        
        # Clear current grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)  # Orphan the widget (don't delete, just remove from layout)
        
        # Set alignment to top-left for proper flow
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Repopulate grid with current apps in order
        for i, app in enumerate(self.apps):
            if app.id in self.app_cards:
                card = self.app_cards[app.id]
                row = i // columns
                col = i % columns
                self.grid_layout.addWidget(card, row, col)
    
    def refresh_apps(self):
        """Reload apps from JSON and rebuild UI."""
        self.load_apps_from_json()
    
    def _get_button_style(self, color: str) -> str:
        """Helper to generate consistent button styles."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """
