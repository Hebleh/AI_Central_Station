"""
Main Window for AI Central Station
  
A simplified PyQt6 window that:
- Loads apps from data/apps.json
- Creates a card for each app
- Displays cards in a grid layout
"""
  
import json
from pathlib import Path
from typing import List, Optional
  
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QScrollArea, QPushButton, QDialog,
    QDialogButtonBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
  
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
        
        # Update All button
        self.update_all_button = QPushButton("🔄 Update All")
        self.update_all_button.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #2d2d2d;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
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
        header_layout.addWidget(self.update_all_button)
        
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.cards_container = QWidget()
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.cards_container)
        
        main_layout.addWidget(scroll)
    
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
    
    def show_add_app_dialog(self, edit_app_id: Optional[str] = None):
        """Show dialog to add a new app."""
        if edit_app_id:
            self.edit_app_id = edit_app_id
        else:
            self.edit_app_id = None
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New App" if not edit_app_id else "Edit App")
        dialog.setMinimumSize(500, 600)
        dialog.setStyleSheet("background-color: #2d2d2d;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # ID input (disabled if editing)
        id_layout = QHBoxLayout()
        id_label = QLabel("ID:")
        id_input = QLineEdit()
        id_input.setPlaceholderText("e.g., my_app")
        if edit_app_id:
            id_input.setText(edit_app_id)
            id_input.setEnabled(False)
        id_layout.addWidget(id_label, 1)
        id_layout.addWidget(id_input, 3)
        layout.addLayout(id_layout)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g., My Application")
        name_layout.addWidget(name_label, 1)
        name_layout.addWidget(name_input, 3)
        layout.addLayout(name_layout)
        
        # Path input
        path_layout = QHBoxLayout()
        path_label = QLabel("Installation Path:")
        path_input = QLineEdit()
        path_input.setPlaceholderText("C:\\path\\to\\app")
        path_browse_btn = QPushButton("Browse...")
        path_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        path_browse_btn.clicked.connect(lambda: self.browse_file(path_input, launch_input))
        path_layout.addWidget(path_label, 1)
        path_layout.addWidget(path_input, 4)
        path_layout.addWidget(path_browse_btn)
        layout.addLayout(path_layout)
        
        # Launch Script input
        launch_layout = QHBoxLayout()
        launch_label = QLabel("Launch Script:")
        launch_input = QLineEdit()
        launch_input.setPlaceholderText("start.bat or .exe filename")
        launch_browse_btn = QPushButton("Browse...")
        launch_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        launch_browse_btn.clicked.connect(lambda: self.browse_file(launch_input, path_input))
        launch_layout.addWidget(launch_label, 1)
        launch_layout.addWidget(launch_input, 4)
        launch_layout.addWidget(launch_browse_btn)
        layout.addLayout(launch_layout)
        
        # Update Script input
        update_layout = QHBoxLayout()
        update_label = QLabel("Update Script (optional):")
        update_input = QLineEdit()
        update_input.setPlaceholderText("update.bat or .exe filename")
        update_browse_btn = QPushButton("Browse...")
        update_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        update_browse_btn.clicked.connect(lambda: self.browse_file(update_input, path_input))
        update_layout.addWidget(update_label, 1)
        update_layout.addWidget(update_input, 4)
        update_layout.addWidget(update_browse_btn)
        layout.addLayout(update_layout)
        
        # Custom Logo Path input
        logo_layout = QHBoxLayout()
        logo_label = QLabel("Custom Logo (optional):")
        logo_input = QLineEdit()
        logo_input.setPlaceholderText("Path to .ico, .png, .jpg image")
        logo_browse_btn = QPushButton("Browse...")
        logo_browse_btn.setStyleSheet(self._get_button_style("#3d59a1"))
        logo_browse_btn.clicked.connect(lambda: self.browse_logo(logo_input))
        logo_layout.addWidget(logo_label, 1)
        logo_layout.addWidget(logo_input, 4)
        logo_layout.addWidget(logo_browse_btn)
        layout.addLayout(logo_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.save_app(
            dialog, id_input, name_input, path_input, launch_input, update_input, logo_input
        ))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Populate if editing
        if edit_app_id:
            self._populate_edit_dialog(
                edit_app_id, id_input, name_input, path_input, launch_input, update_input, logo_input
            )
        
        dialog.exec()
    
    def browse_file(self, path_input: QLineEdit, launch_input: QLineEdit):
        """Open file browser for scripts."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Script",
            path_input.text() or str(Path.home()),
            "Scripts (*.bat *.exe *.cmd);;All Files (*)"
        )
        if filename:
            # Auto-fill the other field based on context
            if launch_input.text() == "" and isinstance(path_input, QLineEdit):
                pass  # Don't auto-fill across fields to avoid confusion
            path_input.setText(filename)
    
    def browse_logo(self, logo_input: QLineEdit):
        """Open file browser for image files."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo Image",
            str(Path.home()),
            "Images (*.ico *.png *.jpg *.jpeg);;All Files (*)"
        )
        if filename:
            logo_input.setText(filename)
    
    def _populate_edit_dialog(self, app_id: str, id_input, name_input, path_input, launch_input, update_input, logo_input):
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
    
    def save_app(self, dialog, id_input, name_input, path_input, launch_input, update_input, logo_input):
        """Route to add or edit based on context."""
        if self.edit_app_id:
            self.save_app_edit(dialog, id_input, name_input, path_input, launch_input, update_input, logo_input)
        else:
            self.save_new_app(dialog, id_input, name_input, path_input, launch_input, update_input, logo_input)
    
    def save_new_app(self, dialog, id_input, name_input, path_input, launch_input, update_input, logo_input):
        """Validate and save new app to apps.json."""
        # Get values
        app_id = id_input.text().strip().lower().replace(" ", "_")
        name = name_input.text().strip()
        path = path_input.text().strip()
        launch_script = launch_input.text().strip()
        update_script = update_input.text().strip() or None
        logo_path = logo_input.text().strip() or None
        
        # Validation
        if not app_id:
            QMessageBox.warning(dialog, "Validation Error", "ID is required.")
            return
        if not name:
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
    
    def save_app_edit(self, dialog, id_input, name_input, path_input, launch_input, update_input, logo_input):
        """Validate and update existing app in apps.json."""
        # Get values
        app_id = self.edit_app_id  # ID cannot be changed
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
