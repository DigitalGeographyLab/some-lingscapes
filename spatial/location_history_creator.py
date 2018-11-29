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
    -lt/--localtime: Specify whether local time column is added into
    dataframe. If local time is not required, don't use -lt flag.

Output:
    A pandas DataFrame containing the location histories of users.
"""

import pandas as pd
import argparse
import pytz

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the DataFrame containing geotagged posts.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the output dataframe with location history.")
ap.add_argument("-c", "--column", required=False,
                help="The name of the column containing the UTC timestamp")
ap.add_argument("-lt", "--localtime", required=False,
                help="Specify whether time_created_local column is created")


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

# Check whether local time zone was requested
if args['localtime'] is not None:
    print('[INFO] - Local time stamps requested!')
    # Convert the datetime in the column 'time_created_utc' to local time
    # (GMT+2). Begin by defining the source and target zones.
    from_zone = pytz.timezone('UTC')
    to_zone = pytz.timezone('Europe/Helsinki')  # change this to your timezone if needed
    print('[INFO] - Creating local time stamps...')
    # Loop over output dataframe
    for ix, row in output_df.iterrows():
        # Fetch the datetime
        time_created_utc = row['time_created_utc']

        # Tell the naive datetime that it's UTC
        time_created_utc = time_created_utc.replace(tzinfo=from_zone)

        # Convert the datetime to local timezone
        time_created_local = time_created_utc.astimezone(to_zone)

        # Add local time
        output_df.at[ix, 'time_created_local'] = time_created_local
else:
    print('[INFO] - No local time stamps requested, moving on...')
    pass

# Save output dataframe as pickle
print('[INFO] - Saving output dataframe to pickle')
output_df.to_pickle(args['output'])
print('[INFO] - ... Done!')
