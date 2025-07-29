import geopandas as gpd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
# Define the path to your local GeoJSON file.
# The script now expects 'district.geojson' to exist.
district_file = "district.geojson"

# Define the coordinates for Kathmandu.
kathmandu_coords = {
    'lon': 85.3240,
    'lat': 27.7172
}

# --- Main Script ---
try:
    # --- Step 1: Check if the file exists ---
    if not os.path.exists(district_file):
        raise FileNotFoundError(f"The required file '{district_file}' was not found in this directory.")

    # --- Step 2: Load the district data ---
    print(f"Attempting to load GeoJSON data from: {district_file}")
    nepal_data = gpd.read_file(district_file)
    print("District file loaded successfully!")

    # --- Step 3: Data Cleaning ---
    # Create a new, cleaned GeoDataFrame by dropping rows where 'geometry' is missing.
    nepal_data_cleaned = nepal_data.dropna(subset=['geometry'])
    
    if nepal_data_cleaned.empty:
        raise ValueError("Could not load any valid geographic data to plot from the file.")

    print(f"Plotting map with {len(nepal_data_cleaned)} districts.")

    # --- Step 4: Plotting Section ---
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # Plot the base map of districts (colorless)
    nepal_data_cleaned.plot(
        ax=ax,
        facecolor='white',  # Set the fill color to white
        edgecolor='black',  # Set the border color to black
        linewidth=0.5
    )

    # Plot the small triangle for Kathmandu
    ax.plot(
        kathmandu_coords['lon'], 
        kathmandu_coords['lat'],
        marker='^',          # Triangle marker
        color='red',         # Marker color
        markersize=10,       # Marker size
        label='Kathmandu'    # Label for the legend
    )
    
    # Customize the plot
    ax.set_title("Map of Nepal's Districts with Kathmandu Marked", fontdict={'fontsize': '18'})
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend() # Display the legend (shows 'Kathmandu')
    
    print("Displaying map...")
    plt.show()

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure you have the required packages: pip install geopandas matplotlib")

