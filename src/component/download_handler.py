# --- src/component/download_handler.py ---
import os
import requests
from datetime import timedelta

def get_nepal_stations():
    """Reads station codes for Nepal from a predefined list."""
    return [
        'R3C0B', 'RD7E6', 'RBBE5', 'R3E21', 'S2D97', 'R1F7C', 'R2C6D', 'R9D38', 'R51F6', 
        'R023E', 'R7173', 'R8C46', 'RBB7B', 'R61FA', 'R0BD5', 'R3B1E', 'RFCB2', 'R02C2', 
        'RC0D5', 'R1E1E', 'RD14A', 'R732B', 'RBCBE', 'RBE19', 'RB628', 'R2E9D', 'R1AA8', 
        'R8328', 'R9445', 'RF015', 'RDF62', 'R5A68', 'R8618', 'RCCCC', 'RC951', 'RDD5D', 
        'REB4C', 'R2109', 'R0920', 'R4051', 'RE2F2', 'R038D', 'REBA8', 'S8618', 'RA922', 
        'R0F23', 'RE3BA', 'RE93F', 'R2D97', 'R68E5', 'R0C4C', 'RED3D', 'R0638', 'RF542', 
        'R9299', 'R263A', 'R14FA', 'RA5AB', 'RD184', 'R3C3F', 'R2AE2', 'RFA80', 'R0CEA', 
        'RE497', 'R43A3', 'RD372', 'R20CE', 'R6EC4', 'R3005', 'R3DBE', 'R6F10', 'R6F2E'
    ]

def download_raspberry_data(event_name, event_time, delta_time, latitude, longitude, output_folder):
    """Downloads seismic data for all Nepal stations from FDSN Dataselect."""
    os.makedirs(output_folder, exist_ok=True)
    
    start_time = event_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (event_time + timedelta(minutes=3*delta_time)).strftime('%Y-%m-%dT%H:%M:%S')
    
    nepal_stations = get_nepal_stations()
    print(f"Querying data for {len(nepal_stations)} stations from {start_time} to {end_time}")

    for station in nepal_stations:
        url = f"https://data.raspberryshake.org/fdsnws/dataselect/1/query?network=AM&station={station}&channel=*Z&starttime={start_time}&endtime={end_time}"
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            if response.content:
                file_path = os.path.join(output_folder, f"AM.{station}.mseed")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded data for AM.{station}")
            else:
                print(f"No data available for AM.{station} in the given time window.")
        except requests.RequestException as e:
            print(f"Failed to download data for AM.{station}: {e}")
            continue
    print("Download process finished.")

