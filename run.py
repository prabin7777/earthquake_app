import csv
import sys
from werkzeug.utils import secure_filename
import re

# Import the main analysis function and the configuration paths
from src.main import main as run_analysis
from config import EVENT_CSV_PATH , USE_FILTRE , CUT_OFF_FREQ, 

def run_from_command_line():
    """
    Reads events from the CSV file defined in config.py and runs the analysis for each one.
    """
    print("--- Starting Command-Line Analysis ---")
    
    try:
        with open(EVENT_CSV_PATH, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            events = list(reader)
    except FileNotFoundError:
        print(f"Error: The event CSV file was not found at the specified path: {EVENT_CSV_PATH}")
        print("Please make sure the path in config.py is correct and the file exists.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        sys.exit(1)

    if not events:
        print("No events found in the CSV file. Exiting.")
        return

    print(f"Found {len(events)} events to process from {EVENT_CSV_PATH}")
    
    success_count = 0
    failure_count = 0

    for i, event in enumerate(events):
        print(f"\n--- Processing Event {i+1} of {len(events)} ---")
        try:
            # Map the USGS-style headers to the application's expected keys
            event_name = re.sub(r'[^a-zA-Z0-9_]', '_', event.get("place", "cli_event"))
            sanitized_name = secure_filename(event_name)
            
            # Run the main analysis function, passing all the required parameters
            run_analysis(
                earthquake_name=sanitized_name,
                event_time=event['time'],
                latitude=float(event['latitude']),
                longitude=float(event['longitude']),
                magnitude=float(event['mag']),
                use_filter= USE_FILTRE # Default to using the filter
                cutoff_frequency= CUT_OFF_FREQ # Default cutoff frequency
            )
            success_count += 1
        except (KeyError, ValueError) as e:
            print(f"Error: Skipping event due to missing or invalid data in CSV row: {event}")
            print(f"Details: {e}")
            failure_count += 1
            continue
        except Exception as e:
            print(f"An unexpected error occurred while processing event {event.get('place')}: {e}")
            failure_count += 1
            continue
            
    print("\n--- Batch Processing Summary ---")
    print(f"Successfully processed: {success_count} events")
    print(f"Failed to process: {failure_count} events")
    print("---------------------------------")


if __name__ == "__main__":
    run_from_command_line()
