#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script creates a topic model for captions written in a specific language,
posted by users from a specific country.

Usage:
    Execute the script from the command line using the following command:
    
    python3 topic_model_for_language+country.py -i input.pkl
    
Arguments:
    -i/--input: Path to the pandas DataFrame containing both location histories
                and predictions for automatic language identification.
    -l/--language: ISO-639 language code (e.g. en, fi, de) for the language of
                   the captions to be included in the topic model.
    -c/--country: The origin country for the users whose captions are included
                  in the topic model.
   
Returns:
    A LaTeX table containing topics and their coherence scores.
"""

# Import the required packages
from gensim import corpora
from nltk.corpus import stopwords
from spacy.lang.en import LOOKUP
from urllib.parse import urlparse

import argparse
import emoji
import gensim
import numpy as np
import pandas as pd
import re
import string


# Set up the argument parser
ap = argparse.ArgumentParser()

# Define arguments
ap.add_argument("-i", "--input", required=True,
                help="Path to the pandas DataFrame with location histories.")
ap.add_argument("-l", "--language", required=True,
                help="ISO-639 language code for the language chosen for topic "
                     "modelling.")
ap.add_argument("-c", "--country", required=True,
                help="Name of the country ...")

# Parse arguments
args = vars(ap.parse_args())

# Assign arguments to variables
language = args['language']

# Load the dataframe input DataFrame and assign to variable
input_df = pd.read_pickle(args['input'])

# Convert the descriptive statistics into dict for use below
loc_stats = input_df['prev-locations'].describe().to_dict()
act_stats = input_df['activity-longest'].describe().to_dict()

# Drop users in the 25th percentile in terms of their location history
input_df = input_df.loc[input_df['prev-locations'] >= loc_stats['25%']]

# Drop users in the 25th percentile in terms of their activity period
input_df = input_df.loc[input_df['activity-longest'] > act_stats['25%']]

# Drop users outside the target country
input_df = input_df.loc[input_df['country-longest'] == args['country']]

# Set up basic processing for building the corpus. First, join stopword lists
# from NLTK and spaCy. Second, fetch a list of punctuation symbols from the
# strings module. Finally, set up a lookup table for spaCy lemmatizer.
if args['language'] == 'en':
    stop = set(stopwords.words('english'))
    lemma_lookup = dict(LOOKUP)
if args['language'] == 'fi':
    stop = set(stopwords.words('finnish'))

excl = set(string.punctuation)

# Set up a placeholder list for sentences preprocessed for topic modelling
sents = []

# Begin looping over the input DataFrame
for ix, row in input_df.iterrows():

    # Assign the predictions into a variable
    predictions = row['langid']

    # Set up a list to hold all predictions for a single caption
    preds_list = [p[0] for p in predictions]

    # Reduce the set to a list
    preds_list = set(preds_list)

    # Filter the result for captions without codeswitching and written in the
    # language chosen for topic modelling
    if len(preds_list) == 1 and list(preds_list)[0] == args['language']:

        # Assign caption to variable
        caption = row['caption']

        # Convert unicode emoji to shortcode emoji
        caption = emoji.demojize(caption)

        # Remove single emojis and their groups
        caption = re.sub(r':(?<=:)([a-zA-Z0-9_\-&\'\’]*)(?=:):', '', caption)

        # Remove all mentions (@) in the caption
        caption = re.sub(r'@\S+ *', '', caption)

        # Remove all hashtags (#) in the caption
        caption = re.sub(r'#\S+ *', '', caption)

        # Split the string into a list
        caption = caption.split()

        # Remove all non-words such as smileys etc. :-) and convert to lowercase
        caption = [word.lower() for word in caption if re.sub('\W', '', word)]

        # Remove non-alphabetic words, such as numbers, years, etc.
        caption = [word for word in caption if word.isalpha()]

        # Check the list of items for URLs and remove them
        caption = [word for word in caption if not urlparse(word).scheme]

        # Remove stopwords
        caption = ' '.join(word for word in caption if word not in stop)

        # Remove punctuation
        caption = ''.join([char for char in caption if char not in excl])

        # Lemmatize tokens present in the lookup table
        if args['language'] == 'en':
            caption = ' '.join(lemma_lookup.get(word, word) for
                               word in caption.split())

        if args['language'] == 'fi':
            pass

        # Append the doc as a list of items to the placeholder list. The doc
        # must be a list of tokens, hence apply the split method first. Check
        # caption length to make sure some content exists.
        if len(caption) > 0:
            caption = caption.split()
            sents.append(caption)

# Print information on the document corpus
print("[INFO] Number of documents: {}".format(len(sents)))

# Begin building the topic model
dictionary = corpora.Dictionary(sents)

# Filter tokens that appear less than once
dictionary.filter_extremes(no_below=1, no_above=0.25)

# Print information on the document corpus
print("[INFO] Size of dictionary: {}".format(len(dictionary)))

# Convert the dictionary into a document term matrix
matrix = [dictionary.doc2bow(sent) for sent in sents]

# Initialize the LDA model from gensim
lda = gensim.models.ldamodel.LdaModel

# Train the model on the document term matrix
model = lda(matrix, num_topics=10, id2word=dictionary, passes=10,
            iterations=150)

# Initialize the coherence evaluation model from gensim
cm = gensim.models.coherencemodel.CoherenceModel(model=model,
                                                 texts=sents,
                                                 coherence='c_v',
                                                 topn=10
                                                 )

# Get the coherence of each topic and round the values
coherence = cm.get_coherence_per_topic()
coherence = [round(score, 3) for score in coherence]

# Print topics
topics = model.show_topics(num_topics=10, num_words=10, formatted=True)

# Add a placeholder list to hold the final output
result = []

# Loop over the topics
for t in topics:

    # Assign the word string into their own variable
    words = t[1]

    # Split the words
    words = words.split(' + ')

    # Extract the words from the predictions
    words = [w.split('*')[1].strip('"') for w in words]

    # Append the row to the final result
    result.append(words)

# Convert the result into a NumPy array and transpose.
result = np.vstack(result).transpose()

# Append the coherence scores (Cv) to the matrix
result = np.vstack([result, coherence])

# Convert the result into a DataFrame
result = pd.DataFrame(result, columns=range(1, len(result)))

# Print out a LaTeX table
print(result.to_latex(na_rep='--', index=False))
