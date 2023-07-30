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
gui.py: This file contains the gui part of the project. This holds the gui class.
main.py: This is the driver file. This is the file to run the whole program.

## Usage

After running main.py, there are two tabs: "Make Setlist" and "View Setlist". I think that each tab is self-explanatory, but I will explain it anyway: The "Make Setlist" tab is used to generate a setlist, and the "View Setlist" tab is used to view the setlist that has already been generated.

Note: CSV file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active. You may use format_csv.py to format the csv file, if you wish.

### Make Setlist

The only thing you need is an input file. You can click the "Browse" tool for this. The input file should be a csv file with the correct format (see songs.csv for a template). The "Generate Setlist" button will generate the setlist to view in the "View Setlist" tab.

The OG Weight is meant to be a weight for the original songs. The higher the weight, the more likely the song will be played. The OG Weight is a multiplier for the weight of the song.

The Mood Weight is meant to be a weight for the mood of the song. The higher the weight, the more likely the song will be played. The Mood Weight is a multiplier for the weight of the song.

The Includes are songs that definitely have to be included. They must be comma separated, and note that they ARE case-senstitive. Includes should be activated in the csv file.

The set time is the amount of time that the set should be. It is in minutes.

The transition time is just subtracted from set time to get the actual time of the set. It is in minutes.

The cluster size is the number of songs in one cluster. A cluster is defined as a group of songs with a similar mood value. It is recommended that you keep this at 2.

### View Setlist

You can view the setlist that has already been generated. You can also save the setlist to a file.

The output file should be a text file. Output file browsing works the same as Input file browsing. Press the export button to export the setlist to a file.
