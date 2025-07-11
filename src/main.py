import os
import sys
import json
from datetime import datetime
import argparse

# --- Setup Python Path ---
# This allows the script to find the 'config' module in the parent directory
# and the 'component' module in its own directory.
# This must be done before importing from other project modules.
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)

# --- Now, local imports will work correctly ---
from config import ASSETS_DIR, OUTPUT_DIR 
from component.download_handler import download_raspberry_data
from component.data_processing import process_seismic_data
from component.map_creation import create_shakemap
from component.plot_creation import create_record_section_plot
from component.metadata import fetch_station_inventory_and_metadata

def main(earthquake_name, event_time, latitude, longitude, magnitude, use_filter, cutoff_frequency):
    """
    Main orchestrator for the seismic data processing pipeline.
    This function is now called by both the web UI and the command-line runner.
    """
    # --- Configuration ---
    INPUT_DATA_DIR = os.path.join(ASSETS_DIR, earthquake_name)
    EVENT_OUTPUT_DIR = os.path.join(OUTPUT_DIR, earthquake_name)
    os.makedirs(INPUT_DATA_DIR, exist_ok=True)
    os.makedirs(EVENT_OUTPUT_DIR, exist_ok=True)

    # --- Step 1: Download Data (if not present) ---
    if not os.listdir(INPUT_DATA_DIR):
        print(f"No local data found for {earthquake_name}. Attempting to download...")
        try:
            event_time_dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            download_raspberry_data(
                event_name=earthquake_name,
                event_time=event_time_dt,
                delta_time=2,
                latitude=latitude,
                longitude=longitude,
                output_folder=INPUT_DATA_DIR
            )
        except Exception as e:
            print(f"Fatal: Data download failed for {earthquake_name}: {e}")
            return # Exit the function for this event, but allow the script to continue
    else:
        print(f"Local data found for {earthquake_name}. Skipping download.")

    # --- Step 2: Fetch Station Inventory and Metadata ---
    inventory, station_metadata = fetch_station_inventory_and_metadata(latitude, longitude)
    if not inventory or not station_metadata:
        print(f"Fatal: Could not fetch station data for {earthquake_name}. Exiting process for this event.")
        return

    # --- Step 3: Process Seismic Data ---
    corrected_traces, pgv_values, used_stations = process_seismic_data(
        folder_path=INPUT_DATA_DIR, 
        inventory=inventory, 
        station_metadata=station_metadata,
        use_filter=use_filter,
        cutoff_frequency=cutoff_frequency
    )
    if not corrected_traces:
        print(f"Fatal: No valid seismic traces could be processed for {earthquake_name}. Exiting process for this event.")
        return

    # --- Step 4: Create Visualizations ---
    print("\nCreating ShakeMap...")
    shakemap_path = os.path.join(EVENT_OUTPUT_DIR, f"{earthquake_name}_shakemap.pdf")
    create_shakemap(used_stations, pgv_values, latitude, longitude, magnitude, shakemap_path)

    print("\nCreating record section plot...")
    create_record_section_plot(corrected_traces, EVENT_OUTPUT_DIR, earthquake_name, magnitude)

    # --- Step 5: Save Event Details to JSON ---
    print("\nSaving event details to JSON...")
    event_details = {
        "name": earthquake_name,
        "time_utc": event_time,
        "latitude": latitude,
        "longitude": longitude,
        "magnitude": magnitude,
        "station_count": len(used_stations),
        "shakemap_file": os.path.basename(shakemap_path),
        "output_directory": EVENT_OUTPUT_DIR
    }
    json_path = os.path.join(EVENT_OUTPUT_DIR, 'event_details.json')
    with open(json_path, 'w') as f:
        json.dump(event_details, f, indent=4)
    
    print(f"\n--- Pipeline finished successfully for event: {earthquake_name} ---")

if __name__ == "__main__":
    # This block is only executed when main.py is called directly
    # by the web server's subprocess, which passes arguments.
    parser = argparse.ArgumentParser(description="Seismic Data Processing Pipeline (called by web server)")
    parser.add_argument('--earthquake_name', required=True, type=str)
    parser.add_argument('--event_time', required=True, type=str)
    parser.add_argument('--latitude', required=True, type=float)
    parser.add_argument('--longitude', required=True, type=float)
    parser.add_argument('--magnitude', required=True, type=float)
    parser.add_argument('--use_filter', action='store_true')
    parser.add_argument('--cutoff_frequency', type=float, default=10.0)
    
    args = parser.parse_args()
    
    main(
        earthquake_name=args.earthquake_name,
        event_time=args.event_time,
        latitude=args.latitude,
        longitude=args.longitude,
        magnitude=args.magnitude,
        use_filter=args.use_filter,
        cutoff_frequency=args.cutoff_frequency
    )
