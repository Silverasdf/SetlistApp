# Setlist Make (w/ GUI) - This is the main GUI class for the setlist generator.

# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active
# Ryan Peruski, 05/27/2023

import pandas as pd
import random
import warnings
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QTabWidget, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtGui import QColor
from setlist_math import *

class SetlistGeneratorWindow(QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        self.output_file_path = ""
        self.debug = debug
        self.setlist = pd.DataFrame()
        self.song_file = ""
        self.available_songs = []
        self.included_songs = []
        self.excluded_songs = [] # List of excluded songs to show in GUI
        self.setWindowTitle("Setlist Generator")
        self.defaults = dict(og_weight=1.2, mood_weight=0.8, set_time=60, cluster_size=2)
        self.init_ui()

    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select Input File", "", "CSV Files (*.csv);;All Files (*)")
        self.input_file_entry.setText(file_path)

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Save Output File", "", "Text Files (*.txt);;All Files (*)")
        self.output_file_path = file_path
        self.output_file_entry.setText(file_path)

    def generate_setlist(self):
        # Get user inputs
        song_file = self.input_file_entry.text()
        og_weight = float(self.og_weight_entry.text() or self.defaults["og_weight"])  # Default value if no input
        mood_weight = float(self.mood_weight_entry.text() or self.defaults["mood_weight"])  # Default value if no input
        set_time = float(self.set_time_entry.text() or self.defaults["set_time"])  # Default value if no input
        transition_time = float(self.transition_time_entry.text() or set_time*0.1)  # Default value if no input
        cluster_size = int(self.cluster_size_entry.text() or self.defaults["cluster_size"])  # Default value if no input
        #Reset random seed
        random.seed()

        # Main code
        try:
            songs = pd.read_csv(song_file)
            # Song file setup for class
            # First Time setup (whenever a new song file is selected)
            if self.song_file != song_file: 
                # Reset variables and then fill in excludes and available songs.
                self.reset_vars()
                self.available_songs = songs["Song"].tolist()
                self.excluded_songs = songs.query('Active == False')["Song"].tolist()

            
            self.song_file = song_file
            # Filter songs
            for song in self.excluded_songs:
                songs = songs.query('Song != @song')


            warnings.filterwarnings("ignore")
            setlist = make_setlist(songs, target_time=set_time-transition_time, og_weight=og_weight, mood_weight=mood_weight, includes=self.included_songs)
            sorted_clusters = sort_sample_into_clusters(setlist, cluster_size=cluster_size)
            self.setlist_generated_text.clear()  # Clear previous message
            self.setlist_generated_text.append("Setlist generated!")
        except FileNotFoundError:
            self.setlist_generated_text.clear()
            self.setlist_generated_text.append("Error: File not found!")
            self.reset_vars()
        except IndexError:
            self.setlist_generated_text.clear()
            self.setlist_generated_text.append("Error: Your set time is too short for the songs you have selected!")
        except Exception as e:
            self.setlist_generated_text.clear()  # Clear previous message
            self.setlist_generated_text.append(f"Error: {e}!")
            self.setlist_generated_text.append(f"Make sure your CSV is formatted correctly.")
            self.setlist_generated_text.append(f"See the README for more information.")
            self.reset_vars()

        #Update tab 3
        self.load_songs_from_csv()

        return dict(
            setlist=sorted_clusters,
            og_weight=og_weight,
            mood_weight=mood_weight,
            set_time=set_time,
            transition_time=transition_time,
            cluster_size=cluster_size,
            includes = self.included_songs,
            excludes = self.excluded_songs
        )

    # Updated the setlist text box and list as well as displaying results for debug. "Run" button under "Make Setlist" tab
    def update_setlist(self):
        vals = self.generate_setlist()
        if self.debug:
            print(f"New setlist with values:")
            for val in reversed(vals):
                if val != "setlist":
                    print(f"{val}: {vals[val]}")
            print("Setlist:")
            for i, row in vals["setlist"].iterrows():
                print(row["Song"])
        self.setlist = vals["setlist"]
        setlist_text = write_setlist_to_string(vals["setlist"])

        self.setlist_text_box.clear()
        self.setlist_text_box.append(setlist_text)
    
    # "Text Mode" button after "Run" button under "Make Setlist" tab
    def show_setlist_text(self):
        self.setlist_list_box.setVisible(False)
        self.setlist_text_box.setVisible(True)
        self.setlist_text_box.clear()
        setlist_text = write_setlist_to_string(self.setlist)
        self.setlist_text_box.append(setlist_text)
        self.message_box_export.clear()
        self.message_box_export.setText(self.message_box_export.text() + "Switched to text mode.")
        if self.debug:
            print("Switched to text mode.")

    # "List Mode" button after "Run" button under "Make Setlist" tab
    def show_setlist_list(self):
        self.setlist_text_box.setVisible(False)
        self.setlist_list_box.setVisible(True)
        self.setlist_list_box.clear()
        for i, row in self.setlist.iterrows():
            self.setlist_list_box.addItem(row["Song"])
        self.message_box_export.clear()
        self.message_box_export.setText(self.message_box_export.text() + "Switched to list mode.")
        if self.debug:
            print("Switched to list mode.")

    # Resets all variables for a new csv file or if an error occurs
    def reset_vars(self):
        if self.debug:
            print("Resetting variables")
        self.output_file_path = ""
        self.song_file = ""
        self.setlist = pd.DataFrame()
        self.available_songs = []
        self.included_songs = []
        self.excluded_songs = []
        self.load_songs_from_csv()

    # The "Export" button on the "View Setlist" Tab
    def export_to_output_file(self):
        setlist_text = write_setlist_to_string(self.setlist)
        if self.output_file_path and not self.setlist.empty: # Setlist must be created and output file must be selected
            with open(self.output_file_path, "w") as file:
                file.write(setlist_text)
                if self.debug:
                    print(f"Exported setlist to {self.output_file_path}")
            self.message_box_export.clear()
            self.message_box_export.setText(self.message_box_export.text() + "Exported to " + os.path.basename(self.output_file_path) + "!\n")
        else: # Error handling
            self.message_box_export.clear()
            if self.output_file_path:
                self.message_box_export.setText(self.message_box_export.text() + "Error: No setlist generated!\n")
                if self.debug:
                    print(f"Error: No setlist generated!")
            else:
                self.message_box_export.setText(self.message_box_export.text() + "Error: No file selected!\n")
                if self.debug:
                    print(f"Error: No file selected!")

    # Prints the available songs, includes, and excludes all to the "Includes/Excludes" tab
    def load_songs_from_csv(self):
        if self.song_file:
            self.available_songs = list(pd.read_csv(self.song_file)["Song"])
            # Clear the existing list items before adding new items
            self.available_songs_list.clear()

            for song in self.available_songs:
                item = QListWidgetItem(song)
                if song in self.included_songs:
                    item.setForeground(QColor("green"))
                elif song in self.excluded_songs:
                    item.setForeground(QColor("red"))
                self.available_songs_list.addItem(item)

            if self.debug:
                print(f"Loading songs from {self.song_file}")
        else:
            self.available_songs_list.clear()
            self.available_songs_list.addItem("No file selected")

    # The "Include" Button on the "Includes/Excludes" tab. Adds the selected songs to the included list
    def include_selected_songs(self):
        if self.song_file != "":
            selected_songs = self.available_songs_list.selectedItems()
            for song in selected_songs:
                if self.debug:
                    print(f"Including {song.text()}")
                if song.text() in self.excluded_songs: # If the song is in the excluded list, remove it
                    self.excluded_songs.remove(song.text())
                self.included_songs.append(song.text())
        self.load_songs_from_csv()

    # The "Exclude" Button on the "Includes/Excludes" tab. Adds the selected songs to the excluded list
    def exclude_selected_songs(self):
        if self.song_file != "":
            selected_songs = self.available_songs_list.selectedItems()
            for song in selected_songs:
                if self.debug:
                    print(f"Excluding {song.text()}")
                if song.text() in self.included_songs: # If the song is in the included list, remove it
                    self.included_songs.remove(song.text())
                self.excluded_songs.append(song.text())
        self.load_songs_from_csv()
    
    # The "Remove" Button on the "Includes/Excludes" tab. Removes the selected songs from either the included and excluded list
    def remove_selected_songs(self):
        if self.song_file != "":
            selected_songs = self.available_songs_list.selectedItems()
            for song in selected_songs:
                if self.debug:
                    print(f"Removing {song.text()}")
                if song.text() in self.included_songs: # If the song is in the included list, remove it
                    self.included_songs.remove(song.text())
                if song.text() in self.excluded_songs:
                    self.excluded_songs.remove(song.text())
        self.load_songs_from_csv()


    # This is the "Modify" Button on the "Includes/Excludes" tab. This takes all of the Includes and Excludes and changes the mood value in the csv file
    def modify_song_csv(self):
        df = pd.read_csv(self.song_file)
        if self.debug:
            print(f"Modifying {self.song_file}")
        for i in range(df.shape[0]):
            if df["Song"][i] in self.excluded_songs:
                if self.debug:
                    print(f"Excluding {df['Song'][i]}")
                df["Active"][i] = "False"
            else:
                df["Active"][i] = "True"
        df.to_csv(self.song_file, index=False)
        self.message_box_modify.clear()
        self.message_box_modify.setText(self.message_box_modify.text() + "Modified " + os.path.basename(self.song_file) + "!\n")
        self.load_songs_from_csv()

    # Gets called with the constructor after all the member variables are initialized. This sets up the layout of the entire UI
    def init_ui(self):

        # Window Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        tab_widget = QTabWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(tab_widget)
        central_widget.setLayout(central_layout)

        # Input File Entry
        self.input_file_entry = QLineEdit()
        browse_input_button = QPushButton("Browse")
        browse_input_button.setToolTip("Click to browse for input CSV file")
        browse_input_button.clicked.connect(self.browse_input_file)
        input_file_layout = QHBoxLayout()
        input_file_layout.addWidget(self.input_file_entry)
        input_file_layout.addWidget(browse_input_button)

        # Output File Entry
        self.output_file_entry = QLineEdit()
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.browse_output_file)
        browse_output_button.setToolTip("Click to find a place for the output file")
        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(self.output_file_entry)
        output_file_layout.addWidget(browse_output_button)

        # Tab 1: Make Setlist
        tab1 = QWidget()
        tab_widget.addTab(tab1, "Make Setlist")

        # OG Weight Entry
        self.og_weight_entry = QLineEdit()
        self.og_weight_entry.setPlaceholderText(str(self.defaults["og_weight"]))

        # Mood Weight Entry
        self.mood_weight_entry = QLineEdit()
        self.mood_weight_entry.setPlaceholderText(str(self.defaults["mood_weight"]))

        # Set Time Entry
        self.set_time_entry = QLineEdit()
        self.set_time_entry.setPlaceholderText(str(self.defaults["set_time"]))

        # Transition Time Entry
        self.transition_time_entry = QLineEdit()

        # Cluster Size Entry
        self.cluster_size_entry = QLineEdit()
        self.cluster_size_entry.setPlaceholderText(str(self.defaults["cluster_size"]))

        # Run Button
        run_button = QPushButton("Run")
        run_button.setToolTip("Generate Setlist")
        run_button.clicked.connect(self.update_setlist)

        # Setlist Generated Text
        self.setlist_generated_text = QTextEdit()
        self.setlist_generated_text.setReadOnly(True)

        # Layout for Tab 1
        tab1_layout = QVBoxLayout()
        tab1_layout.addWidget(QLabel("Input File:"))
        tab1_layout.addLayout(input_file_layout)
        tab1_layout.addWidget(QLabel("OG Weight:"))
        tab1_layout.addWidget(self.og_weight_entry)
        tab1_layout.addWidget(QLabel("Mood Weight:"))
        tab1_layout.addWidget(self.mood_weight_entry)
        tab1_layout.addWidget(QLabel("Set Time (minutes):"))
        tab1_layout.addWidget(self.set_time_entry)
        tab1_layout.addWidget(QLabel("Transition Time (minutes):"))
        tab1_layout.addWidget(self.transition_time_entry)
        tab1_layout.addWidget(QLabel("Cluster Size:"))
        tab1_layout.addWidget(self.cluster_size_entry)
        tab1_layout.addWidget(run_button)
        tab1_layout.addWidget(self.setlist_generated_text)
        tab1.setLayout(tab1_layout)

        # Tab 2: Setlist
        tab2 = QWidget()
        tab_widget.addTab(tab2, "View Setlist")

        # Setlist Text Box
        self.setlist_text_box = QTextEdit()
        self.setlist_text_box.setReadOnly(True)
        self.setlist_text_box.setStyleSheet("border: 1px solid black")

        # Setlist List
        self.setlist_list_box = QListWidget()
        self.setlist_list_box.setVisible(False)  # Hide the list initially
        self.setlist_list_box.setSelectionMode(QListWidget.ExtendedSelection)  # Enable multi-selection

        # Export Button
        export_button = QPushButton("Export to Output File")
        export_button.setToolTip("Export to Selected Output File")
        export_button.clicked.connect(self.export_to_output_file)

        # Feedback Text
        self.message_box_export = QLineEdit()
        self.message_box_export.setReadOnly(True)  # Set the text box to read-only

        # Buttons for "Text" and "List" views
        text_button = QPushButton("Text Mode")
        text_button.setToolTip("Show setlist as text")
        text_button.clicked.connect(self.show_setlist_text)
        list_button = QPushButton("List Mode")
        list_button.setToolTip("Show setlist as list")
        list_button.clicked.connect(self.show_setlist_list)

        # Horizontal Layout for Text and List Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(text_button)
        buttons_layout.addWidget(list_button)

        # Layout for Tab 2
        tab2_layout = QVBoxLayout()
        tab2_layout.addWidget(QLabel("Output File:"))
        tab2_layout.addLayout(output_file_layout)
        tab2_layout.addWidget(export_button)
        tab2_layout.addLayout(buttons_layout)
        tab2_layout.addWidget(self.setlist_text_box)
        tab2_layout.addWidget(self.setlist_list_box)
        tab2_layout.addWidget(self.message_box_export)
        tab2.setLayout(tab2_layout)

        # Tab 3: Available Songs
        tab3 = QWidget()
        tab_widget.addTab(tab3, "Includes/Excludes")

        # Available Songs List
        self.available_songs_list = QListWidget()
        self.available_songs_list.setSelectionMode(QListWidget.ExtendedSelection)  # Enable multi-selection
        self.load_songs_from_csv() # Init the list (although no CSV file is loaded yet)

        # Include and Exclude Buttons
        include_button = QPushButton("Include")
        include_button.setToolTip("Click to include selected songs in the setlist")
        include_button.clicked.connect(self.include_selected_songs)
        exclude_button = QPushButton("Exclude")
        exclude_button.setToolTip("Click to exclude selected songs from the setlist")
        exclude_button.clicked.connect(self.exclude_selected_songs)

        #Remove Button
        remove_button = QPushButton("Remove")
        remove_button.setToolTip("Click to remove selected songs from the includes/excludes list")
        remove_button.clicked.connect(self.remove_selected_songs)

        # Modify Button
        modify_button = QPushButton("Modify")
        modify_button.setToolTip("Click to modify the input CSV file according to the current includes/excludes list. \nExcludes are set to inactive while everything else is set to active.")
        modify_button.clicked.connect(self.modify_song_csv)

        # Feedback Text
        self.message_box_modify = QLineEdit()
        self.message_box_modify.setReadOnly(True)  # Set the text box to read-only

        # Layout for Tab 3
        tab3_layout = QVBoxLayout()
        tab3_layout.addWidget(self.available_songs_list)
        tab3_layout.addWidget(include_button)
        tab3_layout.addWidget(exclude_button)
        tab3_layout.addWidget(remove_button)
        tab3_layout.addWidget(modify_button)
        tab3_layout.addWidget(self.message_box_modify)
        tab3.setLayout(tab3_layout)

        # Show the main window
        self.show()