import subprocess
import os
import datetime

# --- Constants ---
COMMON_DB_PATHS = [
    "/data/data/com.google.android.gms/databases/locations.db",
    "/data/data/com.google.android.gms/databases/cache.db",
]

# --- Helper Functions ---
def _run_adb_command(command_parts):
    """
    Executes an ADB command and returns its output and error.
    Handles common ADB errors.
    """
    try:
        result = subprocess.run(
            ['adb'] + command_parts,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return "", "Error: ADB not found. Please ensure ADB is installed and in your system's PATH."
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else e.stdout.strip()
        return "", f"ADB Command Error: '{' '.join(e.cmd)}' failed with exit code {e.returncode}.\n{error_output}"
    except Exception as e:
        return "", f"An unexpected error occurred while running ADB command: {e}"

# --- Core ADB Functions ---
def get_connected_devices():
    """
    Lists all connected ADB devices.
    Returns a list of device IDs or an empty list if none.
    """
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for connected ADB devices...")
    stdout, stderr = _run_adb_command(['devices'])
    if stderr:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error checking devices: {stderr}")
        return []

    devices = []
    lines = stdout.splitlines()
    for line in lines[1:]:
        if '\tdevice' in line:
            device_id = line.split('\t')[0].strip()
            devices.append(device_id)
    
    if devices:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {len(devices)} device(s): {', '.join(devices)}")
    else:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No ADB devices found. Ensure device is connected and USB debugging is enabled.")
    return devices

def pull_location_db(device_id, local_output_path):
    """
    Attempts to pull the location database from the specified device.
    Returns the path to the pulled file on success, None on failure.
    """
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to pull location database from device '{device_id}'...")

    for remote_path in COMMON_DB_PATHS:
        filename = os.path.basename(remote_path)
        local_db_file = os.path.join(local_output_path, filename)

        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Trying to pull '{remote_path}' to '{local_db_file}'...")
        stdout, stderr = _run_adb_command(['-s', device_id, 'pull', remote_path, local_db_file])

        if "Permission denied" in stderr or "failed to stat" in stderr or "No such file or directory" in stderr:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Permission denied or path not found for '{remote_path}'. Error: {stderr.strip()}. Trying next path...")
            if os.path.exists(local_db_file):
                os.remove(local_db_file)
            continue
        elif stderr:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ADB pull error for '{remote_path}': {stderr.strip()}. Trying next path...")
            if os.path.exists(local_db_file):
                os.remove(local_db_file)
            continue
        elif stdout and "pulled" in stdout:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully pulled '{remote_path}' to '{local_db_file}'")
            return local_db_file

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to pull location database from device '{device_id}' using any common path.")
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TIP: If your phone is not rooted, you may need to use an emulator or a publicly available SQLite location DB.")
    return None