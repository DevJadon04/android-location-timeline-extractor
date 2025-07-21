import argparse
import os
import sys
import datetime

from adb_utils import get_connected_devices, pull_location_db
from db_parser import parse_location_data, DB_TABLE_NAME, TIMESTAMP_COLUMN, LATITUDE_COLUMN, LONGITUDE_COLUMN
from location_analyzer import analyze_stops
from output_generator import generate_all_outputs, log_action

def setup_output_directory(output_dir):
    """Creates the output directory if it doesn't exist."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        log_action(f"Output directory '{output_dir}' ensured.")
    except OSError as e:
        log_action(f"Error: Could not create output directory '{output_dir}'. {e}")
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
        help='(Optional) Directly specify a local path to a location DB file if not pulling from device.'
    )
    parser.add_argument(
        '--device_id',
        type=str,
        help='(Optional) Specify device ID if multiple devices are connected.'
    )

    args = parser.parse_args()
    
    # Initialize action logging
    log_action("Android Location Timeline Extractor started")
    log_action(f"Command line arguments: {' '.join(sys.argv)}")
    
    output_dir = args.output_dir
    setup_output_directory(output_dir)

    pulled_db_path = None

    # Phase 1: Get the database
    if args.db_path:
        if not os.path.exists(args.db_path):
            log_action(f"Error: Specified DB path '{args.db_path}' does not exist.")
            sys.exit(1)
        pulled_db_path = args.db_path
        log_action(f"Using provided local DB path: '{pulled_db_path}'")
    else:
        devices = get_connected_devices()
        if not devices:
            log_action("No devices found to pull from. Please connect an ADB-enabled device or provide a --db_path.")
            sys.exit(1)

        selected_device_id = None
        if args.device_id:
            if args.device_id in devices:
                selected_device_id = args.device_id
            else:
                                log_action(f"Specified device ID '{args.device_id}' not found among connected devices.")
            sys.exit(1)
        elif len(devices) == 1:
            selected_device_id = devices[0]
        else:
            # Multiple devices - let user pick (Nice-to-have feature!)
            log_action("Multiple devices found. Please select one:")
            for i, dev_id in enumerate(devices):
                print(f"  {i+1}. {dev_id}")
            try:
                choice = input("Enter device number or ID: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(devices):
                    selected_device_id = devices[int(choice) - 1]
                elif choice in devices:
                    selected_device_id = choice
                else:
                    log_action("Invalid choice. Exiting.")
                    sys.exit(1)
            except KeyboardInterrupt:
                log_action("Operation cancelled by user.")
                sys.exit(1)

        if selected_device_id:
            pulled_db_path = pull_location_db(selected_device_id, output_dir)
            if not pulled_db_path:
                log_action(f"Failed to pull DB from '{selected_device_id}'.")
                sys.exit(1)

    log_action(f"Location database ready at: {pulled_db_path}")

    # Phase 2: Parse the database
    log_action("Starting database parsing...")
    log_action(f"DB Config: Table='{DB_TABLE_NAME}', Timestamp='{TIMESTAMP_COLUMN}', Lat='{LATITUDE_COLUMN}', Lon='{LONGITUDE_COLUMN}'")
    
    location_data = parse_location_data(pulled_db_path)
    if not location_data:
        log_action("No location data extracted or an error occurred during parsing.")
        sys.exit(1)
    
    log_action(f"Successfully parsed {len(location_data)} location points.")

    # Phase 3: Analyze stops
    log_action("Starting location analysis...")
    stops = analyze_stops(location_data)
    
    if not stops:
        log_action("No stops identified in the location data.")
        # Still generate outputs even with no stops for completeness
    else:
        log_action(f"Identified {len(stops)} stops from location data.")

    # Phase 4: Generate outputs
    log_action("Starting output generation...")
    generate_all_outputs(stops, output_dir)
    
    log_action("Android Location Timeline Extractor completed successfully!")
    log_action(f"All outputs saved to: {os.path.abspath(output_dir)}")

if __name__ == '__main__':
    main()