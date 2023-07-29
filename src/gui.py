# Setlist Make (w/ GUI) - Makes a setlist based on the songs in a csv file, but hopefully usable to people that aren't me

# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active, Not in that order (I don't think)
# Ryan Peruski, 05/27/2023

import pandas as pd
import random
import warnings
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QTabWidget, QHBoxLayout
from setlist_math import make_setlist, sort_sample_into_clusters, write_setlist_to_file

def browse_input_file(input_file_entry):
    file_path, _ = QFileDialog.getOpenFileName(None, "Select Songs File", "", "CSV Files (*.csv);;All Files (*)")
    input_file_entry.setText(file_path)

def browse_output_file(output_file_entry):
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Setlist File", "", "Text Files (*.txt);;All Files (*)")
    output_file_entry.setText(file_path)

def run_program(input_file_entry, output_file_entry, og_weight_entry, mood_weight_entry, includes_entry, set_time_entry, transition_time_entry, cluster_size_entry, setlist_generated_text):
    # Get user inputs
    song_file = input_file_entry.text()
    setlist_file = output_file_entry.text()
    og_weight = float(og_weight_entry.text() or 1.0)  # Default value if no input
    mood_weight = float(mood_weight_entry.text() or 1.0)  # Default value if no input
    includes = includes_entry.text().split(",")
    set_time = float(set_time_entry.text() or 60.0)  # Default value if no input
    transition_time = float(transition_time_entry.text() or 5.0)  # Default value if no input
    cluster_size = int(cluster_size_entry.text() or 5)  # Default value if no input
    
    # Rest of the code goes here
    # Main code
    try:
        songs = pd.read_csv(song_file)
        songs = songs.query('Active == True')
        warnings.filterwarnings("ignore")
        setlist = make_setlist(songs, target_time=set_time-transition_time, og_weight=og_weight, mood_weight=mood_weight, includes=includes)
        sorted_clusters = sort_sample_into_clusters(setlist, cluster_size=cluster_size)
        write_setlist_to_file(sorted_clusters, setlist_file)
        setlist_generated_text.clear()  # Clear previous message
        setlist_generated_text.append("Setlist generated!")
    except Exception as e:
        setlist_generated_text.clear()  # Clear previous message
        setlist_generated_text.append(f"Error: {e}!")

def init_gui():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Setlist Generator")

    # Create a central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Create a tab widget
    tab_widget = QTabWidget()
    central_layout = QVBoxLayout()
    central_layout.addWidget(tab_widget)
    central_widget.setLayout(central_layout)

    # Tab 1: Make Setlist
    tab1 = QWidget()
    tab_widget.addTab(tab1, "Make Setlist")

    # Input File Path
    input_file_label = QLabel("Input File Path:")
    input_file_entry = QLineEdit()
    browse_input_button = QPushButton("Browse")
    browse_input_button.clicked.connect(lambda: browse_input_file(input_file_entry))

    # Output File Path
    output_file_label = QLabel("Output File Path:")
    output_file_entry = QLineEdit()
    browse_output_button = QPushButton("Browse")
    browse_output_button.clicked.connect(lambda: browse_output_file(output_file_entry))

    # OG Weight
    og_weight_label = QLabel("OG Weight (default: 1.0):")
    og_weight_entry = QLineEdit()
    og_weight_entry.setText("1.0")

    # Mood Weight
    mood_weight_label = QLabel("Mood Weight (default: 1.0):")
    mood_weight_entry = QLineEdit()
    mood_weight_entry.setText("1.0")

    # Includes
    includes_label = QLabel("Includes (comma-separated):")
    includes_entry = QLineEdit()

    # Set Time
    set_time_label = QLabel("Set Time (minutes, default: 60.0):")
    set_time_entry = QLineEdit()
    set_time_entry.setText("60.0")

    # Transition Time
    transition_time_label = QLabel("Transition Time (minutes, default: 5.0):")
    transition_time_entry = QLineEdit()
    transition_time_entry.setText("5.0")

    # Cluster Size
    cluster_size_label = QLabel("Cluster Size (default: 5):")
    cluster_size_entry = QLineEdit()
    cluster_size_entry.setText("5")

    # Run Button
    run_button = QPushButton("Run")
    run_button.clicked.connect(lambda: run_program(input_file_entry, output_file_entry, og_weight_entry, mood_weight_entry, includes_entry, set_time_entry, transition_time_entry, cluster_size_entry, setlist_generated_text))

    # Setlist Generated Message
    setlist_generated_text = QTextEdit()
    setlist_generated_text.setReadOnly(True)

    # Layout for Tab 1
    tab1_layout = QVBoxLayout()
    input_layout = QHBoxLayout()
    input_layout.addWidget(input_file_label)
    input_layout.addWidget(input_file_entry)
    input_layout.addWidget(browse_input_button)
    tab1_layout.addLayout(input_layout)

    output_layout = QHBoxLayout()
    output_layout.addWidget(output_file_label)
    output_layout.addWidget(output_file_entry)
    output_layout.addWidget(browse_output_button)
    tab1_layout.addLayout(output_layout)

    tab1_layout.addWidget(og_weight_label)
    tab1_layout.addWidget(og_weight_entry)

    tab1_layout.addWidget(mood_weight_label)
    tab1_layout.addWidget(mood_weight_entry)

    tab1_layout.addWidget(includes_label)
    tab1_layout.addWidget(includes_entry)

    tab1_layout.addWidget(set_time_label)
    tab1_layout.addWidget(set_time_entry)

    tab1_layout.addWidget(transition_time_label)
    tab1_layout.addWidget(transition_time_entry)

    tab1_layout.addWidget(cluster_size_label)
    tab1_layout.addWidget(cluster_size_entry)

    tab1_layout.addWidget(run_button)

    tab1_layout.addWidget(setlist_generated_text)

    tab1.setLayout(tab1_layout)

    # Tab 2: Show Active Songs
    tab2 = QWidget()
    tab_widget.addTab(tab2, "Show Active Songs")
    # Add content for the second tab (Show Active Songs) here

    # Show the main window
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    init_gui()