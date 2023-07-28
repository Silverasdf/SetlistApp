# Setlist Make (w/ GUI) - Makes a setlist based on the songs in a csv file, but hopefully usable to people that aren't me

# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active, Not in that order (I don't think)
# Ryan Peruski, 05/27/2023

import pandas as pd
import random
import warnings
import numpy as np
import tkinter as tk
from tkinter import filedialog
from setlist_math import make_setlist, sort_sample_into_clusters, write_setlist_to_file

def run_program():
    # Get the input values
    song_file = input_file_entry.get()
    setlist_file = output_file_entry.get()
    og_weight = float(og_weight_entry.get() or 1.2)
    mood_weight = float(mood_weight_entry.get() or 0.8)
    includes = includes_entry.get().split(",")
    set_time = float(set_time_entry.get() or 60)  # Set time in minutes
    transition_time = float(transition_time_entry.get() or set_time * 0.1)  # Transition time in minutes (10% of set time)
    cluster_size = int(cluster_size_entry.get() or 2)  # Cluster size

    # Main code
    try:
        songs = pd.read_csv(song_file)
        songs = songs.query('Active == True')
        warnings.filterwarnings("ignore")
        setlist = make_setlist(songs, target_time=set_time-transition_time, og_weight=og_weight, mood_weight=mood_weight, includes=includes)
        sorted_clusters = sort_sample_into_clusters(setlist, cluster_size=cluster_size)
        write_setlist_to_file(sorted_clusters, setlist_file)
        setlist_generated_text.delete("1.0", tk.END)  # Clear previous message
        setlist_generated_text.insert(tk.END, "Setlist generated!")
    except Exception as e:
        setlist_generated_text.delete("1.0", tk.END)
        setlist_generated_text.insert(tk.END, f"Error: {e}")


# Create the GUI window
window = tk.Tk()
window.title("Setlist Generator")

# Input File Path
input_file_label = tk.Label(window, text="Input File Path:")
input_file_label.pack()
input_file_entry = tk.Entry(window)
input_file_entry.pack()
input_file_button = tk.Button(window, text="Browse", command=lambda: input_file_entry.insert(tk.END, filedialog.askopenfilename()))
input_file_button.pack()

# Output File Path
output_file_label = tk.Label(window, text="Output File Path:")
output_file_label.pack()
output_file_entry = tk.Entry(window)
output_file_entry.pack()
output_file_button = tk.Button(window, text="Browse", command=lambda: output_file_entry.insert(tk.END, filedialog.asksaveasfilename()))
output_file_button.pack()

# OG Weight
og_weight_label = tk.Label(window, text="OG Weight (default 1.2):")
og_weight_label.pack()
og_weight_entry = tk.Entry(window)
og_weight_entry.pack()

# Mood Weight
mood_weight_label = tk.Label(window, text="Mood Weight (default 0.8):")
mood_weight_label.pack()
mood_weight_entry = tk.Entry(window)
mood_weight_entry.pack()

# Includes
includes_label = tk.Label(window, text="Includes (comma-separated):")
includes_label.pack()
includes_entry = tk.Entry(window)
includes_entry.pack()

# Set Time
set_time_label = tk.Label(window, text="Set Time (minutes) (default 60):")
set_time_label.pack()
set_time_entry = tk.Entry(window)
set_time_entry.pack()

# Transition Time
transition_time_label = tk.Label(window, text="Transition Time (minutes) (default: 10% of set time):")
transition_time_label.pack()
transition_time_entry = tk.Entry(window)
transition_time_entry.pack()

# Cluster Size
cluster_size_label = tk.Label(window, text="Cluster Size (default 2):")
cluster_size_label.pack()
cluster_size_entry = tk.Entry(window)
cluster_size_entry.pack()

# Run Button
run_button = tk.Button(window, text="Run", command=run_program)
run_button.pack()

# Setlist Generated Message
setlist_generated_text = tk.Text(window, height=1, width=30)
setlist_generated_text.pack()

# Start the GUI event loop
window.mainloop()

if __name__ == '__main__':
    run_program()