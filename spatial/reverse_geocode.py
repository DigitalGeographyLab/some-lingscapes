# -*- coding: utf-8 -*-

"""
This script performs reverse geocoding for post coordinates, fetching the name
of the administrative region to which the post is geotagged.

Usage:
    Execute the script from the command line using the following command:

    python3 reverse_geocode.py -i input.pkl -o output.pkl

Arguments:
    -i/--input: Path to the pandas DataFrame containing user location history.
    -o/--output: Path to the output pandas DataFrame containing reverse geocoded
                 location histories.

Output:
    A pandas DataFrame containing the reverse geocoded location histories.
"""

import argparse
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the DataFrame containing user location history.")
ap.add_argument("-o", "--output", required=True,
                help="Path to the output dataframe containing reverse geocoded "
                     "location histories for the users.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
input_df = pd.read_pickle(args['input'])

# Speed up the reverse geocoding by dropping duplicate user identifiers from the
# input dataframe. Retain the last entry, so the previous posts at the location
# are included in the location history.
input_df = input_df.drop_duplicates(subset='user_id', keep='last')

# Set up a new DataFrame to hold the location histories
output_df = pd.DataFrame(index=input_df.index)

# Copy over user identifiers
output_df['user_id'] = input_df['user_id']

# Load Shapefile from Natural Earth into a GeoDataFrame
countries = gpd.GeoDataFrame.from_file('shapef/ne_10m_admin_0_countries.shp')

# Get the input DataFrame length for counter
input_df_len = len(input_df)

# Loop over the input DataFrame to perform point-in-polygon queries
for i, (ix, row) in enumerate(input_df.iterrows(), start=1):
    print("[INFO] Processing row {}/{}...".format(i, input_df_len))
    history = {}

    try:
        # Loop over each entry in the 'Locations' column

        for entry in row['location_hist']:

            # Convert UNIX timestamp to UTC datetime
            date = entry[0]

            # Swap coordinate values and convert to Point for Shapely
            try:
                point = Point(tuple(reversed((entry[1].point.latitude,
                                             entry[1].point.longitude))))
            except AttributeError:
                pass

            # Perform the point-in-polygon query
            pip_query = countries.geometry.apply(lambda x: x.contains(point))

            # Get the index that returns True
            result_ix = pip_query[pip_query].index

            if len(result_ix) == 0:

                # If no index returns True, skip the entry
                pass

            else:
                # Fetch the country name
                country = str(countries['ADMIN'][result_ix].values[0])

                # Append result to list
                history[date] = country, point

        # Assign location history to the output dataframe
        output_df.at[ix, 'history'] = [history]

    except TypeError:
        pass

# Save output DataFrame to disk
output_df.to_pickle(args['output'])
