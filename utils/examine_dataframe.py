# -*- coding: utf-8 -*-

"""
This script prints out the contents of a Pandas dataframe.

Required arguments:
    -df/--dataframe: Path to the dataframe to be printed.
    
Optional arguments:
    -f/--full: Print all contents in each cell. This optional argument is useful
               for examining the format of the data.
               
Returns:
    A printout of the dataframe contents.    
"""

import argparse
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-df", "--dataframe", required=True,
                help="Path to the DataFrame to be examined.")
ap.add_argument("-f", "--full", required=False, action='store_true',
                help="Select this option to print full columns.")

# Parse arguments
args = vars(ap.parse_args())

# Load dataframe
dataframe = pd.read_pickle(args["dataframe"])

# If requested, display full columns
if args["full"]:
    pd.set_option('display.max_colwidth', -1)

print(dataframe)

