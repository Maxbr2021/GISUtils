# GISUtils

## Background

GIS data become increasingly important when analyzing mobility behaviours in older adults. This Repo offers the utilities to retrive and analyze GPS positions based on their sourrundings. The data is retrived from OSM and stored lacally to ease inference.



## Environment installation
You can install the environment following the description below (might take a while):
```
conda env create --file=environment.yml
```

## Before you are getting started
To be able to utilities you must download the GIS data to a local folder (GisData). You can use the upper part of the demo.py script to do so. The demo.py script will then donwload the GIS data based upon the config.json file which can be modified to suite user preferences.


## Running the analysis and start plotting
The GISUtils repository offers two different functions to analyze GIS data around locations (specified in the data.csv file). The return_count function can be used for count based GIS data like poi, shops, and public transport. They are calculated as the number of data points within a walkability polygon. The return_ratio function allows the user to return a ratio of overlapping GIS data with a buffer around the specified location.
