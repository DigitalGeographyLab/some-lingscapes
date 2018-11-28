#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script adds information about the users' location history to a DataFrame,
performing the join using the unique user identifiers provided in the column
"user_id".

Usage:
    Execute the script from the command line using the following command:

    python3 add_location_hist_to_df.py -i input.pkl -hi hist.pkl -o output.pkl

Arguments:
    -i/--input: Path to the DataFrame to which the location histories are added.
    -hi/--hist: Path to the DataFrame containing users' location histories.
    -o/--output: Path to the new DataFrame containing the input DataFrame and
                 the location histories.

Returns:
    A pandas DataFrame defined in the argument -o/--output.
"""

# Import the necessary packages
import argparse
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the DataFrame to which the location histories "
                     "will be added.")
ap.add_argument("-hi", "--hist", required=True,
                help="Path to the DataFrame containing the location histories.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the DataFrame to which the joined DataFrames"
                     "will be saved.")

# Parse arguments
args = vars(ap.parse_args())

# Load the DataFrame to which the location history will be added.
input_df = pd.read_pickle(args['input'])

# Load the DataFrame containing the location histories.
hist_df = pd.read_pickle(args['hist'])

# Join the input and location history DataFrames on column 'user_id', using the
# keys from the input DataFrame containing all posts. This results in NaN values
# for users that do not have a location history, which are dropped in the next
# step.
joined = pd.merge(input_df, hist_df, how='left', on='user_id')

# Drop the rows without location history.
joined = joined.dropna(subset=['prev-locations'])

# Save the resulting DataFrame to disk
joined.to_pickle(args['output'])

