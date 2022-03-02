#!/usr/bin/env python3

import cmd
from distutils.log import error
import os
import tkinter as tk
from tkinter import filedialog

import numpy as np
import neurokit2 as nk
from matplotlib import pyplot as plt
from pandas import DataFrame, read_csv

import signal_utils
import feature_extraction
import preprocessing

banner = """                                                                          
       ___               __     __                     __         
\  / |  |   /\  |       /__` | / _` |\ |  /\  |       /  ` |    | 
 \/  |  |  /~~\ |___    .__/ | \__> | \| /~~\ |___    \__, |___ | 

Command line tool/module to process ECG and PPG signals for ML analysis. Type "help" or "?" to list commands.                    
"""

help_text = """
-Start with the "load" command to load some data from a file
-Then, use the "select" command to choose a column from that data to manipulate
-Then, use filter functions or transforms to manipulate the signal
-You can plot the current signal with the "plot" command.

Documented commands (type help <command>):
"""

data = None
column = None
signal = None
sample_rate = None


# ===============================================================================================================================
# CLI COMMANDS GO HERE
# ===============================================================================================================================

class vs_cli(cmd.Cmd):
    intro = banner
    prompt = "vs-cli: "
    file = None
    doc_header = help_text

    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_load(self, arg):
        "The start of the preprocessing workflow. Select the file which contains the data you want to process"
        global data
        global sample_rate

        if arg == '':
            print("No file specfied")
        elif not os.path.isfile(arg.strip("'")):
            print("Not a file")
        else:
            data = signal_utils._load_csv(arg.strip("'"))
            print(data.columns)  # TODO: pretty print this
            print("Data loaded!")
            sample_rate = signal_utils._get_sample_rate(data)
        return

    def do_select(self, arg):
        "Select the column you wish to manipulate. Makes a deep copy of the original so you are free to manipulate the signal while retaining a copy of the original."
        global signal

        # TODO: Should check if arg is an index to avoid errors
        if data is not None:
            # Make a true copy of the signal for manipulation
            signal = signal_utils._true_copy_arr(data[arg])
            print("Signal selected!")
        else:
            print("Please load data first")
        return

    def do_trim(self, arg):
        "Manually remove erroneous data from the start of the current signal AND the entire dataset"
        global data
        global signal

        if arg == '':
            print("No index specfied")
        elif int(arg) <= 0:
            print("Expected non-zero positive integer")
        elif data is None:
            print("Please load data first")
        else:
            index = int(arg)
            # Truncate the pandas dataframe
            data = signal_utils._manual_trim(data, index)

            # If there is a signal selected, truncate the said signal too.
            if signal is not None:
                signal = signal[index:]
            print("Done.")
        return

    def do_plot(self, arg):
        "Plot the current signal"
        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            plt.plot(signal)
            plt.show()
        return

    def do_showfs(self, arg):
        "Display the sampling frequency"
        if data is None:
            print("Please load data first")
        else:
            print(sample_rate)
        return

    def do_cheby(self, arg):
        """Apply a (Chebyshev II) lowpass filter with the specified parameters.
usage: lowpass \x1B[3mFILTER_ORDER\x1B[0m \x1B[3mSTOP_BAND_ATTENUATION\x1B[0m \x1B[3mCORNER_FREQUENCY\x1B[0m
ex: lowpass 30 40 20"""
        global signal

        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            args = arg.split()
            y = preprocessing._cheby(signal, int(args[0]), int(args[1]), int(args[2]), sample_rate)

            plt.plot(y)
            plt.show()

            if (input("Keep Changes? (y/n): ") == 'y'):
                signal = y
                print("changes applied")
            else:
                print("changes discarded")
        return

    def do_cleanecg(self, arg):
        "Uses neurokit2 to clean an ECG signal with the Elgendi method"
        global signal

        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            y = preprocessing._cleanECG(signal, sample_rate)

            plt.plot(y)
            plt.show()

            if (input("Keep Changes? (y/n): ") == 'y'):
                signal = y
                print("changes applied")
            else:
                print("changes discarded")
        return

    def do_cleanppg(self, arg):
        "Uses neurokit2 to clean a PPG signal with the Elgendi method"
        global signal

        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            y = preprocessing._cleanPPG(signal, sample_rate)

            plt.plot(y)
            plt.show()

            if (input("Keep Changes? (y/n): ") == 'y'):
                signal = y
                print("changes applied")
            else:
                print("changes discarded")
        return

    def do_butter(self, arg):
        """Apply a Butterworth lowpass filter with the specified parameters.
usage: lowpass  \x1B[3mCORNER_FREQUENCY\x1B[0m
ex: butter 4"""
        global signal

        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            args = arg.split()
            y = preprocessing._butter(signal, int(args[0]), sample_rate)

            plt.plot(y)
            plt.show()

            if (input("Keep Changes? (y/n): ") == 'y'):
                signal = y
                print("changes applied")
            else:
                print("changes discarded")
        return

    def do_segment(self, arg):
        "Get individual heart beats"
        global signal

        alpha = signal_utils._seg(signal, sample_rate)
        num = len(alpha)
        kSQ = np.zeros([num, 1])
        pSQ = np.zeros([num, 1])
        lastvalue = 0

        for acc in range(1, num, 1):
            stnum = str(acc)
            signal = alpha[stnum]["Signal"]

            kSQI = signal_utils._kSQI(signal)
            kSQ[acc - 1] = kSQI
            pSQI = signal_utils._ecg_quality_pSQI(signal, sampling_rate=sample_rate)
            pSQ[acc - 1] = pSQI

            # print(f"kSQI:{kSQI}   pSQI:{pSQI}")

        # Getting the best 10 pulses
        for i in range(len(kSQ)):
            if int(kSQ[i]) > 6.0:
                if (kSQ[i + 1] > 6) & (kSQ[i + 2] > 6) & (kSQ[i + 2] > 6) & (kSQ[i + 3] > 6) & (kSQ[i + 4] > 6) & (
                        kSQ[i + 5] > 6) & (kSQ[i + 6] > 6) & (kSQ[i + 7] > 6) & (kSQ[i + 8] > 6) & (kSQ[i + 9] > 6):
                    lastvalue = i
                    break
        j = 0
        number = len(alpha["1"]["Signal"])
        tenpulse = np.zeros([number * 10, 1])
        # for j in range(1310):
        for ac2 in range(lastvalue + 1, lastvalue + 11, 1):
            sig = alpha[str(ac2)]["Signal"]
            for val in sig:
                tenpulse[j] = val
                j = j + 1

        # print(tenpulse)
        signal = tenpulse
        print(len(signal))
        return

    def do_write(self, arg):
        "Writes the current signal to a file in a machine readable format"
        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            # TODO: Implement this
            print("This command is not implemented yet")
        return

    def do_quit(self, arg):
        "Quit and exit the program"
        return True

    def do_dump(self, arg):
        "A function for debugging. Prints all the values in the current signal"
        signal_utils._dump(signal)

    def do_wavelet(self, arg):
        "Applies wavelet filtering to the signal"
        global signal

        if data is None:
            print("Please load data first")
        elif signal is None:
            print("Please select a signal first")
        else:
            y = preprocessing._wavelet(signal)
            plt.plot(y)
            plt.show()

            if (input("Keep Changes? (y/n): ") == 'y'):
                signal = y
                print("changes applied")
            else:
                print("changes discarded")
        return

    def do_decompose(self, arg):
        "Gets the morphological based features of a signal"
        yin = feature_extraction._decompose(signal)
        print(yin)
        return

    def do_entropy(self, arg):
        "Entropy based features"
        y = signal
        value = feature_extraction._sample_entropy(signal)
        print(value)
        return

    def do_skew(self, arg):
        "Calculate the skew of the signal"
        value = feature_extraction._skew(signal)
        print(value)
        return

    def do_kurt(self, arg):
        "Kurtosis of the signal"
        value = feature_extraction._kurt(signal)
        print(value)
        return

    def do_extract(self, arg):
        "extracts 'em all. First dialog is the directory with data, second dialog is the csv with measured bp."
        global data
        global sample_rate
        global signal

        num_err = 0
        num_ppg = 0
        num_ecg = 0
        num_missing = 0
        num_empty = 0

        args = arg.split(" ")

        if len(args) == 2:
            # Arguments provided
            csv_dir = args[0]
            bp_filepath = args[1]

            # Check that arg[0] is a valid directory
            if csv_dir == '':
                print("No path specfied. Using the current directory.")
                csv_dir = os.getcwd()
                return
            elif not os.path.isdir(csv_dir.strip("'")):
                print("Not a path")
                return

            # Check that arg[1] is a valid file
            if bp_filepath == '':
                print("No file specfied")
                return
            elif not os.path.isfile(bp_filepath.strip("'")):
                print("Not a file")
                return
        elif len(args) == 1:
            # No arguments or not enough arguments. Use graphical selection
            root = tk.Tk()
            root.withdraw()

            csv_dir = filedialog.askdirectory()
            bp_filepath = filedialog.askopenfilename()
        else:
            print("Wrong number of arguments")
            return

        # Open the spreadsheet with true blood pressure measurements
        bp_data = read_csv(bp_filepath.strip("'"), delimiter=",")

        # Create an output dataframe with every available feature, a column for systolic pressure, diastolic pressure, and signal type
        ecg_columns = ['Filename', 'SBP', 'DBP', 'REAL_HR', 'HR', 'HRV', 'RR', 'PAT',
                       'QRSd', 'PQ', 'QT', 'JT',
                       'AUCqrs_pos', 'AUCqrs_neg', 'AUCjt_pos', 'AUCjt_neg',
                       'ENT', 'SKEW', 'KURT',
                       'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12']
        ecg_dataframe = DataFrame(columns=ecg_columns)

        # TODO: ppg dataframe

        # For every file in the directory (Assuming a flat file hierarchy)
        dir_list = os.listdir(csv_dir)
        files = [f for f in dir_list if f.endswith(".csv")]

        for file in files:

            print("Now Extracting: " + file)

            # Try to load the CSV into a dataframe
            try:
                data = signal_utils._load_csv(os.path.join(csv_dir, file))
                sample_rate = signal_utils._get_sample_rate(data)

                # Get the real bp measurement
                real_values = bp_data[bp_data["Filename"].str.contains(file.strip(".csv"), regex=False)]

                # Check for validity. We'll see what checks we REALLY need when the automation breaks :)
                if data.empty:
                    print("Empty data file!")
                    num_empty += 1
                    continue
                elif real_values.empty:
                    print("No measured blood pressure found!")
                    num_missing += 1
                    continue

                    # Extract different features based on the signal type.
                if "ECG" in data.columns:
                    print("ECG data file")

                    # Clean both signals before proceeding
                    data["ECG"] = preprocessing._cleanECG(data["ECG"], sample_rate)
                    data["Red"] = preprocessing._cleanPPG(data["Red"], sample_rate)

                    # Temporary dataframe for holding features as they are calculated
                    temp_df = DataFrame(columns=ecg_columns)

                    # Get a few nice, consecutive pulses
                    segment_dict = signal_utils._seg(data["ECG"],
                                                     sample_rate)  # Spits out a dictionary with every ECG pulse
                    num_segments = len(segment_dict)

                    # Evaluate the quality of each ECG pulse using Kurtosis
                    kSQI_arr = np.zeros(num_segments)
                    for x in range(1, num_segments):
                        pulse = segment_dict[str(x)]["Signal"]
                        kSQI_arr[x - 1] = signal_utils._kSQI(pulse)

                    first_pulse = 0
                    # Get 10 consective (nice) pulses. Conceivably we could do this multiple times for each signal to increase the size of the data set.
                    for i in range(len(kSQI_arr) - 9):
                        if int(kSQI_arr[i]) > 6.0:
                            if (kSQI_arr[i + 1] > 6) & (kSQI_arr[i + 2] > 6) & (kSQI_arr[i + 2] > 6) & (
                                    kSQI_arr[i + 3] > 6) & (kSQI_arr[i + 4] > 6) & (kSQI_arr[i + 5] > 6) & (
                                    kSQI_arr[i + 6] > 6) & (kSQI_arr[i + 7] > 6) & (kSQI_arr[i + 8] > 6) & (
                                    kSQI_arr[i + 9] > 6):
                                first_pulse = i
                                last_pulse = first_pulse + 9
                                break
                    else:
                        print("No set of nice pulses in that one. Skipping...")
                        continue

                    # Get the first index of the first nice pulse, and the last index of the last nice pulse
                    start = segment_dict[str(first_pulse + 1)]["Index"].iloc[0]
                    end = segment_dict[str(last_pulse + 1)]["Index"].iloc[-1]

                    # Truncate the whole dataset to the size of those 10 pulses
                    data = data.truncate(before=start, after=end)
                    # data=data.reset_index()

                    # fig, (ax1, ax2) = plt.subplots(2, 1,sharex=True)
                    # ax1.plot(data["Time"],data["ECG"])
                    # ax2.plot(data["Time"],data["Red"])
                    # plt.show()

                    # Mark the various components of the ECG
                    [peaks, peak_times] = signal_utils._get_ecg_peaks(data["ECG"], data["Time"], sample_rate)
                    _, points = nk.ecg_delineate(data["ECG"], peaks, sampling_rate=sample_rate)

                    # Get features
                    temp_df.at[0, 'HR'] = feature_extraction._ecg_heart_rate(peak_times)
                    temp_df.at[0, 'HRV'] = feature_extraction._hrv(peak_times)
                    temp_df.at[0, 'RR'] = feature_extraction._rr_interval(peaks, sample_rate)
                    temp_df.at[0, 'PAT'] = feature_extraction._pulse_arrival_time(data, sample_rate, "Red")
                    temp_df.at[0, 'QRSd'] = feature_extraction._avg_time_interval(data["Time"], points["ECG_Q_Peaks"],
                                                                                  points["ECG_S_Peaks"])
                    temp_df.at[0, 'PQ'] = feature_extraction._avg_time_interval(data["Time"], points["ECG_P_Onsets"],
                                                                                points["ECG_Q_Peaks"])
                    temp_df.at[0, 'QT'] = feature_extraction._avg_time_interval(data["Time"], points["ECG_Q_Peaks"],
                                                                                points["ECG_T_Offsets"])
                    temp_df.at[0, 'JT'] = feature_extraction._avg_time_interval(data["Time"], points["ECG_S_Peaks"],
                                                                                points["ECG_T_Peaks"])
                    temp_df.at[0, 'AUCqrs_pos'] = feature_extraction._avg_area_under_curve(
                        data["ECG"].clip(lower=0, upper=None), points["ECG_Q_Peaks"], points["ECG_S_Peaks"])
                    temp_df.at[0, 'AUCqrs_neg'] = feature_extraction._avg_area_under_curve(
                        data["ECG"].clip(lower=None, upper=0), points["ECG_Q_Peaks"], points["ECG_S_Peaks"])
                    temp_df.at[0, 'AUCjt_pos'] = feature_extraction._avg_area_under_curve(
                        data["ECG"].clip(lower=0, upper=None), points["ECG_S_Peaks"], points["ECG_T_Offsets"])
                    temp_df.at[0, 'AUCjt_neg'] = feature_extraction._avg_area_under_curve(
                        data["ECG"].clip(lower=None, upper=0), points["ECG_S_Peaks"], points["ECG_T_Offsets"])
                    temp_df.at[0, 'ENT'] = feature_extraction._sample_entropy(data["ECG"])
                    temp_df.at[0, 'SKEW'] = feature_extraction._skew(data["ECG"])
                    temp_df.at[0, 'KURT'] = feature_extraction._kurt(data["ECG"])

                    D = feature_extraction._decompose(data["ECG"])[0]
                    for x in range(1, 12):
                        temp_df.at[0, 'D' + str(x)] = D[x - 1]

                    # Add the filename and true blood pressure to the temporary dataframe
                    temp_df.at[0, 'Filename'] = file
                    temp_df.at[0, 'REAL_HR'] = real_values.get('Real_HR').item()
                    temp_df.at[0, 'SBP'] = real_values.get('SBP').item()
                    temp_df.at[0, 'DBP'] = real_values.get('DBP').item()

                    # Append to output dataframe
                    ecg_dataframe = ecg_dataframe.append(temp_df)
                    num_ecg += 1

                elif "Green" in data.columns or "GREEN" in data.columns:
                    print("PPG data file")

                    # TODO: Evaluate the ppg quality
                    # TODO: get ppg
                    num_ppg += 1
                    continue
                else:
                    print("Couldn't find an the expected columns")
                    continue
            except KeyError as e:
                # This happens when the time column cannot be found in the sample rate calculation.
                num_err += 1
                print(e)
            except ValueError as e:
                # This happens when there are duplicate entries in the blood pressure spreadsheet.
                num_err += 1
                print(e)
            except IndexError as e:
                num_err += 1
                print(e)
            except ZeroDivisionError as e:
                num_err += 1
                print(e)
            except KeyboardInterrupt:
                print("Got Keyboard interrupt, stopping")
                ecg_dataframe.to_csv("ecg_Features.csv")
                return

                # fig, (ax1, ax2) = plt.subplots(2, 1,sharex=True)
                # ax1.plot(data["Time"],data["ECG"])
                # ax2.plot(data["Time"],data["Red"])
                # plt.show()

        # Write the output dataframe to a csv
        ecg_dataframe.to_csv("ecg_Features.csv")

        # TODO write ppg dataframe

        print("\nnumber of errors: " + str(num_err))
        print("number of signals w/o blood pressure: " + str(num_missing))
        print("number of empty files: " + str(num_empty))
        print("number of ppg files: " + str(num_ppg))
        print("number of ecg files: " + str(num_ecg))

        return


def main():
    cli = vs_cli()
    cli.cmdloop()


if __name__ == "__main__":
    main()