from typing import List, Tuple, Optional
import statistics
from constants import TIME_CONVERSION
from constants import *
from entities import Note, MuseSwiprMap, Pattern
from pattern_multipliers import skewed_circle_multiplier, even_circle_multiplier, stream_multiplier, zig_zag_multiplier, nothing_but_theory_multiplier

from pattern_analysis import MapPatternGroups

def create_sections(notes, section_threshold_seconds):
    section_threshold = section_threshold_seconds * TIME_CONVERSION
    song_duration_samples = max(note.sample_time for note in notes)

    # First, sort the notes by sample_time
    notes.sort(key=lambda x: x.sample_time)

    # Calculate the number of sections based on song_duration_samples and section_threshold
    num_sections = int((song_duration_samples + section_threshold - 1) // section_threshold)

    # Initialize empty sections
    sections = [[] for _ in range(num_sections)]

    # Fill sections with notes
    for note in notes:
        section_index = int(note.sample_time // section_threshold)
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

def get_pattern_weighting(notes):
    mpg = MapPatternGroups()
    patterns = analyze_patterns(notes)
    groups = mpg.identify_pattern_groups(patterns)

    total_difficulty_score = 0

    for g in groups:
        score = g.calc_variation_score()
        total_difficulty_score += score
    
    average_difficulty_score = total_difficulty_score/len(groups)
    return average_difficulty_score

def calculate_difficulty(notes, outfile=None, use_moving_average=True):


    sections = create_sections(notes, 1)

    difficulty = None

    if use_moving_average is True:
        moving_avg = moving_average_note_density(sections, 5)
        if outfile:
            for s in moving_avg:
                outfile.write(f"{s}\n")
        difficulty = weighted_average_of_moving_averages(moving_avg)
    
    else:
        nums = []
        for s in sections:
            if outfile:
                outfile.write(f"{len(s)}\n")
            nums.append(len(s))
        difficulty = statistics.mean(nums)
    
    weighting = get_pattern_weighting(notes)

    print(f"{'Difficulty':_^50}")
    print(f"{'Weight:':>25} {weighting}")
    print(f"{'Base Difficulty:':>25} {difficulty}")
    print(f"{'Weighted Difficulty:':>25} {weighting * difficulty}")
    print(f"{'':_^50}")
    
    return difficulty


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



if __name__ == "__main__":
    from pattern_analysis import OtherGroup
    def _Note(lane, seconds):
        return Note(lane, seconds * TIME_CONVERSION)
    super_easier = [
        _Note(0, 0),
        _Note(0, 0.3),
        _Note(1, 0.6),
        _Note(0, 0.9),
        _Note(0, 1.2),
        _Note(0, 1.5),
        _Note(0, 1.9),
        _Note(0, 2.5),
        _Note(1, 3.5),
        _Note(0, 4),
        _Note(0, 4.3),
        _Note(0, 4.7),
        _Note(0, 5),
        _Note(0, 10),
        _Note(0, 10.3),
        _Note(1, 15),
    ]


    much_easier = [
        _Note(0, 0),
        _Note(1, 0.3),
        _Note(0, 0.6),
        _Note(1, 0.9),
        _Note(0, 1.2),
        _Note(1, 1.5),
        _Note(1, 1.9),
        _Note(0, 2.5),
        _Note(0, 3.5),
        _Note(1, 4),
        _Note(0, 4.3),
        _Note(0, 4.7),
        _Note(0, 5),
        _Note(1, 10),
        _Note(0, 10.3),
        _Note(0, 15),
    ]


    easier = [
        _Note(0, 0),
        _Note(1, 10),
        _Note(0, 10.1),
        _Note(1, 10.2),
        _Note(0, 12),
        _Note(1, 12.1),
        _Note(1, 15),
        _Note(0, 15.1),
        _Note(0, 20),
        _Note(1, 20.1),
        _Note(0, 20.2),
        _Note(0, 25),
        _Note(0, 25.1),
        _Note(1, 40),
        _Note(0, 40.1),
        _Note(0, 42),
    ]

    even_circles_easy = [
        _Note(1, 0.1),
        _Note(1, 0.2),
        _Note(0, 0.3),
        _Note(0, 0.4),
        _Note(1, 0.5),
        _Note(1, 0.6),
        _Note(0, 0.7),
        _Note(0, 0.8),
        _Note(1, 0.9),
        _Note(1, 1.0),
        _Note(0, 1.1),
        _Note(0, 1.2),
        _Note(1, 1.3),
        _Note(1, 1.4),
        _Note(0, 1.5),
        _Note(0, 1.6),
    ]

    even_circles_hard = [
        _Note(1, 0.1),
        _Note(1, 0.2),
        _Note(1, 0.3),
        _Note(0, 0.4),
        _Note(0, 0.5),
        _Note(1, 0.6),
        _Note(1, 0.7),
        _Note(1, 0.8),
        _Note(1, 0.9),
        _Note(0, 1.0),
        _Note(0, 1.1),
        _Note(0, 1.2),
        _Note(1, 1.3),
        _Note(1, 1.4),
        _Note(0, 1.5),
        _Note(0, 1.6),
    ]


    samples = {
        # 'super_easier': super_easier, 
        # 'much_easier': much_easier, 
        # 'easier': easier, 
        'even circles easy': even_circles_easy,
        'even circles hard': even_circles_hard
        }
    
    # for name, s in samples.items():
    #     print(f"{name.capitalize():=^50}")
    #     diff = calculate_difficulty(s)

    #     patterns = analyze_patterns(s)

    #     # print_patterns(patterns)
    #     print_patterns(patterns)
    #     mpg = MapPatternGroups()
    #     groups = mpg.identify_pattern_groups(patterns)
    #     for g in groups:
    #         print(f"{g.group_name}: {g.variation_score()}")

    #     print(f'{"=":=^50}\n')

    import math
    class Sample():
        def __init__(self, name, patterns):
            self.group_name = name
            self.patterns = patterns

        def variation_score(self) -> float:
            # Thanks to ChatGPT for writing this for me
            lst = [p.pattern_name for p in self.patterns]

            print(f"Pattern names: {lst}")
            n = len(lst)
            unique_vals = set(lst)
            freq = [lst.count(x) / n for x in unique_vals]

            entropy = -sum(p * math.log2(p) for p in freq)

            return entropy

    mpg = MapPatternGroups()

    even_patterns = [
        Pattern("A", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("B", []),
    ]

    odd_patterns = [
        Pattern("A", []),
        Pattern("B", []),
        Pattern("C", []),
        Pattern("B", []),
        Pattern("D", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("B", []),
    ]

    other_patterns = [
        Pattern("A", []),
        Pattern("A", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("B", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("B", []),
    ]
    

    same_patterns = [
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
        Pattern("A", []),
    ]


    almost_same_patterns = [
        Pattern("A", []),
        Pattern("B", []),
        Pattern("C", []),
        Pattern("B", []),
        Pattern("D", []),
        Pattern("A", []),
        Pattern("L", []),
        Pattern("C", []),
    ]

    groups = [
        Sample("Group A", even_patterns),
        Sample("Group B", odd_patterns),
        Sample("Group C", other_patterns),
        Sample("Group D", same_patterns),
        Sample("Group E", almost_same_patterns),
    ]

    for g in groups:
        print(f"{g.group_name}: {g.variation_score()}\n")

"""
1,1,1,0,0,1,1,1,1,0,0,0,1,1,0,0,

1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,




"""