import sqlite3
import datetime
import sys
from output_generator import log_action

# Configuration
DB_TABLE_NAME = "locations"
TIMESTAMP_COLUMN = "timestamp"
LATITUDE_COLUMN = "latitude"
LONGITUDE_COLUMN = "longitude"

def analyze_database_schema(db_path):
    """Analyze database to find location-related tables and columns."""
    log_action(f"Analyzing database schema: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        log_action(f"Found {len(tables)} tables in database")
        
        location_tables = []
        
        for (table_name,) in tables:
            # Get columns for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Check if table has location-related columns
            has_timestamp = any('time' in col.lower() for col in column_names)
            has_lat = any('lat' in col.lower() for col in column_names)
            has_lon = any('lon' in col.lower() for col in column_names)
            
            if has_timestamp and has_lat and has_lon:
                location_tables.append((table_name, column_names))
                log_action(f"  ✓ Found location table: {table_name}")
                log_action(f"    Columns: {', '.join(column_names)}")
        
        conn.close()
        return location_tables
        
    except Exception as e:
        log_action(f"Error analyzing database: {e}")
        return []

def parse_location_data(db_path):
    """Extracts location data from the database."""
    log_action("Starting location data extraction")
    
    # First analyze the database
    location_tables = analyze_database_schema(db_path)
    
    if not location_tables:
        log_action("No location tables found using standard schema")
        log_action("Attempting to use default table configuration")
        location_tables = [(DB_TABLE_NAME, [TIMESTAMP_COLUMN, LATITUDE_COLUMN, LONGITUDE_COLUMN])]
    
    location_points = []
    seven_days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    seven_days_ago_ms = int(seven_days_ago.timestamp() * 1000)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for table_name, columns in location_tables:
            log_action(f"Attempting to extract from table: {table_name}")
            
            # Find the actual column names
            timestamp_col = next((col for col in columns if 'time' in col.lower()), TIMESTAMP_COLUMN)
            lat_col = next((col for col in columns if 'lat' in col.lower()), LATITUDE_COLUMN)
            lon_col = next((col for col in columns if 'lon' in col.lower()), LONGITUDE_COLUMN)
            
            try:
                query = f"SELECT {timestamp_col}, {lat_col}, {lon_col} FROM {table_name} WHERE {timestamp_col} >= ? ORDER BY {timestamp_col} ASC;"
                log_action(f"Executing query: {query}")
                
                cursor.execute(query, (seven_days_ago_ms,))
                rows = cursor.fetchall()
                
                log_action(f"Found {len(rows)} rows in {table_name}")
                
                for row in rows:
                    timestamp_val, lat, lon = row
                    
                    # Convert timestamp
                    if timestamp_val:
                        timestamp_dt = datetime.datetime.fromtimestamp(timestamp_val / 1000, tz=datetime.timezone.utc)
                        
                        if lat is not None and lon is not None:
                            location_points.append({
                                'timestamp': timestamp_dt,
                                'latitude': float(lat),
                                'longitude': float(lon)
                            })
                
            except sqlite3.Error as e:
                log_action(f"Error querying table {table_name}: {e}")
                continue
        
        conn.close()
        log_action(f"Total location points extracted: {len(location_points)}")
        return location_points
        
    except Exception as e:
        log_action(f"Critical error during parsing: {e}")
        return []