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


def calculate_difficulty(notes):
    # First, let's sort the notes by time
    notes = sorted(notes, key=lambda note: note.time)

    # Calculate the total time of the map in seconds
    total_time = notes[-1].time / 44100

    # We'll keep track of the total difficulty
    total_difficulty = 0

    # Initialize variables for penalty/buff amounts
    short_map_penalty = 0.25
    long_map_buff = 0.05
    chain_penalty = 1.5
    zigzag_buff = 1.25

    # Iterate over the notes to calculate difficulty
    for i in range(1, len(notes)):
        time_diff = (notes[i].time - notes[i-1].time) / 44100
        lane_diff = abs(notes[i].lane - notes[i-1].lane)

        # Penalize chains of notes in one lane that occur very quickly
        if lane_diff == 0 and time_diff < 0.05:
            total_difficulty += chain_penalty * (time_diff + lane_diff)
        else:
            total_difficulty += time_diff + lane_diff

    # Buff difficulty for maps longer than 3 minutes (with increasing buff for longer maps)
    if total_time > 180:
        time_factor = min((total_time - 180) / 60, 2.0)
        total_difficulty *= (1 + long_map_buff * time_factor)

    # Penalize difficulty for maps shorter than 30 seconds
    if total_time < 30:
        total_difficulty *= (1 - short_map_penalty)

    # Buff difficulty for sustained "zig zag" patterns that occur at a rate of at least 13 notes per second
    zigzag_count = 0
    zigzag_time = 0
    for i in range(1, len(notes)):
        time_diff = (notes[i].time - notes[i-1].time) / 44100
        lane_diff = abs(notes[i].lane - notes[i-1].lane)
        if lane_diff == 1 and time_diff < 0.08:
            zigzag_count += 1
            zigzag_time += time_diff
        else:
            if zigzag_count >= 13 and zigzag_time >= zigzag_count * 0.08:
                total_difficulty *= (1 + zigzag_buff)
            zigzag_count = 0
            zigzag_time = 0

    return 10 *(1 / (total_difficulty / (len(notes) - 1)))

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