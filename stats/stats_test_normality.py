# -*- coding: utf-8 -*-

"""
This script was used to test whether the hourly observations follow a normal
distribution.

Usage:
    Execute the script from the command line using the following command:

    python3 stats_test_normality.py -df input.pkl

Arguments:
    -df/--dataframe: Path to the pandas DataFrame containing the data.

Output:
    Results for each hour printed on standard output.
"""

from scipy import stats
from supporting_functions import extract_timestamps, sort, \
    extract_hourly_activity
import argparse
import numpy as np
import pandas as pd


# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-df", "--dataframe", required=True,
                help="Path to the Pandas dataframe to be plotted.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
path_to_df = args['dataframe']

# Extract filename by splitting the directory and file format
fname = path_to_df.split('/')[-1].split('.')[0]

# Load dataframe
df = pd.read_pickle(path_to_df)

# Extract timestamps from the input DataFrame
post_times = extract_timestamps(df)

# Extract the date when the post was uploaded by applying a lambda function to
# the 'time_created_local' column, extracting the attribute date.
post_times['date'] = post_times.time_created_local.apply(lambda x: x.date())

# Exclude posts made outside certain period of time
weekdays = [1, 2, 3, 4, 5]
weekend = [0, 6]

# Use the .loc indexer to select rows whose month of posting is within the
# timeframe defined above.
post_times = post_times.loc[post_times.time_created_local.apply(lambda x: x.weekday()).isin(weekend)]

# Group the DataFrame rows according to the date the post was made, essentially
# creating a group for each day
dates = post_times.groupby('date')

# Collect hourly activity for each date
hours = extract_hourly_activity(dates)

# Sort the dictionary of posts
posts_per_hour = sort(hours)

# Generate a list of post counts for identifying the distribution
hourly_posts = [p for p in posts_per_hour.values()]
hourly_posts = np.array(hourly_posts)

# Loop over the observations for each hour
for h, hour in enumerate(hourly_posts):

    # Test whether the hourly sample comes from a normal distribution
    chi_squared, p_value = stats.normaltest(hour)

    # Check if p < 0.001
    if p_value < 1e-3:
        print("The sample for hour {} does not come from a normal "
              "distribution.".format(h))
    else:
        print("The sample for hour {} comes from a normal "
              "distribution.".format(h))
