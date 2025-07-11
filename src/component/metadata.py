
# --- src/component/metadata.py ---
from obspy.clients.fdsn import Client as FDSNClient
from obspy.geodetics import gps2dist_azimuth

def fetch_station_inventory_and_metadata(epi_lat, epi_lon):
    """
    Fetches the inventory for AM network stations using a fixed geographic search,
    but requests response information for accurate data processing.
    """
    print("Fetching station inventory (including response) from FDSN...")
    inventory = None
    stations_metadata = {}
    try:
        client = FDSNClient("RASPISHAKE")
        # Using the fixed geographic search from the user's previous code,
        # but requesting level="response" to get the instrument gain.
        inventory = client.get_stations(
            network="AM",
            latitude=28.0,
            longitude=84.0,
            maxradius=2.5,
            level="response"
        )
        
        if not inventory:
            raise ValueError("No stations found within the search radius.")

        for network in inventory:
            for station in network:
                try:
                    # Check for valid coordinate data for each station before processing
                    if not (-90 <= station.latitude <= 90 and -180 <= station.longitude <= 180):
                        print(f"Warning: Skipping station {station.code} due to invalid coordinates provided by the server: lat={station.latitude}, lon={station.longitude}")
                        continue

                    # Calculate distance from the *actual* epicenter passed to the function
                    dist_m, _, _ = gps2dist_azimuth(station.latitude, station.longitude, epi_lat, epi_lon)
                    station_code = f"{network.code}.{station.code}"
                    stations_metadata[station_code] = {
                        "lat": station.latitude,
                        "lon": station.longitude,
                        "dist_km": dist_m / 1000
                    }
                except Exception as e:
                    # Catch any other unexpected errors for a single station
                    print(f"Warning: Could not process station {station.code}. Error: {e}. Skipping.")
                    continue
        
        print(f"Successfully processed metadata for {len(stations_metadata)} stations.")

    except Exception as e:
        # If the FDSN query fails for any reason, use the fallback stations
        print(f"Error fetching station metadata: {e}. Using fallback stations.")
        stations_metadata = {
            "AM.R0BD5": {"lat": 28.18, "lon": 83.60, "dist_km": gps2dist_azimuth(28.18, 83.60, epi_lat, epi_lon)[0] / 1000},
            "AM.R0CEA": {"lat": 28.23, "lon": 83.92, "dist_km": gps2dist_azimuth(28.23, 83.92, epi_lat, epi_lon)[0] / 1000}
        }
        # We don't have the full inventory for the fallback stations, so we return None for it.
        # The data processing step will need to handle this case.
        inventory = None

    return inventory, stations_metadata

