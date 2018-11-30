# A repository for the article "[Exploring the linguistic landscape of geotagged social media content in urban environments](https://doi.org/10.1093/llc/fqy049)" published in [Digital Scholarship in the Humanities](https://academic.oup.com/dsh)

## Introduction

The article is published with an open license (CC BY 4.0) and can be found at the journal website [here](https://doi.org/10.1093/llc/fqy049) and in this [repository](hiippala-etal-2018.pdf).

The repository is organised into directories, which contain scripts related to various analyses conducted in the article.

The scripts are described in greater detail in their respective subfolders.

| Directory | Description |
| :-------- | :---------- |
| [langid](langid)   | Scripts for automatic language identification |
| [plots](plots) | Scripts for analysing and plotting the data |
| [spatial](spatial) | Scripts for analysing user mobility |
| [stats](stats) | Scripts for statistical analyses |
| [topics](topics) | Scripts for topic modelling |
| [utils](utils) | Utility scripts and dummy dataset for testing |

## Usage

To use the scripts you need to have Python 3 installed with the required libraries. It's recommended to setup a virtual python 3 environment and install the required libraries:
>`pip install requirements.txt`

The topic modelling script requires NLTK's stopwords and spaCy's model for english language, after installing requirements.txt run:
>`python -m nltk.downloader stopwords`

>`python -m spacy download en`

After installation run the scripts on your data or on the provided [dummy dataset](utils/dummydata.pkl) in the recommended order. For more information about the dummy dataset: scroll down and read **About the dummy dataset** section. 


### Recommended order of running scripts
In the table below is the recommended order to run the scripts in this repo. The input/ouput names are _examples_, you will have to use the correct names for your data.

| Step | Script | Input | Output |
|:---|:---|:---|:---|
|0|[get_fasttext_model.py](/utils/get_fasttext_model.py)|--|langid/models/lid.176.bin|
|1|[run_fasttext.py](/langid/run_fasttext.py) or [run_langid.py](langid/run_langid.py)|___your_data.pkl___|lid_data.pkl|
|2|[location_history_creator.py](/spatial/location_history_creator.py)|lid_data.pkl|lh_data.pkl|
|3|[reverse_geocode.py](/spatial/reverse_geocode.py)|lh_data.pkl|revgeo_data.pkl|
|4|[extract_languages+activities.py](/spatial/extract_languages+activities.py)|revgeo_data.pkl|lochist_data.pkl|
|5|[add_location_hist_to_df.py](/utils/add_location_hist_to_df.py)|lochist_data.pkl + lh_data.pkl|joined_data.pkl|
|6|[topic_model_for_language+country.py](/topics/topic_model_for_language+country.py)|joined_data.pkl|LaTex table|
|7|scripts from [stats](/stats) or [plots](/plots)|joined_data.pkl|outputs vary (images, text)|

In step 1, your input data should be ___a pickled Pandas/GeoPandas DataFrame___ with matching column names from the scripts. 

___Compatibility issues___: Windows compatibility is an issue. _Skbio_ (a library for plots scripts) _doesn't_ work on Windows operating systems. _Pyfasttext_ and its dependencies (mainly _cysignals_) can be difficult to get to work on Windows operating systems.

### About the dummy dataset

The dummy dataset is strictly for script testing purposes. It is a pickled Pandas DataFrame, that contains generated user_ids, photo_ids, caption texts, timestamps and geometries. The caption texts were generated using a Keras RNN and fastText word embeddings from actual Instagram captions from Helsinki. The captions are monolingual and the languages in question are the 10 most frequently used languages in Instagram captions from Helsinki. _User_ids, photo_ids, timestamps_ and _geometries_ are all _randomly generated_ and thus statistical tests on and plotting made with the dummy dataset ___will___ reflect the randomness.


## Reference

If you use these scripts in your research, please cite the following reference:

Hiippala, Tuomo, Hausmann, Anna, Tenkanen, Henrikki and Toivonen, Tuuli (2018) Exploring the linguistic landscape of geotagged social media content in urban environments. <i>Digital Scholarship in the Humanities</i>. DOI: [10.1093/llc/fqy049](https://doi.org/10.1093/llc/fqy049)
