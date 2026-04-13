# AI Central Station

A lightweight, pure-Python local launcher and batch updater for open-source AI tools. Built to replace bloated Electron alternatives.

## Key Features

### Responsive Native UI
Fluid PyQt6 dark-mode grid that scales gracefully across screen sizes. Each app card displays:
- Dynamic logos (custom images, native .exe icons, or gradient squircles)
- One-click Launch and Update buttons
- Edit functionality for managing configurations
- 3-dot menu for quick folder access

### Dual-Sorting Architecture
Independent drag-and-drop sorting systems:
- **Visual Grid Sorting**: Reorder apps in the main grid layout without affecting update sequences
- **Update Sequence Sorting**: Configure execution order for batch updates (lower numbers run first)

### Smart Batching
Generates isolated `start /wait` processes to ensure clean sequential updates:
- Automatically identifies blocking processes (UI-launching updaters) and pushes them to the end of the queue
- Uses `/wait` flag for non-blocking apps to prevent race conditions
- Final app runs without `/wait` to hand terminal control to blocking UIs
- Temporary batch file generated in root directory with timestamped progress logging

## Getting Started

### Prerequisites
- Python 3.8+
- Windows OS (uses native `startfile` and subprocess management)

### Installation

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd AI_Central_Station
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Or use the batch launcher:**
   Double-click `Launch_Central_Station.bat` for a quick start.

### Configuration

Apps are managed via `data/apps.json`. Use the GUI to:
- Add new apps with installation paths, launch scripts, and optional update scripts
- Edit existing configurations
- Set custom logo images (stored in `assets/` folder)
- Configure update order for batch execution

## Architecture Philosophy

This project follows strict `.roorules` guidelines:

**No Background Threads**: All operations are fire-and-forget using Windows native subprocess management. No threading, no async/await complexity.

**No Heavy Abstractions**: Pure PyQt6 with minimal dependencies (PyQt6 + Pydantic). Direct `subprocess.Popen` calls with `CREATE_NEW_CONSOLE` flags.

**Pure Native Windows Subprocess Management**: Leverages Windows `startfile()` for batch files and `cmd /c` wrappers for sequential execution. No cross-platform abstractions that add bloat.

**JSON-Only Persistence**: Configuration stored in human-readable JSON (`data/apps.json`). No SQLite databases, no binary registries.

## Project Structure

```
AI_Central_Station/
├── main.py                 # Entry point with high-DPI scaling
├── Launch_Central_Station.bat  # Windows launcher shortcut
├── requirements.txt        # Dependencies (PyQt6, pydantic)
├── data/
│   ├── apps.json          # App configurations (gitignored)
│   └── apps.example.json  # Example configuration template
├── assets/                # Custom app logos (.png/.jpg)
└── src/
    ├── __init__.py
    ├── app_card.py        # Individual app card widget with gradient squircles
    ├── data_models.py     # Pydantic models for JSON validation
    ├── launcher.py        # Fire-and-forget subprocess management
    └── main_window.py     # Main UI with dual-sorting dialogs
```

## License

MIT License - Free to use and modify.
