# -*- coding: utf-8 -*-

"""
This script extracts information about where, when and for how long social media
users have been active, based on their location history. To do so, the script
requires a location history that has been reverse geocoded.
 
Usage:
    Execute the script from the command line using the following command:
    
    python3 extract_locations+activities.py -i input.pkl -o output.pkl
    
Arguments:
    -i/--input: Path to the DataFrame containing location histories in the
                column 'histories'.
    -o/--output: Path to the DataFrame in which the location and activity
                 information is stored.

Output:
    A pandas DataFrame containing the countries where the user has been active
    and for how long.
"""

import argparse
import datetime
import pandas as pd
from collections import defaultdict

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the pandas DataFrame with location histories.")

ap.add_argument("-o", "--output", required=True,
                help="Path to the output file.")

# Parse arguments
args = vars(ap.parse_args())

# Load dataframe
input_df = pd.read_pickle(args['input']).copy()

# Drop rows with no location history
input_df = input_df.dropna(subset=['history'])

# Check that the dataframe contains a column with location history
if 'history' not in input_df.columns:
    print("*** No user location history found ... quitting.")
    quit()

# Create a new DataFrame for storing information about location history
output_df = pd.DataFrame(index=input_df.index)

# Copy over user identifiers
output_df['user_id'] = input_df['user_id']

# Loop over the input dataframe
for ix, row in input_df.iterrows():

    # Set up dictionaries for countries visited and duration of stays
    visits = defaultdict(list)
    stays = {}

    # Loop over the entries
    for hist in row['history']:

        # Get the number of previous posts
        len_hist = len(hist)

        # Check that location history actually exists
        if len_hist > 0:

            # Loop over the history dictionary
            for k, v in hist.items():

                # Assign the first value into the variable country
                country = v[0]

                # Assign the key to the variable date and append the date to the
                # dictionary of visits (country: dates).
                date = k
                visits[country].append(date)

    # Loop over each visit
    for v in visits:

        # Subtract the earliest visit (min) from the newest (max)
        duration = max(visits[v]) - min(visits[v])

        # Convert duration to a human-readable form
        duration = datetime.timedelta(seconds=duration)

        # Append duration of stay to the dict (country: duration)
        stays[v] = duration

    # Collect information on activity spaces and durations. First check that
    # information on stays is available.
    if stays:

        # Retrieve the country with the longest stay
        longest = max(stays, key=stays.get)

        # Collect the duration of stays into a list
        delta_list = [s for s in stays.values()]

        # Use this list to calculate the average length of stay;
        # note that timedelta(0) is required for sum() to work.
        timedelta_avg = sum(delta_list, datetime.timedelta(0)) / len(delta_list)

        # Retrieve the country where the user has posted most frequently
        most_freq = max(visits, key=visits.get)

        # Assign the country names to columns
        output_df.at[ix, 'country-longest'] = longest
        output_df.at[ix, 'country-frequent'] = most_freq

        # Assign the length of stays to columns
        output_df.at[ix, 'activity-longest'] = stays[longest]
        output_df.at[ix, 'activity-avg'] = timedelta_avg

        # Add the total number of locations in the location history
        output_df.at[ix, 'prev-locations'] = len_hist

# Save output DataFrame to disk
output_df.to_pickle(args['output'])
