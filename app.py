import os
import sys
import json
import csv
import io
import re
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from datetime import datetime
import shutil

# --- Setup Python Path ---
# This allows the script to find modules in the 'src' directory and the main project directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))

# --- Imports ---
from main import main as run_analysis
from config import OUTPUT_DIR

# --- Initialization ---
app = Flask(__name__)
CORS(app)

# --- API Endpoints ---

@app.route('/')
def serve_index():
    """Serves the main index.html file."""
    return send_file(os.path.join(ROOT_DIR, 'index.html'))

@app.route('/batch_process', methods=['POST'])
def batch_process():
    """Handles batch processing of events from an uploaded JSON or CSV file."""
    if 'batch_file' not in request.files:
        return jsonify({"message": "No batch file part in the request"}), 400

    file = request.files['batch_file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
        
    use_filter = request.form.get('use_filter', 'true').lower() == 'true'
    cutoff_frequency = float(request.form.get('cutoff_frequency', 10.0))

    events = []
    try:
        content = file.read().decode('utf-8')
        if file.filename.endswith('.json'):
            events = json.loads(content).get("events", [])
        elif file.filename.endswith('.csv'):
            csvfile = io.StringIO(content, newline=None)
            reader = csv.DictReader(csvfile)
            for row in reader:
                events.append({
                    "event_time": row.get("time"),
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                    "magnitude": row.get("mag"),
                    "event_name": re.sub(r'[^a-zA-Z0-9_]', '_', row.get("place", "csv_event"))
                })
    except Exception as e:
        return jsonify({"message": f"Error parsing file: {e}"}), 400

    if not events:
        return jsonify({"message": "No valid events found in the uploaded file."}), 400

    success_count = 0
    failure_count = 0
    for event in events:
        try:
            sanitized_name = secure_filename(event['event_name'])
            run_analysis(
                earthquake_name=sanitized_name,
                event_time=event['event_time'],
                latitude=float(event['latitude']),
                longitude=float(event['longitude']),
                magnitude=float(event['magnitude']),
                use_filter=use_filter,
                cutoff_frequency=cutoff_frequency
            )
            success_count += 1
        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping invalid event in batch file: {event}. Error: {e}")
            failure_count += 1
            continue
    
    return jsonify({
        "message": f"Batch processing complete. Succeeded: {success_count}, Failed: {failure_count}."
    }), 200


@app.route('/download_raspberry', methods=['POST'])
def download_from_raspberry_shake():
    """Downloads data from Raspberry Shake FDSN and triggers analysis."""
    data = request.get_json()
    required_keys = ['event_name', 'event_time', 'latitude', 'longitude', 'magnitude']
    if not all(key in data for key in required_keys):
        return jsonify({"message": "Missing required event parameters."}), 400
    
    sanitized_name = secure_filename(data['event_name'])
    
    try:
        run_analysis(
            earthquake_name=sanitized_name,
            event_time=data['event_time'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            magnitude=data['magnitude'],
            use_filter=data.get('use_filter', True),
            cutoff_frequency=data.get('cutoff_frequency', 10.0)
        )
        return jsonify({"message": f"Data downloaded and analysis complete for {sanitized_name}."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500


@app.route('/get_events', methods=['GET'])
def get_processed_events():
    """Scans the Output directory and returns a list of processed events."""
    events = []
    if not os.path.exists(OUTPUT_DIR):
        return jsonify({"events": []})

    for event_name in os.listdir(OUTPUT_DIR):
        event_dir = os.path.join(OUTPUT_DIR, event_name)
        json_path = os.path.join(event_dir, 'event_details.json')
        if os.path.isdir(event_dir) and os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    event_data = json.load(f)
                    events.append({
                        "name": event_data.get("name"),
                        "time": event_data.get("time_utc"),
                        "magnitude": event_data.get("magnitude")
                    })
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Could not read or parse JSON for event {event_name}: {e}")
    
    events.sort(key=lambda x: x.get('time', ''), reverse=True)
    return jsonify({"events": events})


@app.route('/download/<event_name>/<file_type>', methods=['GET'])
def download_processed_file(event_name, file_type):
    """Serves the generated PDF files."""
    sanitized_event = secure_filename(event_name)
    
    filename_map = {
        'shakemap.pdf': f"{sanitized_event}_shakemap.pdf",
        'record_section.pdf': f"{sanitized_event}_record_section.pdf"
    }
    
    filename = filename_map.get(file_type)
    if not filename:
        return jsonify({"message": "Invalid file type requested."}), 400

    directory = os.path.join(OUTPUT_DIR, sanitized_event)
    
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
