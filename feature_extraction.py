import antropy as ant
import scipy.stats as scst
from scipy import signal as sg
import pywt as wt
import numpy as np

# ===============================================================================================================================
# FEATURE EXTRACTION
# ===============================================================================================================================

def _decompose(signal):
    "Getting the features for the ecg signal"
    global coeffs
    signal = sg.decimate(signal, 10)
    signal = sg.decimate(signal, 2)
    coeffs = wt.wavedec(signal, 'db8', level=2)
    
    yin = np.append(coeffs[0],coeffs[2])
    yin = np.append(yin,coeffs[1])        
    return yin

def _sample_entropy(L):
    "Sample Entropy"
    return ant.sample_entropy(L)

def _skew(signal):
    "Calculate the skew of the signal"
    return scst.skew(signal)

def _kurt(signal):
    "Kurtosis of the signal"
    return scst.kurtosis(signal)

def _peak_interval(signal):
    """Returns the average number of samples between two peaks of the provided signal. 
Represents the RR interval for ECG signals, but can be used for PPG signals all the same."""


def _pulse_arrival_time(signal):
    "Returns the average number of samples between an ECG peak and the proceeding PPG peak"

