# ECG Feature Extraction

## vital_signal_cli.py
A command line interface for preparing signals for further analysis. Underlying functions are split into `signal_utils.py`, `preprocessing.py`, and `feature_extraction.py`. 

### signal_utils.py
Utilities and helper functions to prepare the signal  

### preprocessing.py
Functions which apply transformations to get more 'shapely' ECG and PPG signals

### feature_extraction.py
Functions which extract values to be used in ML analysis