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

import urllib.request
import os

# Set root directory
rootdir = os.path.dirname(os.path.dirname(__file__))

# Define target path
target_path = os.path.join(rootdir, '..', 'langid', 'models')

# Print status and create target directory
print('[INFO] - Creating path ...')
os.makedirs(target_path, exist_ok=True)

# Print status when target directory has been created
print('[INFO] - Path created!')

# Define model URL
MODEL_URL = "https://s3-us-west-1.amazonaws.com/fasttext-vectors/" \
            "supervised_models/lid.176.bin"

# Print status and download model
print('[INFO] - Note: Downloading the model can take up to 10 minutes')
print('[INFO] - Downloading model...')
urllib.request.urlretrieve(MODEL_URL, os.path.join(target_path, 'lid.176.bin'))

# Print status when complete
print('[INFO] - Download complete!')
