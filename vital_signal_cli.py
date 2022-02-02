#!/usr/bin/env python3

import cmd
import os
import signal_utils
import feature_extraction
import preprocessing
from matplotlib import pyplot as plt

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

class PrePro_Cli(cmd.Cmd):
    intro = banner
    prompt = "pre-pro: "
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
            data = signal_utils._load(arg.strip("'"))
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

    def do_trim(self,arg):
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
            index=int(arg)            
            # Truncate the pandas dataframe
            data=signal_utils._manual_trim(data,index)            
                                    
            # If there is a signal selected, truncate the said signal too. 
            if signal is not None:                
                signal=signal[index:]     
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

    def do_lowpass(self, arg):
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
            y = preprocessing._lowpass(signal, int(args[0]), int(args[1]), int(args[2]), sample_rate)

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

    def do_sqi(self,arg):
        "Prints the signal quality index. Meant for ECG signals"
        print(signal_utils._sqi(signal,sample_rate))
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
        #cD1, cD2, cA = feature_extraction._decompose(signal)
        #yin = np.append(cA, cD1)
        #yin = np.append(yin, cD2)
        yin = feature_extraction._decompose(signal)
        print(yin)
        print(len(yin))
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

    def do_rr_interval(self,arg):
        "RR Interval of an ECG signal"
        print(feature_extraction._rr_interval(signal,sample_rate))

    def do_pat(self,arg):
        "pulse arrival time (between a PPG sys. peak and an ECG R peak)"
        print(feature_extraction._pulse_arrival_time(data,sample_rate,"Red"))
        return


#   Here's a template for a CLI command:
#
#   def do_filter(self, arg):
#        "help text"
#        global signal
#
#        if data is None:
#            print("Please load data first")
#        elif signal is None:
#            print("Please select a signal first")
#        else:
#           y = _filter(signal)
#           plt.plot(y)
#           plt.show()
#
#           if (input("Keep Changes? (y/n): ") == 'y'):
#               signal = y
#               print("changes applied")
#           else:
#               print("changes discarded")
#       return

def main():
    cli = PrePro_Cli()
    cli.cmdloop()


if __name__ == "__main__":
    main()