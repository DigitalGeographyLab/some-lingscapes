# -*- coding: utf-8 -*-

"""
This file contains supporting functions for diversity analyses and plotting.
"""

import numpy as np
import pandas as pd
import pytz
import skbio.diversity.alpha as sk


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
        # Berger-Parker dominance index
        return sk.berger_parker_d(observations.values)

    if measurement == 'dominance':
        # Dominance: 1 - Simpson index. Zero means all languages are equally
        # present, while 1 means that one language dominates the whole data.
        return sk.dominance(observations.values)

    if measurement == 'menhinick':
        return sk.menhinick(observations.values)

    if measurement == 'simpson':
        # Simpson's index
        return sk.simpson(observations.values)

    if measurement == 'singles':
        return sk.singles(observations.values)

    if measurement == 'shannon':
        return np.exp(sk.shannon(observations.values, base=np.e))

    if measurement == 'unique':
        return sk.observed_otus(observations.values)


def extract_monthly_predictions(grouped_months, languages, bundle=False):
    # Create a new dict to hold the post counts for each month
    months = {}

    # Loop over the groups for each month: 'm' is month or the group identifier,
    # while 'posts' contains the monthly posts.
    for m, posts in grouped_months:

        # Count the monthly posts for each language
        monthly_posts = posts['language'].value_counts(normalize=True).to_dict()

        # Set up a dict to hold the monthly observations for each language
        observations = {}

        # Begin looping over the languages to retrieve their corresponding
        # percentage for each month
        for l in languages:
            # Check if the language can be found within the monthly observations
            # by comparing dictionary keys
            if l not in monthly_posts.keys():
                # If a language is not found, try to add 0 to the results dict
                try:
                    observations[l].append(0)
                # If the key for the particular language has not been added yet,
                # do so first.
                except KeyError:
                    observations[l] = 0
            # If the language can be found among the montly results, repeat the
            # same procedure as above.
            else:
                try:
                    observations[l].append(monthly_posts[l])
                except KeyError:
                    observations[l] = monthly_posts[l]

        # Check if languages outside the top-K languages should be included in
        # the plot.
        if bundle is True:
            # Loop over the list of top-k languages and pop them from the dict
            # containing monthly observations.
            for l in languages:
                try:
                    monthly_posts.pop(l)
                except KeyError:
                    pass

            # Sum the monthly percentage for languages outside top-K and append
            # to the dictionary of languages under the key 'other'. Note that
            # the sum of percentages for top-K and other languages does not
            # necessarily add up to 1 due to extremely small rounding errors.
            observations['other'] = sum(monthly_posts.values())

        # Append the monthly observations to the dictionary that holds all
        # observations, using the year-month as a key
        months[m] = observations

    # Return observations per month
    return sort(months)


def extract_weekly_predictions(grouped_weeks, languages, bundle=False):
    # Create a new dict to hold the post counts for each month
    weeks = {}

    # Loop over the groups for each week: 'w' is week or the group identifier,
    # while 'posts' contains the weekly posts.
    for w, posts in grouped_weeks:

        # Count the weekly posts for each language
        weekly_posts = posts['language'].value_counts(normalize=True).to_dict()

        # Set up a dict to hold the weekly observations for each language
        observations = {}

        # Begin looping over the languages to retrieve their corresponding
        # percentage for each week
        for l in languages:
            # Check if the language can be found within the weekly observations
            # by comparing dictionary keys
            if l not in weekly_posts.keys():
                # If a language is not found, try to add 0 to the results dict
                try:
                    observations[l].append(0)
                # If the key for the particular language has not been added yet,
                # do so first.
                except KeyError:
                    observations[l] = 0
            # If the language can be found among the weekly results, repeat the
            # same procedure as above.
            else:
                try:
                    observations[l].append(weekly_posts[l])
                except KeyError:
                    observations[l] = weekly_posts[l]

        # Check if languages outside the top-K languages should be included in
        # the plot.
        if bundle is True:
            # Loop over the list of top-k languages and pop them from the dict
            # containing weekly observations.
            for l in languages:
                try:
                    weekly_posts.pop(l)
                except KeyError:
                    pass

            # Sum the weekly percentage for languages outside top-K and append
            # to the dictionary of languages under the key 'other'. Note that
            # the sum of percentages for top-K and other languages does not
            # necessarily add up to 1 due to extremely small rounding errors.
            observations['other'] = sum(weekly_posts.values())

        # Append the weekly observations to the dictionary that holds all
        # observations, using the week number as a key
        weeks[w] = observations

    # Return observations per weekly
    return sort(weeks)


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


def extract_daily_activity(grouped_weekdays):
    """
    This function counts the number of posts per weekday from a pandas DataFrame
    that has been grouped according to calendar week.

    Parameters:
        grouped_weekdays: a pandas DataFrame grouped according to calendar week,
        with the time of posting in column 'time_created_local'.

    Returns:
        A dictionary with the weekday as the key and a list of post counts per
        weekday on each calendar week as the value.
    """
    # Create a new dict to hold the post counts for each day of the week
    daily_activity = {}
    # Loop over the groups for each calendar week: yw is year-week, or the group
    # identifier, whereas posts contains the weekly posts.
    for yw, posts in grouped_weekdays:
        # Assign date (group key) and retrieve the number of posts made on each
        # day and assign them to a dictionary.
        calendar_week, posts = yw, posts.time_created_local.apply(
            lambda x: x.isoweekday()).value_counts().to_dict()
        # Loop over the post keys (weekdays) and values (number of posts)
        for k, v in posts.items():
            # Try appending the post count to the dictionary, using the hour as
            # key
            try:
                daily_activity[k].append(v)
            # If this raises a KeyError exception, create the new entry
            except KeyError:
                daily_activity[k] = [v]

    # Return a dictionary with daily activity, which has been sorted according
    # to the keys.
    return sort(daily_activity)


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

