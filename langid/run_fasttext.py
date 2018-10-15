# -*- coding: utf-8 -*-

from supporting_functions import detect_ft
import argparse
import pandas as pd

"""
This script runs fastText language identification model on texts stored in a
pandas DataFrame.

Usage:
    Execute the script by running the following command:
    
    python3 run_fasttext.py -i input.pkl -o output.pkl -p 'rm_all'

Returns:
    A pandas DataFrame with fastText predictions in a column named 'langid'.
"""

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define the path to input file
ap.add_argument("-i", "--input", required=True,
                help="Path to the pandas DataFrame with the texts to process. "
                     "The texts are expected to be found in a column named "
                     "'text'.")

# Define the path to output file
ap.add_argument("-o", "--output", required=True,
                help="Path to the output file.")

# Define the preprocessing strategy
ap.add_argument("-p", "--preprocessing", required=True,
                help="Selected preprocessing strategy: valid values include "
                     "'no_preprocessing', 'rm_all' and 'rm_trail'.")

# Define input column manually
ap.add_argument("-c", "--column", required=False,
                help="The name of the column containing the texts to process.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
prep = args['preprocessing']

# Check if DataFrame input column has been set manually
if args['column'] is not None:
    inputcol = args['column']
else:
    inputcol = 'text'

# Initialize the fastText language identification model
try:
    import pyfasttext

# Catch the error thrown by missing module and provide additional instructions
except ImportError:
    exit("pyfasttext language identification module not found! "
         "Run pip install pyfasttext to install the module."
         )
# Load the input DataFrame
input_df = pd.read_pickle(args['input'])

# Perform language identification
input_df['langid'] = input_df[inputcol].apply(lambda x: detect_ft(x, prep))

# Save DataFrame to disk
input_df.to_pickle(args['output'])
