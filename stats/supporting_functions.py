# -*- coding: utf-8 -*-

"""
This file contains supporting functions for diversity analyses and plotting.
"""

import numpy as np
import pandas as pd
import pytz

def extract_predictions(input_df):
    """
    This function extracts the output of a language identification framework
    from a pandas DataFrame, returning a new DataFrame with the predicted
    language of each sentence in a caption. The new DataFrame also includes the
    column for the photograph identifier, which can be then used to group the
    individual sentences.

    Parameters:
        input_df: a pandas DataFrame containing predictions for the language of
        the caption in the column 'predictions'

    Returns:
        A Pandas DataFrame with the predicted language of each sentence in the
        captions of the original DataFrame.
    """
    # Calculate the number of rows required for the output dataframe by applying
    # the count_preds function to each cell
    rows_needed = sum(input_df['langid'].apply(lambda x: len(x)))

    # Create a new dataframe to hold the predictions
    pred_df = pd.DataFrame(index=range(0, rows_needed))

    # Set up a counter to keep track of the index
    current_index = 0

    # Loop over the DataFrame rows
    for ix, row in input_df.iterrows():

        # Fetch the predictions from the 'predictions' column and assign to
        # variable 'preds'; do the same for the unique photo identifier and
        # the timestamp.
        predictions = row['langid']
        photo_id = row['photo_id']
        user_id = row['user_id']
        time_created_local = row['time_created_local']

        # Loop over the predictions
        for p in predictions:

            # Split the individual predictions into an ISO-639 language code,
            # the associated probability and length in characters
            lang, prob, char_len = p[0], p[1], p[2]

            # Enter the predictions and probabilities to the new DataFrame
            # together with the unique identifier for each photo 'photo_id'.
            pred_df.at[current_index, 'char_len'] = int(char_len)
            pred_df.at[current_index, 'language'] = str(lang)
            pred_df.at[current_index, 'probability'] = float(prob)
            pred_df.at[current_index, 'photo_id'] = str(photo_id)
            pred_df.at[current_index, 'user_id'] = int(user_id)
            pred_df.at[current_index, 'time_created_local'] = time_created_local

            # Update index
            current_index = current_index + 1

    # Return the new DataFrame with languages and probabilities
    return pred_df


def extract_timestamps(input_df):
    """
    This function extracts naive timestamps from a Pandas dataframe and adds
    timezone information to them.

    Parameters:
        input_df: a pandas DataFrame containing an UTC timestamp in column
        'time_created_utc'

    Returns:
        A DataFrame with matching index, containing time of posting at UTC and
        local time ('Europe/Helsinki').
    """
    # Convert the datetime in the column 'time_created_utc' to local time
    # (GMT+2). Begin by defining the source and target zones.
    from_zone = pytz.timezone('UTC')
    to_zone = pytz.timezone('Europe/Helsinki')

    # Create a new dataframe; copy the index from the input dataframe.
    output_df = pd.DataFrame(index=input_df.index)

    # Doing this the lazy way for now ...
    for ix, row in input_df.iterrows():

        # Fetch the datetime
        time_created_utc = row['time_created_utc']

        # Tell the naive datetime that it's UTC
        time_created_utc = time_created_utc.replace(tzinfo=from_zone)

        # Convert the datetime to local timezone
        time_created_local = time_created_utc.astimezone(to_zone)

        # Append photo and user identifiers to the dataframe
        output_df.at[ix, 'photo_id'] = row['photo_id']
        output_df.at[ix, 'user_id'] = row['user_id']

        # Assign the new values to the dataframe
        output_df.at[ix, 'time_created_utc'] = time_created_utc
        output_df.at[ix, 'time_created_local'] = time_created_local

    # Return the new dataframe
    return output_df


def extract_hourly_activity(grouped_dates):
    """
    This function counts the number of posts per hour from a pandas DataFrame
    that has been grouped according to date.

    Parameters:
        grouped_dates: a pandas DataFrame grouped according to date, with the
        time of posting in column 'time_created_local'.

    Returns:
        A dictionary with the hour as the key and the number of posts made on
        each date as the value.
    """
    # Set up a dictionary to hold the hourly activity
    hourly_activity = {}
    # Loop over each groups of posts for each date
    for i, d in grouped_dates:
        # Assign date (group key) and retrieve the number of posts made at each
        # hourand assign them to a dictionary.
        date, posts = i, d.time_created_local.apply(lambda x:
                                                    x.hour).\
                                                    value_counts().to_dict()
        # Loop over the dictionary of hours extracted from the dataframe; get
        # post keys (hours) and values (number of posts)
        for k, v in posts.items():
            # Try appending the post count to the dictionary, using the hour as
            # key
            try:
                hourly_activity[k].append(v)
            # If this raises a KeyError exception, create the new entry
            except KeyError:
                hourly_activity[k] = [v]

    # Return the dictionary with hourly activity
    return hourly_activity

def sort(dictionary):
    """
    This function sorts the keys and values of a dictionary storing the number
    of posts made over some period of time.

    Parameters:
        dictionary: A dictionary mapping some period of time to post counts.

    Returns:
        A sorted dictionary.
    """
    # Set up an empty dict for sorted values
    new_dict = {}

    # Loop over the sorted items
    for key, value in sorted(dictionary.items()):
        new_dict[key] = value

    # Return the sorted dictionary
    return new_dict

