import sqlite3
import datetime
import sys

# --- Configuration for your specific DB ---
DB_TABLE_NAME = "locations"
TIMESTAMP_COLUMN = "timestamp"
LATITUDE_COLUMN = "latitude"
LONGITUDE_COLUMN = "longitude"

# --- Helper Functions ---
def convert_timestamp_to_datetime(timestamp_val):
    """
    Converts a timestamp value from the DB to a datetime object.
    Assumes timestamp is in milliseconds.
    """
    if timestamp_val is None:
        return None
    try:
        return datetime.datetime.fromtimestamp(timestamp_val / 1000, tz=datetime.timezone.utc)
    except (TypeError, ValueError):
        print(f"Warning: Could not convert timestamp value: {timestamp_val}. Returning None.", file=sys.stderr)
        return None

# --- Core DB Parsing Function ---
def parse_location_data(db_path):
    """
    Connects to the SQLite database, extracts location data,
    and filters for the last 7 days.
    Returns a list of dictionaries, each containing 'timestamp', 'latitude', 'longitude'.
    """
    location_points = []
    
    # Calculate the timestamp for 7 days ago
    seven_days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    seven_days_ago_ms = int(seven_days_ago.timestamp() * 1000)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

                # Check if the table exists
        cursor.execute(f"PRAGMA table_info({DB_TABLE_NAME});")
        if not cursor.fetchall():
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: Table '{DB_TABLE_NAME}' not found in database '{db_path}'.", file=sys.stderr)
            return []

        # Construct the SQL query
        query = f"SELECT {TIMESTAMP_COLUMN}, {LATITUDE_COLUMN}, {LONGITUDE_COLUMN} FROM {DB_TABLE_NAME} WHERE {TIMESTAMP_COLUMN} >= ? ORDER BY {TIMESTAMP_COLUMN} ASC;"
        
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Querying database for location data from last 7 days...")
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Filtering data from: {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        cursor.execute(query, (seven_days_ago_ms,))
        
        # Iterate through results and process
        for row in cursor:
            raw_timestamp, raw_latitude, raw_longitude = row
            
            # Your DB has regular decimal degrees (not E7), so no division needed
            latitude = raw_latitude
            longitude = raw_longitude
            
            # Convert timestamp
            timestamp_dt = convert_timestamp_to_datetime(raw_timestamp)

            if timestamp_dt and latitude is not None and longitude is not None:
                location_points.append({
                    'timestamp': timestamp_dt,
                    'latitude': latitude,
                    'longitude': longitude
                })
        
        conn.close()
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully extracted {len(location_points)} location points from '{db_path}'.")
        return location_points

    except sqlite3.Error as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SQLite Error: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] An unexpected error occurred during DB parsing: {e}", file=sys.stderr)
        return []