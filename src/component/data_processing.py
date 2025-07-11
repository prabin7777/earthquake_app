
# --- src/component/data_processing.py ---
import os
import obspy
import numpy as np

def get_station_code_from_filename(filename):
    """Intelligently extracts the station code from various filename formats."""
    if filename.startswith('AM.'):
        return ".".join(filename.split('.')[:2])
    if '_' in filename:
        parts = filename.split('_')
        if len(parts) > 1:
            station_part = parts[1].split('.')[0]
            return f"AM.{station_part}"
    return None

def process_seismic_data(folder_path, inventory, station_metadata, use_filter, cutoff_frequency):
    """
    Processes MiniSEED files, performs instrument correction, applies optional filtering, and calculates PGV.
    """
    corrected_traces = []
    pgv_values = {}
    used_stations = {}

    for file in os.listdir(folder_path):
        if not file.lower().endswith(".mseed"):
            continue
        
        station_code = get_station_code_from_filename(file)
        if not station_code or station_code not in station_metadata:
            print(f"Warning: No metadata for station '{station_code}', skipping.")
            continue
            
        file_path = os.path.join(folder_path, file)
        try:
            st = obspy.read(file_path)
            st.merge(method=1, fill_value='latest')
            if not st: continue

            tr = st[0]
            
            # If we are using fallback stations, inventory will be None.
            # In this case, we cannot do a proper instrument correction.
            # We will simulate the velocity instead for visualization.
            if inventory:
                tr.remove_response(inventory=inventory, output="VEL")
                tr.data = tr.data * 100 # Convert to cm/s
            else:
                print(f"Warning: No inventory for {station_code}. Simulating velocity (NOT ACCURATE).")
                tr.data = tr.data / 1e6 # Arbitrary scaling for visualization

            if use_filter:
                tr.filter('lowpass', freq=cutoff_frequency, corners=2, zerophase=True)
            
            pgv = np.max(np.abs(tr.data))
            pgv_values[station_code] = pgv
            
            dist_km = station_metadata[station_code]['dist_km']
            corrected_traces.append((tr, dist_km))
            used_stations[station_code] = station_metadata[station_code]
            
            print(f"Processed {tr.id}, Dist: {dist_km:.1f} km, PGV: {pgv:.4f} cm/s")

        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue
            
    return corrected_traces, pgv_values, used_stations
