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

To use the scripts you need to have Python 3 installed with the required libraries. To install the libraries it's recommended to run `pip install requirements.txt`. About the libraries: __Skbio__ (a library for stats scripts) _doesn't_ work on Windows operating systems and __Pyfasttext__ can be difficult to get to work on Windows operating systems.

There's a generated dummy dataset included under utils that can be used to test the scripts. The dataset contains fake captions in ten languages and randomly generated spatio-temporal characteristics. 

### Recommended order of running scripts
1. Langid scripts (and `get_fasttext_model.py` from utils)
2. Spatial scripts (1. `location_history_creator.py`, 2. `reverse_geocode.py`, 3. `extract_locations+activities.py`)

   a. The scripts assume that geographical data are under _geometry_ column as shapely points.
3. Topics scripts (if required)
4. Stats scripts
5. Plots scripts

## Reference

If you use these scripts in your research, please cite the following reference:

Hiippala, Tuomo, Hausmann, Anna, Tenkanen, Henrikki and Toivonen, Tuuli (2018) Exploring the linguistic landscape of geotagged social media content in urban environments. <i>Digital Scholarship in the Humanities</i>. DOI: [10.1093/llc/fqy049](https://doi.org/10.1093/llc/fqy049)
