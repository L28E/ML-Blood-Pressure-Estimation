from pandas import read_csv
import numpy as np
import neurokit2 as nk

TIME_UNIT = 10 ** -3
CSV_HEADER_ROW = 13

# ===============================================================================================================================
# HELPER FUNCTIONS, FILTERS, AND TRANSFORMS GO HERE
# ===============================================================================================================================

def _load_txt(filename):
    "Loads the contents of the specified file into a numpy matrix"

    # Lambda expression for the hex to int conversion
    # TODO: add graceful error handling for when the converter fails due to incomplete entries
    convert = lambda x: int(x, 16)

    # A dictionary used to store the converters to apply for each column.
    # If we need to read from the files which are NOT hex coded, we could programmatically populate this dictionary based on the first row of the data file.
    # For now all the converters will be hex string to signed int.
    converter_dict = {
        'Time': convert,
        'Red': convert,
        'IR': convert,
        'Green': convert,
        'Ax': convert,
        'Ay': convert,
        'Az': convert,
        'ECG': convert,
        'ETI': convert
    }

    return read_csv(filename, delimiter=",", header=1, converters=converter_dict)

def _load_csv(filename):
    "Loads the contents of the specified csv into a numpy matrix."
   
    data = read_csv(filename, delimiter=",", header=CSV_HEADER_ROW) #Header in the csv files is the 16th row

    return data

def _get_sample_rate(data):
    "Calculates the sample rate from the time difference between samples."

    # Since the time entries are converted from hex on load, we'll just observe the difference between the first two time entries.
    period = (data['Time'][1] - data['Time'][0]) * TIME_UNIT
    return 1 / period

def _true_copy_arr(arr):
    "Makes a deep copy of a numpy array."
    return np.copy(arr)

def _interactive_trim(signal):
    "Interactively trim the dataset to remove erroneous data at the start"
    # The matplotlib.pyplot.ginput() method doesn't seem to be play nice when its time to close the figure. 
    # See https://github.com/matplotlib/matplotlib/issues/17109
    # For now we'll just have to trim it by manually specifying a sample. 
    return None
    
def _manual_trim(data,index):
    "Manually trim the dataset to by specifying an x co-ord. Sample to the left of that co-ord will be removed."    
    return data.truncate(before=index)

def _dump(signal):
    "A function for debugging. Temporarily removes the threshold on printing numpy objects so it prints the entirety of the current signal"
    with np.printoptions(threshold=np.inf):
        print(signal)

def _sqi(signal,fs):
    """Computes the signal quality index of an ECG signal. 
Used to determine the valididty of the signal after preprocessing and before feature extraction
Neurokit only has a mehtod for assessing ECG SQI, so will have to evaluate sqi and assume that the PPG is similarly good or poor"""
    sqi_arr=nk.ecg_quality(signal,sampling_rate=fs)

    total=0
    for x in sqi_arr:        
        total+=x        

    return total/(len(sqi_arr))