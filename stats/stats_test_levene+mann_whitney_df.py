from supporting_functions import extract_timestamps, sort, extract_hourly_activity
from scipy.stats import levene, mannwhitneyu
import argparse
import pandas as pd

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-df_1", "--dataframe_1", required=True,
                help="Path to the file with the first pandas DataFrame.")
# Define arguments
ap.add_argument("-df_2", "--dataframe_2", required=True,
                help="Path to the file with the first pandas DataFrame.")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
path_to_df_1 = args['dataframe_1']
path_to_df_2 = args['dataframe_2']

# Load dataframes
df_1 = pd.read_pickle(path_to_df_1)
df_2 = pd.read_pickle(path_to_df_2)

# Extract timestamps from the input DataFrames
post_times_1 = extract_timestamps(df_1)
post_times_2 = extract_timestamps(df_2)

# Extract the date when the post was uploaded by applying a lambda function to
# the 'time_created_local' column, extracting the attribute date.
post_times_1['date'] = post_times_1.time_created_local.apply(lambda x: x.date())
post_times_2['date'] = post_times_1.time_created_local.apply(lambda x: x.date())

# Group the DataFrame rows according to the date the post was made, essentially
# creating a group for each day
df_1_dates = post_times_1.groupby('date')
df_2_dates = post_times_2.groupby('date')

# Create new dictionaries that hold the hourly post counts for both weekdays and
# weekends
df_1_hours = extract_hourly_activity(df_1_dates)
df_2_hours = extract_hourly_activity(df_2_dates)

# Sort the dictionary of posts
posts_per_hour_df_1 = sort(df_1_hours)
posts_per_hour_df_2 = sort(df_2_hours)

# Set up threshold for statistical significance and lists to hold the hours for
# which the difference is significant
p = 0.05
lev_diffs = []  # Levene's test
mwu_diffs = []  # Mann-Whitney U test

print("Results for Levene's test")

# Loop over the zipped values, use enumeration to fetch the hour
for h, (wd, we) in enumerate(zip(posts_per_hour_df_1.values(),
                                 posts_per_hour_df_2.values())):

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
for h, (wd, we) in enumerate(zip(posts_per_hour_df_1.values(),
                                 posts_per_hour_df_2.values())):

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
