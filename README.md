# Android Location Timeline Extractor

A forensic tool that extracts location history directly from Android devices via ADB, analyzes movement patterns, and generates comprehensive reports including a timeline, interactive map, and detailed action logs.

This version has been prioritize a **device-first extraction path** as its primary workflow, directly addressing the core requirement of the brief.

## Quick Start

### **Primary Method: Extract from a Connected Android Device**

This is the recommended and default method.

1.  **Clone & Install:**
    ```bash
    git clone https://github.com/DevJadon04/android-location-timeline-extractor.git
    cd android-location-timeline-extractor
    pip install -r requirements.txt
    ```
2.  **Connect Device:** Connect an Android device or start an emulator with USB Debugging enabled.
3.  **Verify Connection:**
    ```bash
    adb devices
    ```
4.  **Run the Extractor:**
    ```bash
    python main.py -output_dir ./results
    ```
    The tool will automatically discover and pull the most relevant location databases.

### **Fallback Method: Process a Local Database File**

Use this if you already have a database file or for testing purposes.

```bash
# First, create a sample database if you don't have one
python create_demo_data.py

# Run the extractor with the local file path
python main.py -output_dir ./results --db_path locations.db