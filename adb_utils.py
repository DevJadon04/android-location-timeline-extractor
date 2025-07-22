import subprocess
import os
import datetime
from output_generator import log_action

COMMON_DB_PATHS = [
    "/data/data/com.google.android.gms/databases/locations.db",
    "/data/data/com.google.android.gms/databases/cache.db",
    "/data/data/com.google.android.apps.maps/databases/gmm_myplaces.db",
    "/data/data/com.google.android.apps.maps/databases/gmm_storage.db",
]

def _run_adb_command(command_parts):
    """Executes an ADB command and logs it."""
    cmd_str = ' '.join(['adb'] + command_parts)
    log_action(f"Executing: {cmd_str}")
    
    try:
        result = subprocess.run(
            ['adb'] + command_parts,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            log_action(f"Output: {result.stdout.strip()[:200]}{'...' if len(result.stdout.strip()) > 200 else ''}")
        if result.stderr:
            log_action(f"Error: {result.stderr.strip()}")
            
        return result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        error_msg = "ADB not found. Please install Android SDK Platform Tools."
        log_action(f"Error: {error_msg}")
        return "", error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        log_action(f"Error: {error_msg}")
        return "", error_msg

def get_connected_devices():
    """Lists all connected ADB devices."""
    log_action("Checking for connected ADB devices...")
    stdout, stderr = _run_adb_command(['devices'])
    
    if stderr and "not found" in stderr:
        return []
    
    devices = []
    lines = stdout.splitlines()
    
    for line in lines[1:]:  # Skip header
        if '\tdevice' in line:
            device_id = line.split('\t')[0].strip()
            devices.append(device_id)
            log_action(f"Found device: {device_id}")
    
    if not devices:
        log_action("No ADB devices found")
    
    return devices

def discover_all_databases(device_id):
    """Comprehensive database discovery on the device."""
    log_action(f"Starting comprehensive database discovery on device {device_id}")
    
    # First check if we have root access
    log_action("Checking device root access...")
    stdout, stderr = _run_adb_command(['-s', device_id, 'shell', 'su', '-c', 'id'])
    has_root = 'uid=0' in stdout
    log_action(f"Root access: {'Available' if has_root else 'Not available'}")
    
    # Try to list all databases
    log_action("Searching for all .db files in /data/data/...")
    
    if has_root:
        # If rooted, we can search everywhere
        cmd = ['shell', 'su', '-c', 'find /data/data -name "*.db" 2>/dev/null | head -20']
    else:
        # Without root, try accessible paths
        cmd = ['shell', 'find /sdcard /storage/emulated/0 -name "*.db" 2>/dev/null | head -20']
    
    stdout, stderr = _run_adb_command(['-s', device_id] + cmd)
    
    if stdout:
        db_files = stdout.splitlines()
        log_action(f"Found {len(db_files)} accessible database files:")
        for db in db_files[:10]:  # Log first 10
            log_action(f"  - {db}")
            
            # Try to identify if it has location data
            check_tables_cmd = f'sqlite3 {db} ".tables" 2>/dev/null'
            if has_root:
                tables_out, _ = _run_adb_command(['-s', device_id, 'shell', 'su', '-c', check_tables_cmd])
            else:
                tables_out, _ = _run_adb_command(['-s', device_id, 'shell', check_tables_cmd])
            
            if tables_out and any(keyword in tables_out.lower() for keyword in ['location', 'position', 'coordinate', 'latitude']):
                log_action(f"    ↳ Potential location database! Tables: {tables_out[:100]}")
    else:
        log_action("No accessible databases found or permission denied")
    
    # Always check standard paths
    log_action("Checking standard Google location paths...")
    for path in COMMON_DB_PATHS:
        if has_root:
            stdout, stderr = _run_adb_command(['-s', device_id, 'shell', 'su', '-c', f'ls -la {path}'])
        else:
            stdout, stderr = _run_adb_command(['-s', device_id, 'shell', f'ls -la {path}'])
        
        if 'No such file' not in stderr and 'Permission denied' not in stderr:
            log_action(f"  ✓ Found: {path}")
        else:
                        log_action(f"  ✗ Not accessible: {path}")

def pull_location_db(device_id, local_output_path):
    """Attempts to pull location database from device."""
    log_action(f"Starting database pull from device {device_id}")
    
    # Check if device has root
    stdout, stderr = _run_adb_command(['-s', device_id, 'shell', 'id'])
    has_root = 'uid=0(root)' in stdout
    log_action(f"Root access: {'Available' if has_root else 'Not available'}")
    
    # Try each known path
    for remote_path in COMMON_DB_PATHS:
        filename = os.path.basename(remote_path)
        local_db_file = os.path.join(local_output_path, filename)
        
        log_action(f"Attempting to pull: {remote_path}")
        
        # Since we have root on emulator, try direct pull first
        stdout, stderr = _run_adb_command(['-s', device_id, 'pull', remote_path, local_db_file])
        
        # Check if pull was successful (message might be in stdout OR stderr)
        if ('pulled' in stdout) or (stderr and 'file pulled' in stderr):
            log_action(f"✓ Successfully pulled {remote_path}")
            return local_db_file
        elif 'No such file' in stderr:
            log_action(f"✗ File doesn't exist: {remote_path}")
            if os.path.exists(local_db_file):
                os.remove(local_db_file)
        else:
            log_action(f"✗ Pull failed: {stderr.strip() if stderr else 'Unknown error'}")
            if os.path.exists(local_db_file):
                os.remove(local_db_file)
    
    log_action("Failed to pull any standard location database")
    log_action("Device may not have location history enabled or databases are empty")
    return None