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
                
                if idx == total_apps - 1:
                    # LAST app: No /wait flag so parent can close and hand terminal to final blocking app
                    f.write(f'start "{app.name}" cmd /c "cd /d \"{app.path}\" && "{app.update_script}""\n')
                else:
                    # All other apps: Use /wait to block until child window closes, then proceed to next
                    f.write(f'start /wait "Updating {app.name}" cmd /c "cd /d \"{app.path}\" && "{app.update_script}""\n')
                
                f.write('echo ========================================\n\n')
            
            f.write('echo ========================================\n')
            f.write('echo All updates completed!\n')
            f.write('pause\n')
        
        # Launch batch file (fire-and-forget)
        os.startfile(batch_path)
        print(f"Launched update sequence for {len(sorted_apps)} apps via {batch_path}")
        
    except Exception as e:
        print(f"Error launching updates: {e}")
