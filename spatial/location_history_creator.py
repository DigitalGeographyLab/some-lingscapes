# -*- coding: utf-8 -*-
"""
This script collects location history per user into tuples containing UTC
timestamp and coordinates. This script should be run before reverse geocoding.

Usage:
    Execute the script from the command line using the following command:

    python3 reverse_geocode.py -i input.pkl -o output.pkl

Arguments:
    -i/--input: Path to the pandas DataFrame containing posts.
    -o/--output: Path to the output pandas DataFrame containing location
    histories.
    -c/--column: Name of the timestamp column

Output:
    A pandas DataFrame containing the location histories of users.
"""

import pandas as pd
import argparse

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the DataFrame containing geotagged posts.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the output dataframe with location history.")
ap.add_argument("-c", "--column", required=False,
                help="The name of the column containing the UTC timestamp")

# Parse arguments
args = vars(ap.parse_args())

# Check if DataFrame input column has been set manually
if args['column'] is not None:
    inputcol = args['column']
else:
    inputcol = 'time_created_utc'

# Assign arguments to variables
print('[INFO] - Reading pickled input dataframe in')
input_df = pd.read_pickle(args['input'])

# Retrieve original input dataframe columns
collist = list(input_df.columns)

# Create timestamp and location tuples
print('[INFO] - Creating time and coordinate tuples')
input_df['date_loc'] = None # create empty series
input_df['date_loc'] = input_df['date_loc'].astype(object) # force object dtype
for i, row in input_df.iterrows():
    input_df.at[i, 'date_loc'] = tuple([row[inputcol], row.geometry])

# input_df['date_loc'] = input_df[[inputcol,'geometry']].apply(tuple, axis=1)

# Group by user_id and create sorted location history
print('[INFO] - Grouping location history per user')
grp = input_df.groupby('user_id', as_index=False).agg(lambda x: list(x))
grp['location_hist'] = grp['date_loc'].apply(sorted)

# Merge dataframes on user_id
print('[INFO] - Joining location histories to user ids')
merged = pd.merge(input_df, grp, on='user_id', sort=False, suffixes=('', '_y'))

# Finalize column list for output
collist.extend(['location_hist'])

# Join location history series to dataframe by user_id
output_df = merged[collist]

# Save output dataframe as pickle
print('[INFO] - Saving output dataframe to pickle')
output_df.to_pickle(args['output'])
