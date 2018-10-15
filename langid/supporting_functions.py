# -*- coding: utf-8 -*-

"""
This file contains supporting functions for automatic language identification.
"""

from langid.langid import LanguageIdentifier, model
from nltk.tokenize.punkt import PunktSentenceTokenizer
from urllib.parse import urlparse
import emoji
from pyfasttext import FastText
import re

# Attempt to load the fastText language identification model
try:
    ft_model = FastText('models/lid.176.bin')

# Catch the error thrown by a missing model and provide additional instructions
except ValueError:
    exit("fastText language identification model not found! "
         "Run ../utils/get_fasttext_modells -al.py to download the model."
         )

# Attempt to load langid.py model
li_model = LanguageIdentifier.from_modelstring(model, norm_probs=True)


# Define the preprocessing function
def preprocess_caption(row, mode):
    """Applies the selected preprocessing steps to the text.

     Args:
         row: A UTF-8 string.
         mode: A string indicating the selected preprocessing strategy.
               Valid values include: 'no_preprocessing' (no preprocessing),
               'rm_all' (remove all hashtags) and 'rm_trail' (remove trailing
               hashtags).

     Returns:
         A string containing the preprocessed text.
    """
    # Check if preprocessing has been requested.
    if mode != 'no_preprocessing':

        # Convert unicode emoji to shortcode emoji
        row = emoji.demojize(row)

        # Remove single emojis and their groups
        row = re.sub(r':(?<=:)([a-zA-Z0-9_\-&\'’]*)(?=:):', '', row)

        # Apply the selected preprocessing strategy defined in the variable
        # 'mode'. This defines how each row is processed. The selected mode
        # defines the preprocessing steps applied to the data below by
        # introducing different conditions.

        # Remove all mentions (@) in the caption
        row = re.sub(r'@\S+ *', '', row)

        # If mode is 'rm_all', remove all hashtags (#) in the caption
        if mode == 'rm_all':
            row = re.sub(r'#\S+ *', '', row)

        # Split the string into a list
        row = row.split()

        # Remove all non-words such as smileys etc. :-)
        row = [word for word in row if re.sub('\W', '', word)]

        # Check the list of items for URLs and remove them
        row = [word for word in row if not urlparse(word).scheme]

        # Attempt to strip extra linebreaks following any list item
        row = [word.rstrip() for word in row]

        # If mode is 'rm_trail', remove hashtags trailing the text, e.g.
        # "This is the caption and here are #my #hashtags"
        if mode == 'rm_trail':
            while len(row) != 0 and row[-1].startswith('#'):
                row.pop()

        # Reconstruct the row
        row = ' '.join(row)

        # If mode is 'rm_trail', drop hashes from any remaining hashtags
        if mode == 'rm_trail':
            row = re.sub(r'g*#', '', row)

    # Simplify punctuation, removing sequences of exclamation and question
    # marks, commas and full stops, saving only the final character
    row = re.sub(r'[?.!,_]+(?=[?.!,_])', '', row)

    # Return the preprocessed row
    return row


def split_sentence(caption):
    """Tokenizes sentences using NLTK's Punkt tokenizer.

    Args:
        caption: A string containing UTF-8 encoded text.

    Returns:
        A list of tokens (sentences).
    """

    # Initialize the sentence tokenizer
    tokenizer = PunktSentenceTokenizer()

    # Tokenize the caption
    sent_tokens = tokenizer.tokenize(caption)

    # Return a list of tokens (sentences)
    return sent_tokens


def detect_ft(caption, preprocessing):
    """Identifies the language of a text using fastText.

    Args:
        caption: A string containing UTF-8 encoded text.
        preprocessing: A string indicating the selected preprocessing strategy.
                       Valid values include: 'no_preprocessing'
                       (no preprocessing),  'rm_all' (remove all hashtags) and
                       'rm_trail' (remove trailing hashtags).

    Returns:
        Saves the prediction into a column named 'langid' in the pandas
        DataFrame as a list of three tuples. The three tuple consists of an
        ISO-639 code, its associated probability and character length of the
        string input to fastText, e.g. ('en', 0.99999, 21).
    """
    # If the caption is None, return None
    if caption == 'None' or caption is None:
        return

    # Preprocess the caption
    caption = preprocess_caption(caption, preprocessing)

    # Perform sentence splitting for any remaining text
    if len(caption) == 0:
        return None

    else:
        # Get sentences
        sentences = split_sentence(caption)

        # Calculate the character length of each sentence
        char_len = [len(s) for s in sentences]

        # Make predictions
        predictions = ft_model.predict_proba(sentences, k=1, normalized=True)

        # Get the predicted languages and their probabilities
        languages = [[elem[0] for elem in p] for p in predictions]
        probabilities = [[elem[1] for elem in p] for p in predictions]

        # Return languages and probabilities
        return list(zip(*languages, *probabilities, char_len))


def detect_li(caption, preprocessing):
    """Identifies the language of a text using langid.py.

    Args:
        caption: A string containing UTF-8 encoded text.
        preprocessing: A string indicating the selected preprocessing strategy.
                       Valid values include: 'no_preprocessing'
                       (no preprocessing),  'rm_all' (remove all hashtags) and
                       'rm_trail' (remove trailing hashtags).

    Returns:
        Saves the prediction into a column named 'langid' in the pandas
        DataFrame as a list of three tuples. The three tuple consists of an
        ISO-639 code, its associated probability and character length of the
        string input to fastText, e.g. ('en', 0.99999, 21).
    """
    # If the caption is None, return None
    if caption == 'None' or caption is None:
        return

    # Preprocess the caption
    caption = preprocess_caption(caption, preprocessing)

    # Perform sentence splitting for any remaining text
    if len(caption) == 0:
        return None

    else:
        # Get sentences
        sentences = split_sentence(caption)

        # Calculate the character length of each sentence
        char_len = [len(s) for s in sentences]

        # Make predictions
        predictions = [li_model.classify(sent) for sent in sentences]
            
        # Get the predicted languages and their probabilities
        languages = [p[0] for p in predictions]
        probabilities = [p[1] for p in predictions]

        # Return languages and probabilities
        return list(zip(languages, probabilities, char_len))

