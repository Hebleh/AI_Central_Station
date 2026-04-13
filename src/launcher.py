import subprocess
import os


def launch_app(path: str, launch_script: str):
    """Fire and forget - no tracking, no cleanup.
    
    Args:
        path: Installation directory for the app OR full path to executable
        launch_script: Script name to execute (ignored if path is a file)
    """
    if not path or not launch_script:
        print("Error: Both path and launch_script are required")
        return
    
    # Determine actual target and working directory
    # If path points directly to a file, use it as the target; otherwise join with script name
    if os.path.isfile(path):
        full_path = path
        cwd = os.path.dirname(path)
    else:
        full_path = os.path.join(path, launch_script)
        cwd = path
    
    if not os.path.exists(full_path):
        print(f"Script not found: {full_path}")
        return
    
    # Use Windows native startfile for batch files to open in new console window
    if full_path.lower().endswith('.bat'):
        os.startfile(full_path)
    else:
        subprocess.Popen(
            [full_path],
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


def run_update(path: str, update_script: str):
    """Fire and forget - same logic as launch_app.
    
    Args:
        path: Installation directory for the app OR full path to executable
        update_script: Script name to execute (ignored if path is a file)
    """
    if not path or not update_script:
        print("Error: Both path and update_script are required")
        return
    
    # Determine actual target and working directory
    # If path points directly to a file, use it as the target; otherwise join with script name
    if os.path.isfile(path):
        full_path = path
        cwd = os.path.dirname(path)
    else:
        full_path = os.path.join(path, update_script)
        cwd = path
    
    if not os.path.exists(full_path):
        print(f"Script not found: {full_path}")
        return
    
    # Same fire-and-forget logic as launch_app
    if full_path.lower().endswith('.bat'):
        os.startfile(full_path)
    else:
        subprocess.Popen(
            [full_path],
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )


def run_all_updates(apps_list):
    """Generate batch file and launch sequential updates for all apps with update scripts.
    
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
    
    # Generate temporary batch file in root directory
    batch_path = "temp_update_all.bat"
    
    try:
        with open(batch_path, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting updates for all apps...\n')
            f.write('echo Date: %date% %time%\n')
            f.write('echo ========================================\n\n')
            
            for app in apps_to_update:
                f.write(f'echo Updating: {app.name} ({app.id})\n')
                f.write(f'cd /d "{app.path}"\n')
                # Use 'call' so batch file continues after each script
                f.write(f'call "{app.update_script}"\n')
                f.write('echo ========================================\n\n')
            
            f.write('echo ========================================\n')
            f.write('echo All updates completed!\n')
            f.write('pause\n')
        
        # Launch batch file (fire-and-forget)
        os.startfile(batch_path)
        print(f"Launched update sequence for {len(apps_to_update)} apps via {batch_path}")
        
    except Exception as e:
        print(f"Error launching updates: {e}")
