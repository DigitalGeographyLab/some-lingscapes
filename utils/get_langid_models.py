# -*- coding: utf-8 -*-

"""
This script downloads a pre-trained fastText model for automatic language
identification.

Usage:
    Execute the script from the command line using the following command:

    python3 get_langid_models.py

Returns:
    Downloads the model and saves it to ../langid/models/lid.176.bin. This
    allows you to perform language identification using fastText. For more
    details see ../langid.
"""
import urllib
import os

# Setting root directory
rootdir = os.path.dirname(os.path.dirname(__file__))

# Create path
print('[INFO] - Creating path...')
os.makedirs(os.path.join(rootdir,'langid\models'), exist_ok=True)
print('[INFO] - Path created!')

# Define model URL
MODEL_URL = "https://s3-us-west-1.amazonaws.com/fasttext-vectors/" \
            "supervised_models/lid.176.bin"

# Download model
print('[INFO] - Downloading model...')
urllib.request.urlretrieve(MODEL_URL,
                           os.path.join(rootdir,'langid\models\lid.176.bin'))
print('[INFO] - Download complete!')
