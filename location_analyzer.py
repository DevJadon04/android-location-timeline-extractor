import datetime
import math
from typing import List, Dict, Tuple

# --- Constants ---
STOP_RADIUS_METERS = 50  # Group points within 50m
MIN_STOP_DURATION_MINUTES = 1  # Minimum time to consider a location a "stop"
MAX_TIME_GAP_MINUTES = 30  # Maximum time gap between points to consider them part of the same stop

# --- Helper Functions ---
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using Haversine formula.
    Returns distance in meters.
    """
    # Earth's radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def calculate_center_point(points: List[Dict]) -> Tuple[float, float]:
    """
    Calculate the average center point of a list of location points.
    Returns (latitude, longitude).
    """
    if not points:
        return 0.0, 0.0
    
    avg_lat = sum(p['latitude'] for p in points) / len(points)
    avg_lon = sum(p['longitude'] for p in points) / len(points)
    return avg_lat, avg_lon

# --- Core Analysis Function ---
def analyze_stops(location_points: List[Dict]) -> List[Dict]:
    """
    Analyzes location points and groups them into "stops".
    A stop is defined as staying within STOP_RADIUS_METERS for at least MIN_STOP_DURATION_MINUTES.
    
    Returns a list of stops, each containing:
    - arrival_time: datetime
    - departure_time: datetime
    - duration_minutes: int
    - latitude: float
    - longitude: float
    - point_count: int (number of location points in this stop)
    """
    if not location_points:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No location points to analyze.")
        return []
    
    # Sort by timestamp to ensure chronological order
    sorted_points = sorted(location_points, key=lambda x: x['timestamp'])
    
    stops = []
    current_stop_points = [sorted_points[0]]
    
    for i in range(1, len(sorted_points)):
        current_point = sorted_points[i]
        
        # Calculate time difference from last point
        time_diff = (current_point['timestamp'] - current_stop_points[-1]['timestamp']).total_seconds() / 60
        
        # Calculate distance from the center of current stop
        center_lat, center_lon = calculate_center_point(current_stop_points)
        distance = calculate_distance(
            center_lat, center_lon,
            current_point['latitude'], current_point['longitude']
        )
        
        # Check if this point belongs to the current stop
        if distance <= STOP_RADIUS_METERS and time_diff <= MAX_TIME_GAP_MINUTES:
            # Add to current stop
            current_stop_points.append(current_point)
        else:
            # Current stop has ended, process it
            if len(current_stop_points) >= 1:
                arrival_time = current_stop_points[0]['timestamp']
                departure_time = current_stop_points[-1]['timestamp']
                duration_minutes = (departure_time - arrival_time).total_seconds() / 60
                
                # Only record stops that meet minimum duration
                if duration_minutes >= MIN_STOP_DURATION_MINUTES:
                    center_lat, center_lon = calculate_center_point(current_stop_points)
                    stops.append({
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'duration_minutes': int(duration_minutes),
                        'latitude': round(center_lat, 6),
                        'longitude': round(center_lon, 6),
                        'point_count': len(current_stop_points)
                    })
            
            # Start new stop with current point
            current_stop_points = [current_point]
    
    # Don't forget to process the last stop
    if len(current_stop_points) >= 1:
        arrival_time = current_stop_points[0]['timestamp']
        departure_time = current_stop_points[-1]['timestamp']
        duration_minutes = (departure_time - arrival_time).total_seconds() / 60
        
        if duration_minutes >= MIN_STOP_DURATION_MINUTES:
            center_lat, center_lon = calculate_center_point(current_stop_points)
            stops.append({
                'arrival_time': arrival_time,
                'departure_time': departure_time,
                'duration_minutes': int(duration_minutes),
                'latitude': round(center_lat, 6),
                'longitude': round(center_lon, 6),
                'point_count': len(current_stop_points)
            })
    
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Analyzed {len(sorted_points)} location points and found {len(stops)} stops.")
    
    return stops