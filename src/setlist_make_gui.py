# Setlist Make (w/ GUI) - Makes a setlist based on the songs in a csv file, but hopefully usable to people that aren't me

# Note: Csv file must have the following columns: Song, Artist, Key, Tuning, Time, Mood, Active, Not in that order (I don't think)
# Ryan Peruski, 05/27/2023

import pandas as pd
import random
import warnings
import numpy as np
import tkinter as tk
from tkinter import filedialog

# song_file = "electric_bluze/songs.csv"
# setlist_file = "electric_bluze/setlist.txt"
# target_time = 120
# time_allotted_for_transitions = 5
# og_weight = 1.5
# mood_weight = 0.5
# includes = []
# cluster_size = 2

def make_setlist(df, target_time, og_weight, mood_weight, includes):
    # Filter songs by "OG" artist
    includes = df[df['Song'].isin(includes)].index.tolist()
    og_songs = df[df['Artist'] == 'OG']
    og_count = len(og_songs)

    # Initialize variables
    sampled_songs = pd.DataFrame(columns=df.columns)
    total_time = 0.0
    sampled_indices = set()
    for i in includes:
        # Check if the song is in the dataframe
        if i not in df['Song']:
            warnings.warn('Song with index {} not found in dataframe'.format(i))
            continue
        # Check if the song has already been sampled
        if i in sampled_indices:
            warnings.warn('Song with index {} already sampled'.format(i))
            continue
        # Check if the song exceeds the remaining time needed
        if total_time + df.loc[i, 'Time'] > target_time:
            warnings.warn('Song with index {} exceeds remaining time'.format(i))
            continue
        # Append the song and update the total time and sampled indices
        sampled_songs = pd.concat([sampled_songs, df.loc[[i]]])
        total_time += df.loc[i, 'Time']
        sampled_indices.add(i)

    # Perform sequential sampling until the target time is reached
    while total_time < target_time:
        # Calculate the probabilities
        if og_count != 0:
            og_prob = og_count / (og_count + len(sampled_songs))
        else:
            og_prob = 0
        other_prob = 1 - og_prob

        # Calculate the weights based on the "Mood" values and OG weight
        df['Weight'] = df['Mood'] ** mood_weight
        og_songs['Weight'] = og_weight

        # Merge OG songs with the rest of the songs
        merged_songs = pd.concat([og_songs, df[df['Artist'] != 'OG']])

        # Filter out already sampled songs
        remaining_songs = merged_songs[~merged_songs.index.isin(sampled_indices)]

        # Check if there are remaining songs to sample
        if len(remaining_songs) == 0:
            break

        # Calculate the weights based on the "Mood" values and OG weight of the remaining songs
        weights = remaining_songs['Weight'] / remaining_songs['Weight'].sum()

        # Randomly sample a song based on the updated weights
        song = remaining_songs.sample(n=1, weights=weights)

        # Check if the song exceeds the remaining time needed
        if total_time + song['Time'].values[0] > target_time:
            break

        # Append the sampled song and update the total time and sampled indices
        sampled_songs = pd.concat([sampled_songs, song])
        total_time += song['Time'].values[0]
        sampled_indices.add(song.index[0])

    return sampled_songs.reset_index(drop=True)

def sort_sample_into_clusters(sample, cluster_size):
    # Convert 'Mood' column to numeric dtype
    sample['Mood'] = pd.to_numeric(sample['Mood'], errors='coerce')

    # Sort the sample by descending "Mood" values
    sorted_sample = sample.sort_values('Mood', ascending=False)

    # Split the sample into clusters of the specified size
    clusters = [sorted_sample[i:i+cluster_size] for i in range(0, len(sorted_sample), cluster_size)]

    # Check if the first cluster has high mood songs
    first_cluster = clusters[0]
    max_mood_first = first_cluster['Mood'].max()

    # If the maximum "Mood" value is not high, swap the first cluster with a cluster that has high mood songs
    if max_mood_first < 7:
        for i in range(1, len(clusters)):
            cluster = clusters[i]
            if cluster['Mood'].max() >= 8:
                clusters[0], clusters[i] = clusters[i], clusters[0]
                break

    # Swap songs within the first cluster so that the song with the highest mood is placed first
    if len(clusters) > 0:
        first_cluster = clusters[0]
        first_cluster = first_cluster.sort_values('Mood', ascending=False)
        clusters[0] = first_cluster

    # Shuffle the middle clusters
    if len(clusters) > 2:
        middle_clusters = clusters[1:-1]
        random.shuffle(middle_clusters)
        clusters[1:-1] = middle_clusters

    # Check if the last cluster has high mood songs
    last_cluster = clusters[-1]
    max_mood_last = last_cluster['Mood'].max()

    # If the maximum "Mood" value is not high, swap the last cluster with a cluster that has high mood songs
    if max_mood_last < 8:
        for i in range(len(clusters) - 2, -1, -1):
            cluster = clusters[i]
            if cluster['Mood'].max() >= 8:
                clusters[-1], clusters[i] = clusters[i], clusters[-1]
                break
    # Sort the songs within the last cluster by descending "Mood" values
    if len(clusters) > 1:
        last_cluster = clusters[-1]
        last_cluster = last_cluster.sort_values('Mood', ascending=True)
        clusters[-1] = last_cluster

    # Concatenate the clusters into a single DataFrame
    sorted_clusters = pd.concat(clusters)

    return sorted_clusters

def write_setlist_to_file(setlist, output_file):
    # Open the output file in write mode
    with open(output_file, 'w') as file:
        # Iterate over the setlist songs and write to the file
        for i in range(len(setlist)):
            song = setlist.iloc[i]

            # Check if the current song and the next song have the same key
            if i < len(setlist) - 1 and song['Key'] == setlist.iloc[i+1]['Key'] and song["Tuning"] == setlist.iloc[i+1]['Tuning'] and song["Key"] != "Misc":
                song_name = f"{song['Song']} -->"
            else:
                song_name = song['Song']

            # Check if the tuning is not "E Standard"
            if song['Tuning'] != "E Standard":
                song_name += f" ({song['Tuning']})"

            # Write the song name to the file
            file.write(song_name + '\n')


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