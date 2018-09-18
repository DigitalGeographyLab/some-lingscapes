from supporting_functions import extract_predictions
from scipy.stats import kruskal
import argparse
import pandas as pd
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


# Initialize seaborn for prettier plots.
sns.set()

# Set color palette to hls with 16 colours
palette = sns.color_palette("husl", 16)
sns.set_palette(palette)

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
path_to_df = args['dataframe']

if args['fthresh']:
    ft = args['fthresh']
if args['cthresh']:
    ct = args['cthresh']

# Load DataFrame
df = pd.read_pickle(path_to_df)

# Extract predictions from the input DataFrame
posts = extract_predictions(df)
len_orig = len(posts)

# Print status
print("[INFO] Extracted {} sentences from the captions.".format(len_orig))

# If thresholds have been defined, drop the predictions whose confidence is
# below the thresholds.
if args['fthresh']:
    posts = posts.loc[posts['probability'].apply(lambda x: float(x) >= ft)]

if args['cthresh']:
    posts = posts.loc[posts['char_len'].apply(lambda x: float(x) >= ct)]

# Print out statistics for data loss, if filtering has been applied
if len(posts) != len_orig:
    data_loss = (100 - (len(posts) / len_orig * 100))
    print("[INFO] Lost {:.2f}% of data due to filtering.".format(data_loss))

# Create a DateTimeIndex
posts.index = posts['time_created_local']

# Use pivot_table to take the individual languages from the column 'language'
# and use them as columns for a new DataFrame. The cells will be populated by
# the date of posting, which will be turned into integers in the next step.
languages = posts.pivot_table(values='time_created_local', index=posts.index,
                              columns='language', aggfunc='first')

# Take years 2014 and 2015
year_2014 = languages.ix['2014-01-01':'2014-12-31']
year_2015 = languages.ix['2015-01-01':'2016-12-31']

# Convert the timestamps for individual languages using the notnull() method,
# casting the boolean value into an integer.
year_2014 = year_2014.notnull().astype('int')
year_2015 = year_2015.notnull().astype('int')

# Take the columns for Russian for both years
ru_2014 = year_2014['ru']
ru_2015 = year_2015['ru']

# Group the observations by date
ru_2014 = ru_2014.groupby(ru_2014.index.date)
ru_2015 = ru_2015.groupby(ru_2015.index.date)

# Note that because the column uses binary values to indicate the presence
# or absence of a language, taking the mean returns the proportion of the
# particular language in relation to other languages observed on that day.
ru_2014 = ru_2014.apply(lambda x: x.mean()).to_frame('mean')
ru_2015 = ru_2015.apply(lambda x: x.mean()).to_frame('mean')

# Finally, cast the columns with mean values into numpy arrays for stats test
ru_2014 = ru_2014['mean'].values
ru_2015 = ru_2015['mean'].values

# Compare the observations using the Kruskal-Wallis test
kw_test = kruskal(ru_2014, ru_2015)

# Print status
print("Kruskal-Wallis H-statistic: {:.3f}, P-value: {:.3f}".format(kw_test[0],
                                                                   kw_test[1]))


