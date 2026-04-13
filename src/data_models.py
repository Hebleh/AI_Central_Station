from pydantic import BaseModel
from typing import Optional


class App(BaseModel):
    """Pydantic model for app data from apps.json."""
    id: str
    name: str
    path: str
    launch_script: Optional[str] = None
    update_script: Optional[str] = None
    logo_path: Optional[str] = None  # Custom user-provided logo path (highest priority)
