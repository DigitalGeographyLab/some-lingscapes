## Utility scripts

This directory contains various scripts for supporting the analyses.

| File | Description |
| :-------- | :---------- |
| [examine_dataframe.py](examine_dataframe.py) | Print out the contents of a pandas DataFrame for examination |
| [get_fasttext_model.py](get_fasttext_model.py) | Download fastText language identification model |
| [dummydata.pkl](dummydata.pkl) | Generated dummy dataset for testing |
| [add_location_hist_to_df.py](add_location_hist_to_df.py) | Merge location history pickle with language id pickle |

### About dummy dataset

The dummy dataset is strictly for script testing purposes. It is a pickled Pandas DataFrame, that contains generated user_ids, photo_ids, caption texts, timestamps and geometries. The caption texts were generated using a Keras RNN and fastText word embeddings from actual Instagram captions from Helsinki. The captions are monolingual and the languages in question are the 10 most frequently used languages in Instagram captions from Helsinki. _User_ids, photo_ids, timestamps_ and _geometries_ are all _randomly generated_ and thus statistical tests on and plotting made with the dummy dataset ___will___ reflect the randomness.
