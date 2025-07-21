import csv
import hashlib
import os
import datetime
import folium
from typing import List, Dict

# --- Action Log Management ---
action_log = []

def log_action(message: str):
    """Add a timestamped message to the action log."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    action_log.append(log_entry)
    print(log_entry)

# --- Helper Functions ---
def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        log_action(f"Error calculating hash for {filepath}: {e}")
        return "ERROR"

# --- Core Output Generation Functions ---
def generate_timeline_csv(stops: List[Dict], output_dir: str) -> str:
    """
    Generate timeline.csv with stop information.
    Returns the filepath of the generated file.
    """
    filepath = os.path.join(output_dir, "timeline.csv")
    log_action("Generating timeline.csv...")
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['arrival_time', 'departure_time', 'duration_minutes', 'latitude', 'longitude', 'point_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for stop in stops:
                writer.writerow({
                    'arrival_time': stop['arrival_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'departure_time': stop['departure_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'duration_minutes': stop['duration_minutes'],
                    'latitude': stop['latitude'],
                    'longitude': stop['longitude'],
                    'point_count': stop['point_count']
                })
        
        log_action(f"Successfully generated timeline.csv with {len(stops)} stops")
        return filepath
    except Exception as e:
        log_action(f"Error generating timeline.csv: {e}")
        raise

def generate_map_html(stops: List[Dict], output_dir: str) -> str:
    """
    Generate map.html with interactive map showing stops.
    Returns the filepath of the generated file.
    """
    filepath = os.path.join(output_dir, "map.html")
    log_action("Generating map.html...")
    
    try:
        # Create base map centered on the average of all stops
        if stops:
            avg_lat = sum(stop['latitude'] for stop in stops) / len(stops)
            avg_lon = sum(stop['longitude'] for stop in stops) / len(stops)
        else:
            # Default to San Francisco if no stops
            avg_lat, avg_lon = 37.7749, -122.4194
        
        # Create map
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        # Add markers for each stop
        for i, stop in enumerate(stops):
            # Create popup text with stop details
            popup_text = f"""
            <b>Stop #{i+1}</b><br>
            Arrival: {stop['arrival_time'].strftime('%Y-%m-%d %H:%M')}<br>
            Departure: {stop['departure_time'].strftime('%Y-%m-%d %H:%M')}<br>
            Duration: {stop['duration_minutes']} minutes<br>
            Location points: {stop['point_count']}
            """
            
            # Color code by duration
            if stop['duration_minutes'] < 30:
                color = 'green'
                icon = 'play'
            elif stop['duration_minutes'] < 120:
                color = 'orange'
                icon = 'pause'
            else:
                color = 'red'
                icon = 'stop'
            
            folium.Marker(
                location=[stop['latitude'], stop['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"Stop #{i+1} ({stop['duration_minutes']} min)",
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
        
        # Add a heatmap layer (Nice-to-have feature for bonus points!)
        from folium.plugins import HeatMap
        heat_data = [[stop['latitude'], stop['longitude'], stop['duration_minutes']] for stop in stops]
        if heat_data:
            HeatMap(heat_data, radius=15, blur=10, max_zoom=13).add_to(m)
        
        # Save map
        m.save(filepath)
        log_action(f"Successfully generated map.html with {len(stops)} markers")
        return filepath
    except Exception as e:
        log_action(f"Error generating map.html: {e}")
        raise

def generate_hashes_csv(files_to_hash: List[str], output_dir: str) -> str:
    """
    Generate hashes.csv with SHA-256 hashes of output files.
    Returns the filepath of the generated file.
    """
    filepath = os.path.join(output_dir, "hashes.csv")
    log_action("Generating hashes.csv...")
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['filename', 'sha256_hash']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for file_path in files_to_hash:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    file_hash = calculate_file_hash(file_path)
                    writer.writerow({
                        'filename': filename,
                        'sha256_hash': file_hash
                    })
                    log_action(f"Calculated hash for {filename}: {file_hash[:16]}...")
        
        log_action("Successfully generated hashes.csv")
        return filepath
    except Exception as e:
        log_action(f"Error generating hashes.csv: {e}")
        raise

def generate_action_log(output_dir: str) -> str:
    """
    Generate action_log.txt with all logged actions.
    Returns the filepath of the generated file.
    """
    filepath = os.path.join(output_dir, "action_log.txt")
    log_action("Generating action_log.txt...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Android Location Timeline Extractor - Action Log\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in action_log:
                f.write(entry + "\n")
            
            f.write(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Action log completed.")
        
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully generated action_log.txt")
        return filepath
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error generating action_log.txt: {e}")
        raise

def generate_all_outputs(stops: List[Dict], output_dir: str):
    """
    Generate all required output files.
    """
    log_action("Starting output generation...")
    
    # Generate timeline.csv
    timeline_path = generate_timeline_csv(stops, output_dir)
    
    # Generate map.html
    map_path = generate_map_html(stops, output_dir)
    
    # Generate action_log.txt (before hashes so it's included in hash calculation)
    log_path = generate_action_log(output_dir)
    
    # Generate hashes.csv for the other three files
    files_to_hash = [timeline_path, map_path, log_path]
    hashes_path = generate_hashes_csv(files_to_hash, output_dir)
    
    log_action("All output files generated successfully!")
    log_action(f"Output directory: {os.path.abspath(output_dir)}")