import antropy as ant
import scipy.stats as scst
from scipy import signal as sg
import pywt as wt
import numpy as np
import neurokit2 as nk

# ===============================================================================================================================
# FEATURE EXTRACTION
# ===============================================================================================================================

def _decompose(signal):
    "Getting the features for the ecg signal"
    signal = np.append(signal,signal)
    signal = sg.decimate(signal, 15)
    signal = sg.decimate(signal, 15)
    coeffs = wt.wavedec(signal, 'db8', level=0)

    #yin = np.append(coeffs[0],coeffs[2])
    #yin = np.append(yin,coeffs[1])
    return coeffs

def _sample_entropy(L):
    "Sample Entropy"
    return ant.sample_entropy(L)

def _skew(signal):
    "Calculate the skew of the signal"
    return scst.skew(signal)

def _kurt(signal):
    "Kurtosis of the signal"
    return scst.kurtosis(signal)

def _rr_interval(signal,fs):
    """Returns the average time difference between two peaks of the provided ECG signal.""" 
    # NOTE: The ppg_findpeaks method changed the values in the signal array!
    # Make a true copy, just to be safe.    
    peaks=nk.ecg_findpeaks(np.copy(signal),sampling_rate=fs,method="elgendi2010")["ECG_R_Peaks"]

    total=0
    for x in range(0,len(peaks)-2):
        diff=peaks[x+1]-peaks[x]
        total+=diff        

    temp=total/(len(peaks)-1)
    return temp/fs

def _pulse_arrival_time(data,fs,ppg_channel):
    """Returns the average number of samples between an ECG peak and the proceeding PPG peak
    Choose which ppg channel to use by giving the key of the channel in ppg_channel. 
    We can make this more robust with an enum later. Use 'Red' or 'IR'."""
    ecg_signal=np.copy(data["ECG"])
    ppg_signal=np.copy(data[ppg_channel])*-1 

    ecg_signal=nk.ecg_clean(ecg_signal, sampling_rate=fs, method="elgendi2010")
    ppg_signal=nk.ppg_clean(ppg_signal, sampling_rate=fs, method='elgendi')

    ecg_peaks = nk.ecg_findpeaks(np.copy(ecg_signal),sampling_rate=fs,method="elgendi2010")["ECG_R_Peaks"]
    ppg_peaks=nk.ppg_findpeaks(np.copy(ppg_signal),sampling_rate=fs,method="elgendi")["PPG_Peaks"] 

    total=0
    count=0
    y=0

    for x in range(0,len(ecg_peaks)-1):    
        while y<len(ppg_peaks):        
            if ppg_peaks[y] > ecg_peaks[x]:
                if ppg_peaks[y] < ecg_peaks[x+1]:
                    # ppg peak index is higher than the current ecg peak,
                    # and less than the next ecg peak. Update variables.
                    total+=ppg_peaks[y]-ecg_peaks[x]
                    count+=1
                    break
                else:
                    # ppg peak index is higher than the current ecg peak,
                    # but larger than the next ecg peak. Move on to the next ECG peak
                    break
            else:    
                # ppg peak index is lower than the current ecg peak. Try the next PPG peak
                y+=1

    # fig, (ax1, ax2) = plt.subplots(2, sharex=True)
    # fig.suptitle('ECG & PPG')
    # ax1.plot(ecg_signal)
    # ax2.plot(ppg_signal)       
    
    return (total/count)/fs
