from typing import List
import os
import json
import statistics

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"
TIME_CONVERSION = 44100 # time_s * TIME_CONVERSION = sample_time

class Note:
    def __init__(self, lane, sample_time):
        self.lane = lane
        self.sample_time = sample_time

    def __repr__(self):
        return f"{self.lane},{self.sample_time}"

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
        
        self.notes = sorted(self.notes, key=lambda note: note.sample_time)

    def output_notes(self, file_path):
        """
        Written by ChatGPT. May have errors but it's neat :)
        """
        notes = self.notes
        # Find the smallest time distance between notes
        smallest_time_distance = min(note2.sample_time - note1.sample_time for note1, note2 in zip(notes, notes[1:]))
        
        # Sort the notes by descending time order
        sorted_notes = sorted(notes, key=lambda note: note.sample_time, reverse=True)
        
        # Get the range of time values to iterate over
        start_time = sorted_notes[-1].sample_time
        end_time = sorted_notes[0].sample_time + smallest_time_distance
        time_range = range(start_time, end_time, smallest_time_distance)
        
        # Write the output to the file
        with open(file_path, 'w') as file:
            for time in reversed(time_range):
                for note in sorted_notes:
                    if note.sample_time <= time < note.sample_time + smallest_time_distance:
                        if note.lane == 0:
                            file.write("[]\n")
                        elif note.lane == 1:
                            file.write("     []\n")
                        break
                else:
                    file.write("\n")


def create_sections(notes, section_threshold_seconds):
    section_threshold = section_threshold_seconds * TIME_CONVERSION
    song_duration_samples = max(note.sample_time for note in notes)

    # First, sort the notes by sample_time
    notes.sort(key=lambda x: x.sample_time)

    # Calculate the number of sections based on song_duration_samples and section_threshold
    num_sections = (song_duration_samples + section_threshold - 1) // section_threshold

    # Initialize empty sections
    sections = [[] for _ in range(num_sections)]

    # Fill sections with notes
    for note in notes:
        section_index = note.sample_time // section_threshold
        if 0 <= section_index < len(sections):
            sections[section_index].append(note)

    return sections


def moving_average_note_density(sections, window_size):
    num_sections = len(sections)
    note_densities = [len(section) for section in sections]
    moving_averages = []

    for i in range(num_sections):
        start = max(0, i - window_size + 1)
        end = i + 1
        window = note_densities[start:end]
        average = sum(window) / len(window)
        moving_averages.append(average)

    return moving_averages

def weighted_average_of_moving_averages(moving_averages, top_percentage=0.3, top_weight=0.7, bottom_weight=0.3):
    # Find the threshold that separates the top 30% highest densities from the rest
    threshold_index = int(len(moving_averages) * (1 - top_percentage))
    moving_averages_sorted = sorted(moving_averages, reverse=True)
    threshold = moving_averages_sorted[threshold_index]

    # Calculate the weighted average
    total_weight = 0
    weighted_sum = 0

    for avg in moving_averages:
        if avg >= threshold:
            weight = top_weight
        else:
            weight = bottom_weight

        weighted_sum += avg * weight
        total_weight += weight

    weighted_average = weighted_sum / total_weight
    return weighted_average

def calculate_difficulty(notes, filename, outfile, use_moving_average=True):


    sections = create_sections(notes, 1)

    # TODO: Look into stretches of high density
    # TODO: Look at outliers of density - see if it is throughout or just a little bit skewing the difficulty
    # TODO: Look into pattern variety (look at the column diffs)

    if use_moving_average is True:
        moving_avg = moving_average_note_density(sections, 5)
        for s in moving_avg:
            outfile.write(f"{s}\n")
        # return statistics.mean(moving_avg)
        return weighted_average_of_moving_averages(moving_avg)
    
    else:
        nums = []
        for s in sections:
            outfile.write(f"{len(s)}\n")
            nums.append(len(s))
        return statistics.mean(nums)


if __name__ == "__main__":


    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    # filter out any non-file entries
    file_list = []

    # maps_of_interest = ["kill the beat", "nothing but theory", "gimme da blood", "surf", "big black", "everything will freeze"]
    # maps_of_interest = ["surf"]

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

                name = filename.split("\\")[-1].split(".asset")[0]

                with open(f"analysis/{name}", "w", encoding="utf-8") as outfile:
                    f.write(f"{filename.split(char)[-1].split('.asset')[0]}||{calculate_difficulty(m_map.notes, filename, outfile):.2f}\n")
            except Exception as e:
                print(f"error parsing file: {filename}: {e}")
                continue
