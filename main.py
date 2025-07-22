import argparse
import os
import sys
import datetime

from adb_utils import get_connected_devices, pull_location_db, discover_all_databases
from db_parser import parse_location_data
from location_analyzer import analyze_stops
from output_generator import generate_all_outputs, log_action

def setup_output_directory(output_dir):
    """Creates the output directory if it doesn't exist."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        log_action(f"Output directory '{output_dir}' ensured.")
        return True
    except OSError as e:
        log_action(f"Error: Could not create output directory '{output_dir}'. {e}")
        return False

def select_device(devices):
    """Let user select from multiple devices"""
    log_action(f"Multiple devices found: {devices}")
    print("\nMultiple devices detected. Please select one:")
    for i, dev_id in enumerate(devices):
        print(f"  {i+1}. {dev_id}")
    
    while True:
        try:
            choice = input("Enter device number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(devices):
                selected = devices[int(choice) - 1]
                log_action(f"User selected device: {selected}")
                return selected
        except KeyboardInterrupt:
            log_action("User cancelled device selection")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Android Location Timeline Extractor - Real-Device Edition",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-output_dir',
        type=str,
        required=True,
        help='Directory to save output files (timeline.csv, map.html, hashes.csv, action_log.txt).'
    )
    parser.add_argument(
        '--db_path',
        type=str,
        help='(Optional) Fallback path to a local database file if device extraction fails.'
    )

    args = parser.parse_args()
    
    # Initialize logging
    log_action("="*60)
    log_action("Android Location Timeline Extractor started")
    log_action(f"Version: 2.0 (Device-First Edition)")
    log_action(f"Command line: {' '.join(sys.argv)}")
    log_action("="*60)
    
    # Setup output directory
    if not setup_output_directory(args.output_dir):
        sys.exit(1)
    
    pulled_db_path = None
    
    # ALWAYS try device first (as per feedback)
    log_action("Starting device-first extraction process...")
    devices = get_connected_devices()
    
    if devices:
        log_action(f"Found {len(devices)} connected device(s)")
        
        # Select device
        if len(devices) == 1:
            selected_device_id = devices[0]
            log_action(f"Auto-selected single device: {selected_device_id}")
        else:
            selected_device_id = select_device(devices)
        
        # First, discover all possible databases
        log_action("Starting comprehensive database discovery...")
        discover_all_databases(selected_device_id)
        
        # Try to pull location database
        pulled_db_path = pull_location_db(selected_device_id, args.output_dir)
        
        if not pulled_db_path:
            log_action("Failed to pull database from device")
            if args.db_path:
                log_action(f"Falling back to provided --db_path: {args.db_path}")
                if os.path.exists(args.db_path):
                    pulled_db_path = args.db_path
                else:
                    log_action(f"Error: Fallback database not found at {args.db_path}")
                    sys.exit(1)
            else:
                log_action("No --db_path provided as fallback. Cannot proceed.")
                log_action("TIP: Use --db_path to specify a local database file as fallback")
                sys.exit(1)
    else:
        log_action("No ADB devices detected")
        if args.db_path:
            log_action(f"Using provided --db_path: {args.db_path}")
            if os.path.exists(args.db_path):
                pulled_db_path = args.db_path
            else:
                log_action(f"Error: Database not found at {args.db_path}")
                sys.exit(1)
        else:
            log_action("No devices found and no --db_path provided")
            log_action("Please connect an Android device with USB debugging enabled")
            log_action("Or provide --db_path for a local database file")
            sys.exit(1)
    
    if not pulled_db_path:
        log_action("Critical error: No database available for processing")
        sys.exit(1)
    
    log_action(f"Database ready for processing: {pulled_db_path}")
    log_action("-"*60)
    
    # Parse database
    log_action("Starting database parsing phase...")
    location_data = parse_location_data(pulled_db_path)
    
    if not location_data:
        log_action("Warning: No location data extracted from database")
        # Continue anyway to generate empty outputs
    else:
        log_action(f"Successfully extracted {len(location_data)} location points")
    
    # Analyze stops
    log_action("Starting location analysis phase...")
    stops = analyze_stops(location_data)
    log_action(f"Analysis complete: {len(stops)} stops identified")
    
    # Generate outputs
    log_action("Starting output generation phase...")
    generate_all_outputs(stops, args.output_dir)
    
    log_action("-"*60)
    log_action("Android Location Timeline Extractor completed successfully!")
    log_action(f"All outputs saved to: {os.path.abspath(args.output_dir)}")
    log_action("="*60)

if __name__ == '__main__':
    main()