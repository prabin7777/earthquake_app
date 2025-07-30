import os
import json
import requests

# Path to store latest event ID
LATEST_ID_PATH = "data/latest_event_id.txt"

# Fetch the most recent earthquake event from USGS
def fetch_latest_usgs_event():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "limit": 1,
        "orderby": "time"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data["features"][0]

# Check if the current event is new
def is_new_event(event_id):
    if os.path.exists(LATEST_ID_PATH):
        with open(LATEST_ID_PATH, "r") as f:
            saved_id = f.read().strip()
        return event_id != saved_id
    return True  # No previous ID found

# Save the latest event ID locally
def save_latest_event_id(event_id):
    os.makedirs(os.path.dirname(LATEST_ID_PATH), exist_ok=True)
    with open(LATEST_ID_PATH, "w") as f:
        f.write(event_id)

# Main logic to check and download if new event is found
def check_and_download_new_event(download_callback):
    try:
        latest_event = fetch_latest_usgs_event()
        event_id = latest_event["id"]
        if is_new_event(event_id):
            print(f"🟢 New earthquake detected: {event_id}")
            download_callback(event_id)  # your function to download based on event_id
            save_latest_event_id(event_id)
        else:
            print("🔁 No new earthquake event.")
    except Exception as e:
        print(f"❌ Error checking latest event: {e}")
