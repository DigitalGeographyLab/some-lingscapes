from scipy.stats import pearsonr, normaltest
from supporting_functions import extract_predictions
import argparse
import pandas as pd
import seaborn as sns
import skbio.diversity.alpha as sk


# Define supporting functions
def diversity(languages, measurement):
    """
    A function for various diversity indices provided by scikit-bio.

    Parameters:
        languages: A pandas Series containing daily observations for different
                   languages.
        measurement: The diversity index to be calculated.

    Returns:
        The requested diversity index as a NumPy array.
    """

    # Count the number of unique languages observed per day.
    observations = languages.value_counts()

    # Check the requested measurement and return the corresponding index.
    if measurement == 'berger':
        return sk.berger_parker_d(observations.values)
    if measurement == 'menhinick':
        return sk.menhinick(observations.values)
    if measurement == 'simpson':
        return sk.simpson(observations.values)
    if measurement == 'singles':
        return sk.singles(observations.values)
    if measurement == 'shannon':
        return sk.shannon(observations.values)
    if measurement == 'unique':
        return sk.observed_otus(observations.values)


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

# Initialize seaborn for prettier plots
sns.set()

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
path_to_df = args['dataframe']

if args['fthresh']:
    ft = args['fthresh']
if args['cthresh']:
    ct = args['cthresh']

# Load dataframe
input_df = pd.read_pickle(path_to_df)

# Extract predictions from the input DataFrame
posts = extract_predictions(input_df)

# If thresholds have been defined, drop the predictions whose confidence is
# below the thresholds.
if args['fthresh']:
    posts = posts.loc[posts['probability'].apply(lambda x: float(x) >= ft)]

if args['cthresh']:
    posts = posts.loc[posts['char_len'].apply(lambda x: float(x) >= ct)]

# Set the timestamp indicating the time of creation to create a DateTimeIndex
posts.index = posts['time_created_local']

# Use the DateTimeIndex to group the posts according to their posting time, then
# apply the diversity measurement function to the 'language' column.
posts = posts.groupby(posts.index.date)['language']

# Count the number of unique languages; convert the result to a DataFrame; then
# generate a DateTimeIndex for the DataFrame.
unique = posts.apply(
    lambda x: diversity(x, 'unique')).to_frame(name='Distinct languages')
unique.index = pd.to_datetime(unique.index)

# Next, count single occurrences of a language.
single = posts.apply(
    lambda x: diversity(x, 'singles')).to_frame(name='Single occurrences')
single.index = pd.to_datetime(single.index)

# Take 30-day rolling averages for both
unique_avg = unique.rolling(window=30).mean()
single_avg = single.rolling(window=30).mean()

# Drop NaN values resulting from taking a trailing rolling average
unique_avg = unique_avg.dropna()
single_avg = single_avg.dropna()

# Test whether the data follows a normal distribution
pvalue_1 = normaltest(unique_avg.values)[1]
pvalue_2 = normaltest(single_avg.values)[1]

if pvalue_1 < 1e-3:
    print("[INFO] The first data set follows a normal distribution.")
if pvalue_2 < 1e-3:
    print("[INFO] The second data set follows a normal distribution.")

# Calculate Pearson's R between the two series
pearson = pearsonr(unique_avg.values, single_avg.values)

print("[INFO] Pearson's r: {:.3f}, n: {}, p: {}".format(
    pearson[0][0], len(unique_avg), pearson[1][0]))
