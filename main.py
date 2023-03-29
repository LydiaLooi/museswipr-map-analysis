from typing import List
import os
import json

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"

class Note:
    def __init__(self, lane, time):
        self.lane = lane
        self.time = time

    def __repr__(self):
        return f"{self.lane},{self.time}"

class MuseSwiprMap:
    def __init__(self, koreograph_asset_filename):

        data = None
        with open(f"{koreograph_asset_filename}", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.title = list(data.keys())[0]
        self.tempo_sections = data[self.title]["value"]["mTempoSections"]
        self.tracks = data[self.title]["value"]["mTracks"]
        self.notes = []

        self._parse_notes()

    def _parse_notes(self):
        for t in self.tracks:
            note_times_data = t["mEventList"]
            for d in note_times_data:
                assert d["mStartSample"] == d["mEndSample"]
                if t["mEventID"] != "TimingPoint":
                    note = Note(int(t["mEventID"]), d["mStartSample"])
                    self.notes.append(note)
        
        self.notes = sorted(self.notes, key=lambda note: note.time)

    def output_notes(self, file_path):
        """
        Written by ChatGPT. May have errors but it's neat :)
        """
        notes = self.notes
        # Find the smallest time distance between notes
        smallest_time_distance = min(note2.time - note1.time for note1, note2 in zip(notes, notes[1:]))
        
        # Sort the notes by descending time order
        sorted_notes = sorted(notes, key=lambda note: note.time, reverse=True)
        
        # Get the range of time values to iterate over
        start_time = sorted_notes[-1].time
        end_time = sorted_notes[0].time + smallest_time_distance
        time_range = range(start_time, end_time, smallest_time_distance)
        
        # Write the output to the file
        with open(file_path, 'w') as file:
            for time in reversed(time_range):
                for note in sorted_notes:
                    if note.time <= time < note.time + smallest_time_distance:
                        if note.lane == 0:
                            file.write("[]\n")
                        elif note.lane == 1:
                            file.write("     []\n")
                        break
                else:
                    file.write("\n")

import itertools
def calculate_difficulty(notes):
    if not notes:
        return 0

    TIME_CONVERSION = 44100
    MINIMUM_MAP_TIME = 30
    LONG_MAP_TIME = 180

    time_sec = [note.time / TIME_CONVERSION for note in notes]
    time_diff = [time_sec[i + 1] - time_sec[i] for i in range(len(time_sec) - 1)]
    total_duration = time_sec[-1] - time_sec[0]

    # Penalize short maps
    if total_duration < MINIMUM_MAP_TIME:
        difficulty_penalty = 0.5
    else:
        difficulty_penalty = 1

    # Buff long maps
    if total_duration > LONG_MAP_TIME:
        difficulty_buff = 1 + 0.005 * (total_duration - LONG_MAP_TIME)
    else:
        difficulty_buff = 1

    # Penalize chains of notes in one lane occurring quickly
    chain_penalty = 1
    for t, group in itertools.groupby(time_diff):
        count = len(list(group))
        if count > 3 and t <= 0.05:
            chain_penalty *= 0.95

    # # Penalize chains of notes in one lane occurring quickly
    # chain_penalty = 0
    # for t, group in itertools.groupby(time_diff):
    #     count = len(list(group))
    #     if count > 3 and t <= 0.05:
    #         chain_penalty += count * 0.1

    # Modify buff for zig-zag patterns with exponential scaling for 13 to 20 notes per second
    zig_zag_buff = 0
    zig_zag_count = 0
    for i in range(len(notes) - 2):
        if (notes[i].lane != notes[i + 1].lane) and (notes[i + 1].lane != notes[i + 2].lane):
            zig_zag_count += 1
        else:
            zig_zag_count = 0

        if zig_zag_count >= 3 and time_diff[i] <= 1 / 13:
            note_rate = 1 / time_diff[i]
            zig_zag_scale = max(min((note_rate - 13) / (20 - 13), 1), 0)
            zig_zag_buff += 0.1 * (1 + zig_zag_scale) ** 2

            
    # Calculate difficulty
    base_difficulty = sum(time_diff) / len(time_diff)
    difficulty = (base_difficulty * difficulty_penalty * chain_penalty) * difficulty_buff + zig_zag_buff

    interest = ["everything will free", "world's end val", "big black", "grin", ]

    for i in interest:
        if i in filename.lower():
            print(filename)
            print(f"chain_penalty: {chain_penalty}")
            print(f"zig_zag_buff: {zig_zag_buff}")
            print(f"base_difficulty: {base_difficulty}")
            print(f"difficulty_penalty: {difficulty_penalty}")
            print(f"difficulty_buff: {difficulty_buff}")
            print(f"difficluty: {difficulty}")
            # print(f"v1 value: {actual_notes(notes)}")
            print()

    return difficulty


if __name__ == "__main__":
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    # filter out any non-file entries
    file_list = []

    # walk through all the directories and files in the specified path
    for root, directories, files in os.walk(DATA_DIR):
        for filename in files:
            # construct the full file path
            file_path = os.path.join(root, filename)
            # append the file path to the list
            file_list.append(file_path)
    
    with open("difficulties.txt", "w", encoding="utf-8") as f:

        for filename in file_list:
            try:
                char = "\\"
                m_map = MuseSwiprMap(filename)
                f.write(f"{filename.split(char)[-1].split('.asset')[0]}, {calculate_difficulty(m_map.notes):.2f}\n")
            except Exception as e:
                print(f"error parsing file: {filename}: {e}")
                continue