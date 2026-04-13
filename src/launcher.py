import subprocess
import os
from typing import List


def launch_app(path: str, launch_script: str):
    """
    Launch an application using the provided script.
    
    Args:
        path: Directory or file path to the app
        launch_script: Name of the launch script (e.g., 'start.bat' or 'app.exe')
    """
    # Determine working directory and full script path
    if os.path.isfile(path):
        # Path is a file, use its directory as cwd
        cwd = os.path.dirname(path)
        full_path = launch_script if os.path.isabs(launch_script) else os.path.join(cwd, launch_script)
    else:
        # Path is a directory
        cwd = path
        full_path = launch_script if os.path.isabs(launch_script) else os.path.join(cwd, launch_script)
    
    # Fire-and-forget logic using Windows native methods
    if full_path.lower().endswith('.bat'):
        os.startfile(full_path)
    else:
        subprocess.Popen(
            [full_path],
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


def run_update(path: str, update_script: str):
    """
    Run an update script for an application.
    
    Args:
        path: Directory path to the app
        update_script: Name of the update script (e.g., 'update.bat')
    """
    full_path = update_script if os.path.isabs(update_script) else os.path.join(path, update_script)
    
    # Same fire-and-forget logic as launch_app
    if full_path.lower().endswith('.bat'):
        os.startfile(full_path)
    else:
        subprocess.Popen(
            [full_path],
            cwd=path,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


def run_all_updates(apps_list):
    """Generate batch file and launch sequential updates for all apps with update scripts.
    
    Uses manual progression: each step launches in a child terminal, then the parent
    waits for user keystroke before proceeding to next app. Final step auto-closes.
    
    Args:
        apps_list: List of App models from data/apps.json
    """
    # Filter apps that have valid update_script and path
    apps_to_update = [
        app for app in apps_list
        if app.update_script and app.path and app.update_script.strip()
    ]
    
    if not apps_to_update:
        print("No apps with update scripts configured.")
        return
    
    # Sort by update_order (lower = first, default 999 = last)
    sorted_apps = sorted(apps_to_update, key=lambda x: x.update_order)
    
    # Generate temporary batch file in root directory
    batch_path = "temp_update_all.bat"
    
    try:
        with open(batch_path, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting sequential updates for all apps...\n')
            f.write('echo Date: %date% %time%\n')
            f.write('echo ========================================\n\n')
            
            total_apps = len(sorted_apps)
            for idx, app in enumerate(sorted_apps):
                step_num = idx + 1
                # Log progress before launching
                f.write(f'echo [Step {step_num} of {total_apps}] Updating: {app.name}...\n')
                
                # Launch update in independent child terminal (no /wait)
                f.write(f'start "{app.name}" cmd /c "cd /d \"{app.path}\" && \"{app.update_script}\""\n')
                
                if idx == total_apps - 1:
                    # Final app: wait then auto-close
                    f.write('echo.\n')
                    f.write('echo [COMPLETE] All updates finished. Press any key to close...\n')
                    f.write('pause >nul\n')
                    f.write('exit\n')
                else:
                    # Wait for user to manually proceed to next update
                    f.write('echo.\n')
                    f.write('echo [WAITING] Press any key in THIS window when ready to proceed to the next update...\n')
                    f.write('pause >nul\n')
                
                f.write('echo ========================================\n\n')
            
            f.write('echo ========================================\n')
            f.write('echo All updates completed!\n')
        
        # Launch batch file (fire-and-forget)
        os.startfile(batch_path)
        print(f"Launched update sequence for {len(sorted_apps)} apps via {batch_path}")
        
    except Exception as e:
        print(f"Error launching updates: {e}")
