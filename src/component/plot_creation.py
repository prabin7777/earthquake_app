import os
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend for macos
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from obspy.taup import TauPyModel
import datetime

#Roundup datetime to nearest 30secmark
def round_upto_next_thiry_sec(dt):
    seconds = dt.second
    remainder = 30 - (seconds % 30) if seconds % 30 !=0 else 0
    rounded = dt + datetime.timedelta(seconds=remainder)
    return rounded.replace(microsecond=0)
    
    

def create_record_section_plot(traces_with_dist, output_dir, event_name, magnitude):
    """
    Creates a professional record section plot where each trace has its own subplot,
    arranged vertically and sorted by distance, with normalized amplitudes.
    """
    if not traces_with_dist:
        print("No traces to plot for record section.")
        return

    # Earthquake start time
    start_time = traces_with_dist[0][0].stats.starttime.datetime
    
    # Sort traces by distance from the epicenter
    traces_with_dist.sort(key=lambda x: x[1])
    
    num_traces = len(traces_with_dist)
    
    # Create a figure with one subplot for each trace
    fig, axes = plt.subplots(num_traces, 1, figsize=(16, 1.5 * num_traces), sharex=True)
    
    if num_traces == 1:
        axes = [axes]

    # Find the overall maximum amplitude across all traces to normalize them consistently
    max_global_amp = 0
    for tr, _ in traces_with_dist:
        current_max = np.max(np.abs(tr.data))
        if current_max > max_global_amp:
            max_global_amp = current_max

    # Plot each trace on its own subplot
    for i, (tr, dist_km) in enumerate(traces_with_dist):
        ax = axes[i] if num_traces > 1 else axes
        
        # Use matplotlib's date plotting capabilities for the time axis
        times = tr.times("matplotlib")
        
        # Normalize data by the global maximum amplitude
        normalized_data = tr.data / max_global_amp if max_global_amp > 0 else tr.data
        
        # Plot the normalized velocity data
        ax.plot(times, normalized_data, 'k-', lw=0.8)
        
        # Plot grid line on the graph for 30sec interval
        ax.grid(True, axis="x", which="major", linestyle='--', color='gray', alpha=0.25)
        
        # Fill the positive part of the waveform for better visibility
        # ax.fill_between(times, normalized_data, 0, where=(normalized_data > 0), color='black', interpolate=True)
        
        # Add a label to the y-axis for each trace with station info and distance
        # The label is positioned to the left of the plot area
        ax.text(-0.05, 0.5, f"{tr.stats.station}\n{dist_km:.1f} km", 
                transform=ax.transAxes, rotation=0, ha='right', va='center', fontsize=10)
        
        # Clean up the plot appearance
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        #ax.spines['bottom'].set_position(('outward', 5))
        # Code to remove extra x-axis line between the plots
        if i != num_traces - 1:
            ax.spines['bottom'].set_visible(False)
            ax.tick_params(bottom=False,labelbottom=False)


    # Set the main title for the entire figure
    fig.suptitle(f"Record Section for {event_name.replace('_', ' ')} (M{magnitude})", fontsize=22, y=1.0)
    
    # Set the shared y-axis label at the left
    fig.text(0.02,0.5,"Station Name\nDistance from Epicenter",va="center",ha="center", rotation="vertical", fontsize=16)
    
    # Set the shared x-axis label at the bottom
    axes[-1].set_xlabel("Time (UTC)", fontsize=16, labelpad=10)
    
    # Format the shared x-axis to show date and time nicely
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
    plt.setp(axes[-1].get_xticklabels(), rotation=45, ha="right", fontsize=12)
    
    # Set ticks strictly at 00 and 30 seconds only
    locator = mdates.SecondLocator(bysecond=[0, 30])
    axes[-1].xaxis.set_major_locator(locator)

    # Align x-axis start limit to the next 30-second boundary
    start_datetime = mdates.num2date(axes[-1].get_xlim()[0])
    rounded_start = round_upto_next_thiry_sec(start_datetime)
    rounded_start_mpl = mdates.date2num(rounded_start)
    
    # Only shift the start limit; keep the right limit unchanged
    current_xlim = axes[-1].get_xlim()
    axes[-1].set_xlim(left=rounded_start_mpl, right=current_xlim[1])

    # Adjust layout to prevent titles and labels from overlapping
    plt.tight_layout(rect=[0.05, 0.05, 1, 0.97]) # Adjust rect to make space for suptitle and labels

    # Save the combined plot to a single PDF file
    output_path = os.path.join(output_dir, f"{event_name}_record_section.pdf")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved record section plot to: {output_path}")


