# Android Location Timeline Extractor

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/android-location-timeline-extractor.git
cd android-location-timeline-extractor

# Install dependencies
pip install -r requirements.txt

# Create sample database for testing
python create_sample_db.py

# Run the extractor
python main.py -output_dir ./results --db_path ./sample_data/locations.db
