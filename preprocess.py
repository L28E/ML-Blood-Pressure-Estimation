#!/usr/bin/env python3

import cmd
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

banner = """                                                                          
    ____  ________        ____  _________  ________  ______________  _____
   / __ \/ ___/ _ \______/ __ \/ ___/ __ \/ ___/ _ \/ ___/ ___/ __ \/ ___/
  / /_/ / /  /  __/_____/ /_/ / /  / /_/ / /__/  __(__  |__  ) /_/ / /    
 / .___/_/   \___/     / .___/_/   \____/\___/\___/____/____/\____/_/     
/_/                   /_/                                            

Proprietary command line tool/module for preparing ECG and PPG signals. Type "help" or "?" to list commands.                    
"""

help_text = """
-Start with the "load" command to load some data from a file
-Then, use the "select" command to choose a column from that data to manipulate
-Then, use filter functions or transforms to manipulate the signal
-You can plot the current signal with the "plot" command.

Documented commands (type help <command>):
"""          

data=None
column=None
signal=None

# ===============================================================================================================================
# HELPER FUNCTIONS, FILTERS, AND TRANSFORMS GO HERE
# ===============================================================================================================================

def _load(filename):
    "Loads the contents of the specified file into a numpy matrix" 
    
    #Lambda expression for the hex to int conversion
    convert = lambda x: int(x, 16) or 0
    
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
    
    return pd.read_csv(filename, delimiter=",", header=1,converters=converter_dict)    
    #return np.matrix(np.loadtxt(filename, dtype=int, delimiter=",",converters=converter_dict, skiprows=2))

# Here's a template for a filter
#    
# def _filter(signal):
#     "A description of the filter" 
#              
#     Some math changing the signal...
#     It's an array so it's gunna get passed by reference. That's fine though, the original signal is in the global data variable if we need it
#     By that same coin we don't really need to pass the variable but its better to be explicit, expicially if this function is going to be called from outside this file     
#    
#     return signal    
        


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
        """The start of the preprocessing workflow. Select the file which contains the data you want to process"""
        global data
        
        if arg=='':
            print("no file specfied")            
        elif not os.path.isfile(arg.strip("'")): 
            print("not a file")
        else:            
            data = _load(arg.strip("'"))
            print(data.columns) #TODO: pretty print this
            print("data loaded!")
         
        return 
      
    def do_select(self, arg):
        "The column you wish to manipulate. Makes a deep copy of the original so you are free to manipulate the signal while retaining a copy of the original."       
        global signal
                 
        #TODO: Should check if arg is an index to avoid errors
        if data is not None:
            # Make a true copy of the signal for manipulation        
            signal=np.copy(data[arg])
            print("signal selected!") 
        else:
            print("Please load data first")               
        
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
   
    def do_write(self, arg):
        "Writes the current signal to a file in a machine readable format"       
        if data is None:
            print("Please load data first")            
        elif signal is None:
            print("Please select a signal first")
        else:       
           #TODO: Implement this
            print("This command is not implemented yet") 
        return     
   
    def do_quit(self, arg):
        "Quit and exit the program"       
        return True
    
    def do_dump(self, arg):
        "A function for debugging. Temporarily removes the threshold on printing numpy objects so it prints the entirety of the current signal"      
        with np.printoptions(threshold=np.inf):
            print(signal)    
            
#   Here's a template for a CLI command
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
#           signal = _filter(signal) 
#        return              

def main():
    cli = PrePro_Cli()
    cli.cmdloop()

if __name__ == "__main__":
    main()