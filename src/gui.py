# Setlist Make (w/ GUI) - Makes a setlist based on the songs in a csv file, but hopefully usable to people that aren't me

# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active, Not in that order (I don't think)
# Ryan Peruski, 05/27/2023

import pandas as pd
import random
import warnings
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QTabWidget, QHBoxLayout
from setlist_math import *

class SetlistGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.output_file_path = ""

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
        includes = self.includes_entry.text().split(",")
        set_time = float(self.set_time_entry.text() or self.defaults["set_time"])  # Default value if no input
        transition_time = float(self.transition_time_entry.text() or self.defaults["set_time"]*0.1)  # Default value if no input
        cluster_size = int(self.cluster_size_entry.text() or self.defaults["cluster_size"])  # Default value if no input
        #Reset random seed
        random.seed()
        
        # Main code
        try:
            songs = pd.read_csv(song_file)
            songs = songs.query('Active == True')
            warnings.filterwarnings("ignore")
            setlist = make_setlist(songs, target_time=set_time-transition_time, og_weight=og_weight, mood_weight=mood_weight, includes=includes)
            sorted_clusters = sort_sample_into_clusters(setlist, cluster_size=cluster_size)
            setlist_string = write_setlist_to_string(sorted_clusters)
            self.setlist_generated_text.clear()  # Clear previous message
            self.setlist_generated_text.append("Setlist generated!")
        except Exception as e:
            self.setlist_generated_text.clear()  # Clear previous message
            self.setlist_generated_text.append(f"Error: {e}!")
            setlist_string = ""

        return setlist_string

    def update_setlist_text(self):
        setlist_string = self.generate_setlist()
        print(setlist_string)
        self.setlist_text.clear()
        self.setlist_text.append(setlist_string)

    def export_to_output_file(self):
        setlist_string = self.generate_setlist()
        if self.output_file_path:
            with open(self.output_file_path, "w") as file:
                file.write(setlist_string)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        tab_widget = QTabWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(tab_widget)
        central_widget.setLayout(central_layout)

        # Tab 1: Make Setlist
        tab1 = QWidget()
        tab_widget.addTab(tab1, "Make Setlist")

        # Input File Entry
        self.input_file_entry = QLineEdit()
        browse_input_button = QPushButton("Browse")
        browse_input_button.clicked.connect(self.browse_input_file)
        input_file_layout = QHBoxLayout()
        input_file_layout.addWidget(self.input_file_entry)
        input_file_layout.addWidget(browse_input_button)

        # Output File Entry
        self.output_file_entry = QLineEdit()
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.browse_output_file)
        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(self.output_file_entry)
        output_file_layout.addWidget(browse_output_button)

        # OG Weight Entry
        self.og_weight_entry = QLineEdit()
        self.og_weight_entry.setPlaceholderText(str(self.defaults["og_weight"]))

        # Mood Weight Entry
        self.mood_weight_entry = QLineEdit()
        self.mood_weight_entry.setPlaceholderText(str(self.defaults["mood_weight"]))

        # Includes Entry
        self.includes_entry = QLineEdit()

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
        run_button.clicked.connect(self.update_setlist_text)

        # Setlist Generated Text
        self.setlist_generated_text = QTextEdit()
        self.setlist_generated_text.setReadOnly(True)

        # Layout for Tab 1
        tab1_layout = QVBoxLayout()
        tab1_layout.addWidget(QLabel("Input File:"))
        tab1_layout.addLayout(input_file_layout)
        tab1_layout.addWidget(QLabel("Output File:"))
        tab1_layout.addLayout(output_file_layout)
        tab1_layout.addWidget(QLabel("OG Weight:"))
        tab1_layout.addWidget(self.og_weight_entry)
        tab1_layout.addWidget(QLabel("Mood Weight:"))
        tab1_layout.addWidget(self.mood_weight_entry)
        tab1_layout.addWidget(QLabel("Includes (comma-separated):"))
        tab1_layout.addWidget(self.includes_entry)
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
        tab_widget.addTab(tab2, "Setlist")

        # Setlist Text
        self.setlist_text = QTextEdit()
        self.setlist_text.setReadOnly(True)

        # Export Button
        export_button = QPushButton("Export to Output File")
        export_button.clicked.connect(self.export_to_output_file)

        # Layout for Tab 2
        tab2_layout = QVBoxLayout()
        tab2_layout.addWidget(self.setlist_text)
        tab2_layout.addWidget(export_button)
        tab2.setLayout(tab2_layout)

        # Show the main window
        self.show()