import os

# --- Configuration File ---

# Get the absolute path of the project's root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Input Paths ---
# Path to the CSV file containing the list of earthquake events to process.
# This is used by the command-line `run.py` script.
EVENT_CSV_PATH = os.path.join(ROOT_DIR, 'events.csv')

# --- Directory Paths ---
# Directory where downloaded MiniSEED files are temporarily stored.
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')

# Main directory where all output files (plots, JSON) will be saved.
OUTPUT_DIR = os.path.join(ROOT_DIR, 'Output')


USE_FILTRE = True # this only use when commandline mode is used 

CUT_OFF_FREQ = 100 #set cutoff frequency to 100 hz low pass filter it uses 2nd order butterworth filtre
