# -*- coding: utf-8 -*-

"""
This script describes the diversity of the data using Shannon entropy and uses
pandas regression plot to render the results for visual inspection.

Usage:
    Execute the script from the command line using the following command:

    python3 regplot_richness_vs_users.py -df input.pkl -ft 0.4 -ct 10 -b 1000

Arguments:
    -df/--dataframe: Path to the pandas DataFrame containing the data.
    -ft/--fthresh: fastText confidence threshold for including the data.
    -ct/--cthresh: Character length thredshold for including the data.
    -b/--n_boot: Number of bootstrapped samples to draw from the data.

Returns:
    The plot, saved into the file regplot_shan.pdf.
"""

from supporting_functions import diversity, extract_predictions
import argparse
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-df", "--dataframe", required=True,
                help="Path to the Pandas dataframe to be plotted.")

ap.add_argument("-ft", "--fthresh", required=False, type=float,
                help="fastText threshold for including data into the plot. "
                     "The value must be in range [0..1].")

ap.add_argument("-ct", "--cthresh", required=False, type=int,
                help="Character length threshold for including data into the "
                     "plot. The value must be an integer.")

ap.add_argument("-b", "--n_boot", required=True, type=int,
                help="Number of bootstrapped samples to draw from the data.")

# Initialize seaborn for prettier plots.
sns.set()

# Set seaborn style
sns.set_style("white", {'axes.grid': False})  # disable grid

# Set color palette to hls with 16 colours
palette = sns.color_palette("husl", 16)
sns.set_palette(palette)

# Parse arguments
args = vars(ap.parse_args())
n_boot = args['n_boot']

# Assign arguments to variables
path_to_df = args['dataframe']

# Check if a confidence thresholds has been provided for fastText
if args['fthresh']:

    # Assign threshold to variable
    ft = args['fthresh']

# Check if a character threshold has been provided for text length
if args['cthresh']:

    # Assign threshold to variable
    ct = args['cthresh']

# Load dataframe
input_df = pd.read_pickle(path_to_df)

# Extract predictions from the input DataFrame
posts = extract_predictions(input_df)

# If thresholds have been defined, drop the predictions below the threshold
if args['fthresh']:

    # Filter posts based on fastText prediction confidence
    posts = posts.loc[posts['probability'].apply(lambda x: float(x) >= ft)]

if args['cthresh']:

    # Filter posts based on character length
    posts = posts.loc[posts['char_len'].apply(lambda x: float(x) >= ct)]

# Print status
print("[INFO] Plotting a total of {} sentences ...".format(len(posts)))

# Set the timestamp indicating the time of creation to create a DateTimeIndex
posts.index = posts['time_created_local']

# Use the DateTimeIndex to group the posts according to their posting time, then
# apply the diversity measurement function to the 'language' column.
posts = posts.groupby(posts.index.date)['language']

# Count the number of unique languages and convert the result to a DataFrame;
# then generate a DateTimeIndex for the DataFrame.
data = posts.apply(lambda x:
                   diversity(x, 'shannon')).to_frame(name='Shannon')
data['Date'] = pd.to_datetime(data.index)

# Assign the day of observation into a column
data['Day'] = np.arange(0, len(data))

# Get day zero or the start of the observations. This will be used to convert
# the day ticks into dates, as seaborn does not support DateTime on x-axis
day_zero = data.iloc[0]['Date']

# Initialize figure and add subplot with 1 row, 1 column and 1 as identifier
fig = plt.figure(figsize=(6, 4))
ax = fig.add_subplot(1, 1, 1)

# Note that axis limits need to be set manually for seaborn
ax.set_xlim(0, len(data))

# Plot the data
sns.regplot(x=data['Day'], y=data['Shannon'], data=data, scatter=False,
            fit_reg=True, x_ci=99.9, order=3, n_boot=n_boot)

# Get the current list of ticks
ticks = ax.get_xticks().tolist()

# Map the ticks (floats) into integers
ticks = list(map(int, ticks))

# Define a dictionary for month names
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

# Get the first date in the dataframe (day zero); add a timedelta with the
# corresponding number of days to day zero to get tick date.
for i, t in enumerate(ticks):

    # Get the current addition to day zero
    addition = datetime.timedelta(t)

    # Fetch the time passed since day zero, which will be used as new tick value
    new_tick = (day_zero + addition)

    # Check tick month
    month = new_tick.month

    # Add year under month for each label
    ticks[i] = str(months[month]) + '\n' + str(new_tick.year)

# Set new ticks
ax.set_xticklabels(ticks)

# Set axis labels
plt.xlabel('Date', fontsize=13)  # Set x-axis label
plt.ylabel('Shannon entropy', fontsize=13)  # Set y-axis label

# Save the figure to PDF to the directory with the data
plt.savefig('regplot_shan.pdf', bbox_inches='tight')

# Show the plot
plt.show()

# Print status
print("[INFO] ... Done.")


