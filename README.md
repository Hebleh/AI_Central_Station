# AI Central Station

A lightweight, bloat-free local launcher for open-source tools. My first ever project.

*disclosure: fully vibecoded*

## Features

- **Fire-and-Forget Launching**: Launch applications in native Windows console windows without blocking the UI.
- **Sequential Update Batching**: The "Update All" button generates a temporary batch file that sequentially runs all configured update scripts using `call` commands, ensuring each completes before the next begins.
- **Custom Logos**: Support for custom logo paths with automatic fallback to native .exe icon extraction, assets folder images, or colored text boxes.
- **Simple JSON Configuration**: All app data stored in a single `data/apps.json` file—no databases, no complexity.
- **More to come...

## Setup Instructions

1. **Clone and Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Apps**
   Copy the example configuration:
   ```bash
   copy data\apps.example.json data\apps.json
   ```
   Then edit `data/apps.json` with your actual application paths and scripts. Or add them using the UI itself.

3. **Run the Application**
   ```bash
   python main.py
   ```

## Architecture Philosophy

AI Central Station proudly embraces extreme simplicity by refusing to use:

- **No SQLite or Databases**: The entire state is managed through a single JSON file (`data/apps.json`). No database migrations, no WAL mode complexity, no connection pooling.
- **No psutil or Process Tracking**: We do not monitor running processes. Applications are launched and forgotten—Windows manages them natively.
- **No Background Threads**: The UI remains responsive by using Windows-native subprocess launching (`subprocess.Popen` with `CREATE_NEW_CONSOLE`) rather than Python threading or async/await complexity.

This project prioritizes direct execution over enterprise-level abstractions. Every feature is implemented with the minimum viable code required to work reliably on Windows.

## Project Structure

```
AI_Central_Station/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies (PyQt6, pydantic)
├── README.md              # This file
├── .gitignore             # Ignores data/apps.json and assets/
├── src/
│   ├── __init__.py
│   ├── main_window.py     # Main UI window with app cards grid
│   ├── app_card.py        # Individual card widget with logo logic
│   ├── launcher.py        # Fire-and-forget subprocess launching
│   └── data_models.py     # Pydantic model for JSON validation
├── data/
│   ├── apps.json          # Your configuration (git-ignored)
│   └── apps.example.json  # Example schema
└── assets/                # Optional logo images (contents git-ignored)
```

## License

MIT License - Simple, lightweight, and free to use.
