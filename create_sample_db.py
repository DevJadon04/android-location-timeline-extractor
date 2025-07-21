import sqlite3
import os
from datetime import datetime, timedelta
import random

os.makedirs("sample_data", exist_ok=True)


db_path = os.path.join("sample_data", "locations.db")


if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Existing {db_path} removed.")

# Connect to SQLite
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create locations table with schema matching Android's location database
c.execute('''
CREATE TABLE IF NOT EXISTS locations (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    accuracy INTEGER,
    altitude REAL,
    speed REAL,
    bearing REAL,
    provider TEXT
)
''')

# Helper function to generate timestamps
def get_timestamp(days_ago, hour, minute):
    """Generate a timestamp for a specific time in the past"""
    date = datetime.now() - timedelta(days=days_ago)
    date = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return int(date.timestamp() * 1000)  # Convert to milliseconds

# Sample location data representing various places in San Francisco Bay Area
# Format: (days_ago, hour, minute, latitude, longitude, accuracy, altitude, speed, bearing, provider)
location_data = [
    # Home location (morning, repeated pattern)
    (7, 8, 0, 37.7749, -122.4194, 10, 52.3, 0.0, 0.0, "gps"),
    (7, 8, 30, 37.7749, -122.4194, 12, 52.3, 0.0, 0.0, "network"),
    
    # Commute to work (driving)
    (7, 9, 0, 37.7751, -122.4180, 15, 48.1, 8.5, 45.0, "gps"),
    (7, 9, 15, 37.7805, -122.4121, 20, 35.2, 12.3, 65.0, "gps"),
    (7, 9, 30, 37.7858, -122.4064, 18, 28.5, 15.7, 85.0, "gps"),
    (7, 9, 45, 37.7901, -122.4012, 25, 22.1, 10.2, 90.0, "network"),
    
    # At office (Google HQ area)
    (7, 10, 0, 37.4220, -122.0841, 30, 15.0, 0.0, 0.0, "network"),
    (7, 12, 0, 37.4220, -122.0841, 35, 15.0, 0.0, 0.0, "network"),
    (7, 14, 0, 37.4220, -122.0841, 40, 15.0, 0.0, 0.0, "passive"),
    (7, 16, 0, 37.4220, -122.0841, 45, 15.0, 0.0, 0.0, "network"),
    
    # Lunch break (walking to nearby restaurant)
    (7, 12, 30, 37.4225, -122.0835, 10, 15.5, 1.2, 120.0, "gps"),
    (7, 12, 35, 37.4230, -122.0828, 12, 16.0, 1.5, 135.0, "gps"),
    (7, 13, 0, 37.4235, -122.0820, 15, 16.5, 0.0, 0.0, "gps"),
    
    # Weekend trip to Golden Gate Bridge
    (5, 10, 0, 37.8199, -122.4783, 8, 75.0, 0.0, 0.0, "gps"),
    (5, 10, 30, 37.8199, -122.4783, 10, 75.0, 0.0, 0.0, "gps"),
    (5, 11, 0, 37.8199, -122.4783, 12, 75.0, 0.0, 0.0, "network"),
    
    # Shopping at Union Square
    (4, 15, 0, 37.7879, -122.4075, 20, 45.0, 0.8, 180.0, "network"),
    (4, 15, 30, 37.7881, -122.4078, 25, 45.0, 0.5, 210.0, "network"),
    (4, 16, 0, 37.7885, -122.4082, 30, 45.0, 0.0, 0.0, "passive"),
    
    # Evening jog in the park
    (3, 18, 0, 37.7694, -122.4862, 10, 120.0, 2.5, 270.0, "gps"),
    (3, 18, 15, 37.7701, -122.4905, 12, 125.0, 3.2, 285.0, "gps"),
    (3, 18, 30, 37.7712, -122.4948, 15, 130.0, 2.8, 300.0, "gps"),
    (3, 18, 45, 37.7725, -122.4990, 18, 128.0, 2.1, 315.0, "gps"),
    
    # Recent locations (today and yesterday)
    (1, 9, 0, 37.7749, -122.4194, 10, 52.3, 0.0, 0.0, "gps"),
    (1, 12, 30, 37.7735, -122.4142, 15, 38.0, 0.0, 0.0, "network"),
    (1, 18, 0, 37.7749, -122.4194, 12, 52.3, 0.0, 0.0, "gps"),
    
    (0, 8, 0, 37.7749, -122.4194, 10, 52.3, 0.0, 0.0, "gps"),
    (0, 10, 30, 37.7805, -122.4090, 20, 30.0, 5.5, 45.0, "gps"),
    (0, 14, 0, 37.7820, -122.4015, 25, 25.0, 0.0, 0.0, "network"),
]

# Insert data into database
print("Inserting location data...")
for data in location_data:
    days_ago, hour, minute, lat, lon, acc, alt, speed, bearing, provider = data
    timestamp = get_timestamp(days_ago, hour, minute)
    
    c.execute('''
    INSERT INTO locations (timestamp, latitude, longitude, accuracy, altitude, speed, bearing, provider)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, lat, lon, acc, alt, speed, bearing, provider))

# Create an index on timestamp for faster queries
c.execute('CREATE INDEX idx_timestamp ON locations (timestamp)')

# Add some statistics
c.execute('SELECT COUNT(*) FROM locations')
total_records = c.fetchone()[0]

c.execute('SELECT MIN(timestamp), MAX(timestamp) FROM locations')
min_ts, max_ts = c.fetchone()

# Commit and close
conn.commit()
conn.close()

# Print summary
print(f"\n✅ SUCCESS! locations.db created at: {os.path.abspath(db_path)}")
print(f"📊 Database Statistics:")
print(f"   - Total records: {total_records}")
print(f"   - Date range: {datetime.fromtimestamp(min_ts/1000).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(max_ts/1000).strftime('%Y-%m-%d')}")
print(f"   - File size: {os.path.getsize(db_path):,} bytes")
print(f"\n📍 Location points include:")
print(f"   - Home location (repeated morning pattern)")
print(f"   - Commute routes with movement data")
print(f"   - Office locations throughout the day")
print(f"   - Weekend trips and activities")
print(f"   - Various accuracy levels and providers (gps/network/passive)")