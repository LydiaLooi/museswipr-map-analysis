from entities import Note, MuseSwiprMap, Pattern
from typing import List, Union, Tuple, Optional, Dict, Any
from pattern_analysis import MapPatternGroups
import os
import json
import statistics
from constants import TIME_CONVERSION
from constants import *

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"



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
    


def get_next_pattern_and_required_notes(prev_note: Note, note: Note, time_difference: int) -> Tuple[str, int]:
    notes_per_second = TIME_CONVERSION / time_difference

    if notes_per_second >= 5:
        if note.lane != prev_note.lane:
            return ZIG_ZAG, 2
        else:
            return SINGLE_STREAMS, 2
    elif notes_per_second < 0.5:
        return LONG_INTERVAL, 0
    elif notes_per_second < 1:
        return MED_INTERVAL, 0
    elif notes_per_second < 5:
        return SHORT_INTERVAL, 0
    else:
        return OTHER, 0


def handle_current_pattern(patterns: List[Pattern], current_pattern: Optional[Pattern]) -> List[Pattern]:
    if current_pattern:
        if current_pattern.pattern_name == OTHER:
            patterns.append(current_pattern)
        elif len(current_pattern.notes) >= current_pattern.required_notes:
            if current_pattern.pattern_name == ZIG_ZAG and len(current_pattern.notes) == 2:
                current_pattern.pattern_name = SWITCH
            elif current_pattern.pattern_name == SINGLE_STREAMS and len(current_pattern.notes) < 5:
                current_pattern.pattern_name = f"{len(current_pattern.notes)}-Stack"
            patterns.append(current_pattern)
    return patterns


def analyze_patterns(notes: List[Note]):
    """
    Given a list of `Note` objects, detects patterns in the sequence of notes and returns a list of `Pattern` objects.

    Args:
        notes (List[Note]): A list of `Note` objects representing the sequence of notes to be analyzed.

    Returns:
        A list of `Pattern` objects, each representing a detected pattern in the sequence of notes.
    """
    patterns = []
    current_pattern = None
    tolerance = 10 * TIME_CONVERSION / 1000  # 10ms in sample time

    for i in range(1, len(notes)): # Starts at second note
        prev_note = notes[i - 1]
        note = notes[i]

        time_difference = note.sample_time - prev_note.sample_time

        # Get the name of the next pattern and the notes required to complete it
        next_pattern_name, next_required_notes = get_next_pattern_and_required_notes(prev_note, note, time_difference)

        # If the current pair of notes belongs to the same pattern as the previous pair of notes
        if current_pattern and current_pattern.pattern_name == next_pattern_name:
            base_time_difference = current_pattern.notes[1].sample_time - current_pattern.notes[0].sample_time

            # If the time difference between the current pair of notes is within the tolerance of the base time difference of the current pattern
            if abs(time_difference - base_time_difference) <= tolerance:
                current_pattern.notes.append(note)
            else: # The time difference between the current pair of notes is not within the tolerance of the base time difference of the current pattern
                patterns = handle_current_pattern(patterns, current_pattern)
                current_pattern = Pattern(next_pattern_name, [prev_note, note], next_required_notes, time_difference)
        else: # If the current pair of notes does not belong to the same pattern as the previous pair of notes
            patterns = handle_current_pattern(patterns, current_pattern)
            current_pattern = Pattern(next_pattern_name, [prev_note, note], next_required_notes, time_difference)

    patterns = handle_current_pattern(patterns, current_pattern)

    return patterns



# Generate output
def print_patterns(patterns: List[Pattern]):
    for pattern in patterns:
        start_time = pattern.notes[0].sample_time
        end_time = pattern.notes[-1].sample_time
        time_difference = end_time - start_time
        notes_per_second = TIME_CONVERSION / abs(pattern.notes[1].sample_time - pattern.notes[0].sample_time)

        print(
            f"{time_difference / TIME_CONVERSION:.2f} | {start_time/ TIME_CONVERSION:.2f} - {end_time/ TIME_CONVERSION:.2f}: "
            f"{pattern.pattern_name} ({notes_per_second:.2f}nps|{(notes_per_second/4)*60:.2f}BPM) | {pattern.time_difference/TIME_CONVERSION:.2f}s"
        )

def mini_test():

    notes = [
        Note(1,5669300),
        Note(1,5679100),
        Note(0,5688900),
        Note(1,5695433),
        Note(0,5701966),
        Note(1,5708500),
        Note(0,5715033),
        Note(1,5721566),
        Note(0,5728100),
        Note(1,5747700),
        Note(1,5757500),
        Note(1,5767300),
        Note(0,5773833),
        Note(1,5780366),
        Note(0,5786900),
        Note(1,5793433),
        Note(0,5799966),
    ]

    p = analyze_patterns(notes)
    print_patterns(p)

def run_analysis():

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

    m = "nothing but theory"

    for filename in file_list:
        try:
            char = "\\"
            mpg = MapPatternGroups()
            m_map = MuseSwiprMap(filename)

            name = filename.split("\\")[-1].split(".asset")[0]
            if m in name.lower():
                # for n in m_map.notes:
                #     print(n)
                p = analyze_patterns(m_map.notes)
                groups = mpg.identify_pattern_groups(p)
                print(name)
                for g in groups:
                    print(g)
                print("=" * 25)
                # print_patterns(p)
                m_map.output_notes(f"{name}.txt")
        except Exception as e:
            print(f"error parsing file: {filename}: {e}")
            continue

if __name__ == "__main__":
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    # mini_test()
    run_analysis()

    
    # with open("difficulties.txt", "w", encoding="utf-8") as f:

    #     for filename in file_list:
    #         try:
    #             char = "\\"
    #             m_map = MuseSwiprMap(filename)

    #             name = filename.split("\\")[-1].split(".asset")[0]

    #             with open(f"analysis/{name}", "w", encoding="utf-8") as outfile:
    #                 f.write(f"{filename.split(char)[-1].split('.asset')[0]}||{calculate_difficulty(m_map.notes, filename, outfile):.2f}\n")
    #         except Exception as e:
    #             print(f"error parsing file: {filename}: {e}")
    #             continue
