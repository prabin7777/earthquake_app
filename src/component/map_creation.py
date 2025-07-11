
# --- src/component/map_creation.py ---
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def pgv_to_mmi(pgv_cms):
    """Converts PGV (in cm/s) to MMI (Modified Mercalli Intensity)."""
    if pgv_cms < 0.1: return 1
    if pgv_cms < 1.4: return 4
    if pgv_cms < 4.7: return 5
    if pgv_cms < 9.6: return 6
    if pgv_cms < 20: return 7
    if pgv_cms < 41: return 8
    if pgv_cms < 86: return 9
    return 10

def get_mmi_color(mmi):
    """Returns a color for a given MMI value based on USGS standards."""
    mmi_colors = {
        1: '#c0c0c0', 2: '#a0e6ff', 3: '#80ffff', 4: '#60ff80',
        5: '#ffff00', 6: '#ffc000', 7: '#ff8000', 8: '#ff0000',
        9: '#c00000', 10: '#800000'
    }
    return mmi_colors.get(int(mmi), '#ffffff')

def create_shakemap(stations, pgv_values, epi_lat, epi_lon, magnitude, output_pdf):
    """Creates a ShakeMap-style visualization."""
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.set_extent([80, 89, 26, 31], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.RIVERS)
    
    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    ax.plot(epi_lon, epi_lat, '*', markersize=20, markerfacecolor='yellow', markeredgecolor='black', label='Epicenter')

    for station_code, station_info in stations.items():
        pgv = pgv_values.get(station_code, 0)
        mmi = pgv_to_mmi(pgv)
        color = get_mmi_color(mmi)
        
        ax.plot(station_info['lon'], station_info['lat'], 'o',
                markersize=8, markerfacecolor=color, markeredgecolor='black',
                transform=ccrs.Geodetic())

    ax.set_title(f"ShakeMap for M{magnitude} Earthquake", fontsize=16)
    
    legend_elements = [plt.Rectangle((0, 0), 1, 1, color=get_mmi_color(i), label=f'MMI {i}') for i in range(4, 11)]
    ax.legend(handles=legend_elements, title="Modified Mercalli Intensity", loc='lower right', fontsize=10)

    plt.savefig(output_pdf)
    plt.close(fig)
    # --- FIX: Corrected variable name from output_path to output_pdf ---
    print(f"ShakeMap saved to {output_pdf}")
