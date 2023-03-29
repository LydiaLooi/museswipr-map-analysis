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
        with open(f"{koreograph_asset_filename}", "r") as f:
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

    # We'll keep track of the total difficulty
    total_difficulty = 0

    # Now we can calculate the difficulty of each note by looking at the time
    # difference between it and the previous note, as well as the distance between
    # the two notes on the playfield
    for i in range(1, len(notes)):
        time_diff = notes[i].time - notes[i-1].time
        lane_diff = abs(notes[i].lane - notes[i-1].lane)
        difficulty = time_diff + lane_diff
        total_difficulty += difficulty

    # Finally, we'll return the average difficulty per note
    return 100000 *(1 / (total_difficulty / (len(notes) - 1)))

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
    
    with open("difficulties.txt", "w") as f:

        for filename in file_list:
            try:
                char = "\\"
                m_map = MuseSwiprMap(filename)
                f.write(f"{filename.split(char)[-1].split('.asset')[0]}, {calculate_difficulty(m_map.notes):.2f}\n")
            except Exception as e:
                print(f"error parsing file: {filename}: {e}")
                continue