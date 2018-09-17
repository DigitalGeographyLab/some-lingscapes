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


# Define model URL
MODEL_URL = "https://s3-us-west-1.amazonaws.com/fasttext-vectors/" \
            "supervised_models/lid.176.bin"
