# SetlistApp

This app was mainly just used to help my bands generate setlists, given a proper csv file with all the songs in it

## Installation

It is recommended you use conda to install the dependencies for this project. To do so, run the following command:

```bash
conda env create -f environment.yml
conda activate setlistapp
```

Otherwise, you can download python and download the necessary requirements from the requirements.txt file.

## src

format_csv.py: This file is used to format the csv file that is used to generate the setlist. It is not necessary to run this file if the csv file is already formatted.
setlist_make_gui.py: This file is used to generate the setlist. It is the main file that should be run.

## Usage

After running the file, the only things you need to find are the input and output files. You can click the "Browse" tool for this. The input file should be a csv file with the correct format (see songs.csv for a template). The output file should be a text file that will be generated with the setlist. The "Generate Setlist" button will generate the setlist and save it to the output file.

The OG Weight is meant to be a weight for the original songs. The higher the weight, the more likely the song will be played. The OG Weight is a multiplier for the weight of the song.

The Mood Weight is meant to be a weight for the mood of the song. The higher the weight, the more likely the song will be played. The Mood Weight is a multiplier for the weight of the song.

The Includes are songs that definitely have to be included. They must be comma separated, and note that they ARE case-senstitive. Includes should be activated in the csv file.

The set time is the amount of time that the set should be. It is in minutes.

The transition time is just subtracted from set time to get the actual time of the set. It is in minutes.

The cluster size is the number of songs in one cluster. A cluster is defined as a group of songs with a similar mood value. It is recommended that you keep this at 2.
