# MLxBP

Capstone project. Our attempt at using machine learning to obtain a blood pressure estimate.

## `vital_signal_cli.py`
A command line interface for preparing signals for further analysis. Previously, we had all the underlying functions exposed so we could use this file as a module in other python scripts, but they've since been split into `signal_utils.py`, `preprocessing.py`, and `feature_extraction.py`. 

### `signal_utils.py`
Utilities and helper functions to prepare the signal  

### `preprocessing.py`
Functions which apply transformations to get more 'shapely' ECG and PPG signals

### `feature_extraction.py`
Functions which extract values to be used in ML analysis


# Dependencies:
* numpy, pandas, and scipy (for manipulating large data structures) 
* matplotlib (for visualization) 
* neurokit2 (for biosignal processing) 
* pywavelets (for wavelet based transformations) 
* antropy (for calculating entropy)

Install them all with `pip3 install numpy pandas scipy matplotlib neurokit2 PyWavelets antropy`
