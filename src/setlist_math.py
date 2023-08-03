# Setlist Math - This file contains the functions that perform the calculations for the setlist generator.
# Ryan Peruski, 07/28/2023

import pandas as pd
import random
import warnings
import numpy as np
import tkinter as tk
from tkinter import filedialog

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

def write_setlist_string_to_file(setlist_string, output_file):
    # Open the output file in write mode
    with open(output_file, 'w') as file:
        file.write(setlist_string)

def write_setlist_to_string(setlist):
    # Iterate over the setlist songs and write to the file
    setlist_string = []
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

        # Write the song name to the string
        setlist_string.append(song_name + '\n')
    setlist_string = ''.join(setlist_string)
    return setlist_string[:-1] # Remove the last newline character

def write_setlist_to_list(setlist):
    # Iterate over the setlist songs and write to the file
    setlist_list = []
    for i in range(len(setlist)):
        song = setlist.iloc[i]
        setlist_list.append(song["Song"])
    return setlist_list

def show_active_songs(df):
    songs = []
    df = df[df['Active'] == True]
    for i, song in df.iterrows():
        songs.append(song['Song'])
    return songs