import neurokit2 as nk
import pywt as wt
from scipy import signal as sg
import numpy as np

# ===============================================================================================================================
# FILTERS AND TRANSFORMS
# ===============================================================================================================================

def _lowpass(signal, order, atten, corner, sample_rate):
    "Applies a lowpass filter of the specified paramaters to the provided signal"

    # Create the filter coeffs. For now we'll stick to a Chebyshev II, but we can change the filter or paramaterize it later if we need to.
    sos = sg.cheby2(order, atten, corner, btype='lowpass', analog=False, output='sos',
                    fs=sample_rate)  # use second-order sections to avoid numerical error

    # Apply the filter and return the output.
    return sg.sosfilt(sos, signal)


def _cleanECG(signal, sample_rate):
    "Uses neurokit2 to clean an ECG signal"
    return nk.ecg_clean(signal, sampling_rate=sample_rate, method="elgendi2010")


def _cleanPPG(signal, sample_rate):
    "Uses neurokit2 to clean a PPG signal. Also inverts signal to give Real PPG waveform"
    return nk.ppg_clean(signal, sampling_rate=sample_rate, method='elgendi')*(-1)


def _butter(signal, corner, sample_rate):
    "Applies a Butterworth lowpass filter of the specified paramaters to the provided signal. Also inverts signal to give Real PPG waveform"

    b, a = sg.butter(5, corner/(sample_rate/2), 'low')
    
    # Apply the filter and return the output.
    return sg.filtfilt(b, a, signal)*(-1)

def _wavelet(signal):
    "Uses pywavelets to apply wavelet filtering"
    wavelet = 'sym8'
    level = 1
    coeff = wt.wavedec(signal, wavelet, mode="per")
    sigma = (1 / 0.6745) * _madev(coeff[-level])
    uthresh = sigma * np.sqrt(2 * np.log(len(signal)))
    coeff[1:] = (wt.threshold(i, value=uthresh, mode='hard') for i in coeff[1:])
    return wt.waverec(coeff, wavelet, mode='per')


def _madev(d, axis=None):
    "Mean absolute deviation of a signal"
    return np.mean(np.absolute(d - np.mean(d, axis)), axis)

def _ampl_normalize(signal):
    """Normalizes the amplitude of the signal. There are too many variables which can 
effect the amplitude of the measured biometic readings, so we normalize them and only use features based on their morphopology."""
