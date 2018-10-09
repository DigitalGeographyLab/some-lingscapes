# -*- coding: utf-8 -*-

"""
This script was used to perform Levene's test and the Mann-Whitney U-test
between observations in a single DataFrame.

Usage:
    Execute the script from the command line using the following command:

    python3 stats_test_levene+mann_whitney.py -df input.pkl

Arguments:
    -df/--dataframe: Path to the pandas DataFrame containing the data.

Output:
    Results for Levene's test and the Mann-Whitney U-test printed on standard
    output.
"""


from supporting_functions import extract_timestamps, sort, extract_hourly_activity
from scipy.stats import levene, mannwhitneyu
import argparse
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

# Define the numbers of days for both weekdays and weekends. These correspond
# to the numbering in pandas.
weekdays = [1, 2, 3, 4, 5]
weekend = [0, 6]

# Use the .loc indexer to select rows whose month of posting is within the
# timeframe defined above.
posts_weekday = post_times.loc[post_times.time_created_local.apply(lambda x: x.weekday()).isin(weekdays)]
posts_weekend = post_times.loc[post_times.time_created_local.apply(lambda x: x.weekday()).isin(weekend)]

# Group the DataFrame rows according to the date the post was made, essentially
# creating a group for each day
weekday_dates = posts_weekday.groupby('date')
weekend_dates = posts_weekend.groupby('date')

# Create new dictionaries that hold the hourly post counts for both weekdays and
# weekends
weekday_hours = extract_hourly_activity(weekday_dates)
weekend_hours = extract_hourly_activity(weekend_dates)

# Sort the dictionary of posts
posts_per_hour_weekday = sort(weekday_hours)
posts_per_hour_weekend = sort(weekend_hours)

# Set up threshold for statistical significance and lists to hold the hours for
# which the difference is significant
p = 0.05
lev_diffs = []  # Levene's test
mwu_diffs = []  # Mann-Whitney U test

print("Results for Levene's test")

# Loop over the zipped values, use enumeration to fetch the hour
for h, (wd, we) in enumerate(zip(posts_per_hour_weekday.values(),
                                 posts_per_hour_weekend.values())):

    # Perform Levene's test to assess the variance of hourly observations
    W_stat, p_value_L = levene(wd, we, center='mean')

    # Print out the result, marking statistically significant differences using
    # an asterisk
    print(h, "{:.3f}".format(W_stat),
          ("{:.3f}".format(p_value_L) if p_value_L > p
           else "{:.3f}*".format(p_value_L)))

    # Append the hour to the list of hours, for which Levene's test returns a
    # statistically significant difference.
    if p_value_L < p:
        lev_diffs.append(h)

print("Results for Mann-Whitney U test")

# Loop over the zipped values, use enumeration to fetch the hour
for h, (wd, we) in enumerate(zip(posts_per_hour_weekday.values(),
                                 posts_per_hour_weekend.values())):

    # Perform Mann-Whitney U test ...
    U_stat, p_value_MWU = mannwhitneyu(wd, we, alternative='two-sided')

    # Append the hour to the list of hours, for which Levene's test returns a
    # statistically significant difference.
    if p_value_MWU < p:
        mwu_diffs.append(h)

    # Print out the result, marking statistically significant differences using
    # an asterisk
    print(h, "{:.3f}".format(U_stat),
          ("{:.3f}".format(p_value_MWU) if p_value_MWU > p
           else "{:.3f}*".format(p_value_MWU)))
