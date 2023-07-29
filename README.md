# SetlistApp

This app was mainly just used to help my bands generate setlists, given a proper csv file with all the songs in it

## Installation

I have 2 different options for installation. The first is using Python and Pip, and the second is using Conda. I personally use Conda, but I have included the Python and Pip option for my bandmates. If you have any issues, please contact me.

### Python and Pip (recommended for my bandmates)

All you need to do is download Python 3.10.9 or 3.11.4 (I've tested on only these versions, but I'm sure it will work with others), and then download the requirements.txt file. Then, run the following command:

```bash
pip install -r requirements.txt
```

The command above will install all the necessary dependencies for the project. However, if this does not work, seek this guide (or contact me). <https://packaging.python.org/en/latest/tutorials/installing-packages/>.

### Conda

I personally use a conda virtual environment, so I have exported my environment in a .yml file. To create this environment, make sure you have conda installed and then run the following command:

```bash
conda env create -f environment.yml
conda activate setlistapp
```

## src

format_csv.py: This file is used to format the csv file that is used to generate the setlist. It is not necessary to run this file if the csv file is already formatted.
setlist_math.py: This file contains the math part of the project. It is used to generate the setlist.
gui.py: This file contains the gui part of the project. It is also the main file that should be run.

## Usage

After running the file, the only things you need to find are the input and output files. You can click the "Browse" tool for this. The input file should be a csv file with the correct format (see songs.csv for a template). The output file should be a text file that will be generated with the setlist. The "Generate Setlist" button will generate the setlist and save it to the output file.

The OG Weight is meant to be a weight for the original songs. The higher the weight, the more likely the song will be played. The OG Weight is a multiplier for the weight of the song.

The Mood Weight is meant to be a weight for the mood of the song. The higher the weight, the more likely the song will be played. The Mood Weight is a multiplier for the weight of the song.

The Includes are songs that definitely have to be included. They must be comma separated, and note that they ARE case-senstitive. Includes should be activated in the csv file.

The set time is the amount of time that the set should be. It is in minutes.

The transition time is just subtracted from set time to get the actual time of the set. It is in minutes.

The cluster size is the number of songs in one cluster. A cluster is defined as a group of songs with a similar mood value. It is recommended that you keep this at 2.
