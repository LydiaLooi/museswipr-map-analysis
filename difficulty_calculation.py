from typing import List, Tuple, Optional
import statistics
from constants import TIME_CONVERSION
from constants import *
from entities import Note, MuseSwiprMap, Pattern

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

    for g in groups:
        print(g)

    print()

    total_difficulty_score = 0

    for g in groups:
        score = g.get_difficulty_score()
        total_difficulty_score += score
    
    average_difficulty_score = total_difficulty_score/len(groups)
    return average_difficulty_score

def calculate_difficulty(notes, filename=None, outfile=None, use_moving_average=True):


    sections = create_sections(notes, 1)

    # TODO: Look into stretches of high density
    # TODO: Look into pattern variety (look at the column diffs)

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

    print(f'{"="*20} DIFFICULTY {"="*20}')
    print(f"Weight: {weighting}")
    print(f"Difficulty: {difficulty}")
    print(f"Weighted: {weighting * difficulty}")
    print("="*20)
    
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

    harder = [
        _Note(0, 0),
        _Note(1, 0.1),
        _Note(1, 0.25),
        _Note(0, 0.3),
        _Note(1, 0.4),
        _Note(1, 0.55),
        _Note(0, 0.7),
        _Note(1, 0.8),
        _Note(0, 0.95),
        _Note(1, 1.1),
        _Note(0, 1.25),
        _Note(1, 1.35),
        _Note(0, 1.5),
        _Note(1, 5),
        _Note(0, 5.1),
        _Note(1, 5.15),
    ]



    diff = calculate_difficulty(easier)
    # # print()
    # diff = calculate_difficulty(harder)

    # patterns = analyze_patterns(harder)
    # print_patterns(patterns)
    # mpg = MapPatternGroups()
    # groups = mpg.identify_pattern_groups(patterns)
    # for g in groups:
        # print(g)

    diff = calculate_difficulty(harder)