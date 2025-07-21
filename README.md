# Android Location Timeline Extractor

## Overview
This Python application extracts location data from an Android device (or a provided SQLite database), analyzes movement patterns to identify "stops" (locations where the user stayed for a period of time), and generates multiple output formats including a CSV timeline, interactive map, and security hashes.

## Installation

### Prerequisites
- Python 3.8 or higher
- Android Debug Bridge (ADB) - only required if pulling from a real device

### Install Dependencies
```bash
pip install -r requirements.txt