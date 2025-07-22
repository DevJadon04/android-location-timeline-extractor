import csv
import hashlib
import os
import datetime
import folium
from folium.plugins import HeatMap
from typing import List, Dict

# Global action log
action_log = []

def log_action(message: str):
    """Add a timestamped message to the action log."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_entry = f"[{timestamp}] {message}"
    action_log.append(log_entry)
    print(log_entry)

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

def generate_timeline_csv(stops: List[Dict], output_dir: str) -> str:
    """Generate timeline.csv with stop information."""
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
        
        log_action(f"✓ Generated timeline.csv with {len(stops)} stops")
        return filepath
    except Exception as e:
        log_action(f"✗ Error generating timeline.csv: {e}")
        raise

def generate_map_html(stops: List[Dict], output_dir: str) -> str:
    """Generate interactive map with stops."""
    filepath = os.path.join(output_dir, "map.html")
    log_action("Generating map.html...")
    
    try:
        if stops:
            avg_lat = sum(stop['latitude'] for stop in stops) / len(stops)
            avg_lon = sum(stop['longitude'] for stop in stops) / len(stops)
        else:
            avg_lat, avg_lon = 37.7749, -122.4194
        
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        for i, stop in enumerate(stops):
            popup_text = f"""
            <b>Stop #{i+1}</b><br>
            Arrival: {stop['arrival_time'].strftime('%Y-%m-%d %H:%M')}<br>
            Departure: {stop['departure_time'].strftime('%Y-%m-%d %H:%M')}<br>
            Duration: {stop['duration_minutes']} minutes<br>
            Location points: {stop['point_count']}
            """
            
            if stop['duration_minutes'] < 30:
                color = 'green'
            elif stop['duration_minutes'] < 120:
                color = 'orange'
            else:
                color = 'red'
            
            folium.Marker(
                location=[stop['latitude'], stop['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"Stop #{i+1} ({stop['duration_minutes']} min)",
                icon=folium.Icon(color=color)
            ).add_to(m)
        
        # Add heatmap
        if stops:
            heat_data = [[stop['latitude'], stop['longitude'], stop['duration_minutes']] for stop in stops]
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
        
        m.save(filepath)
        log_action(f"✓ Generated map.html with {len(stops)} markers and heatmap")
        return filepath
    except Exception as e:
        log_action(f"✗ Error generating map.html: {e}")
        raise

def generate_hashes_csv(files_to_hash: List[str], output_dir: str) -> str:
    """Generate hashes.csv."""
    filepath = os.path.join(output_dir, "hashes.csv")
    log_action("Generating hashes.csv...")
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['filename', 'sha256_hash'])
            
            for file_path in files_to_hash:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    file_hash = calculate_file_hash(file_path)
                    writer.writerow([filename, file_hash])
                    log_action(f"  - {filename}: {file_hash[:16]}...")
        
        log_action("✓ Generated hashes.csv")
        return filepath
    except Exception as e:
        log_action(f"✗ Error generating hashes.csv: {e}")
        raise

def generate_action_log(output_dir: str) -> str:
    """Generate comprehensive action log."""
    filepath = os.path.join(output_dir, "action_log.txt")
    log_action("Generating action_log.txt...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Android Location Timeline Extractor - Detailed Action Log\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            for entry in action_log:
                f.write(entry + "\n")
            
            f.write(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Action log completed.")
        
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Generated action_log.txt")
        return filepath
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error generating action_log.txt: {e}")
        raise

def generate_all_outputs(stops: List[Dict], output_dir: str):
    """Generate all required output files."""
    log_action("="*50)
    log_action("Starting output file generation")
    log_action("="*50)
    
    timeline_path = generate_timeline_csv(stops, output_dir)
    map_path = generate_map_html(stops, output_dir)
    log_path = generate_action_log(output_dir)
    
    files_to_hash = [timeline_path, map_path, log_path]
    hashes_path = generate_hashes_csv(files_to_hash, output_dir)
    
    log_action("="*50)
    log_action("All output files generated successfully!")
    log_action(f"Output directory: {os.path.abspath(output_dir)}")
    log_action("="*50)