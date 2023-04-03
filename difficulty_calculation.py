from typing import List, Tuple, Optional
import statistics
from constants import DEFAULT_SAMPLE_RATE
from constants import *
from entities import Note, MuseSwiprMap, Pattern
from pattern_multipliers import skewed_circle_multiplier, even_circle_multiplier, stream_multiplier, zig_zag_multiplier, nothing_but_theory_multiplier

from pattern_analysis import MapPatternGroups

def create_sections(notes, section_threshold_seconds=1, sample_rate:int=DEFAULT_SAMPLE_RATE):
    section_threshold = section_threshold_seconds * sample_rate
    song_start_samples = min(note.sample_time for note in notes)
    song_duration_samples = max(note.sample_time for note in notes)

    # First, sort the notes by sample_time
    notes.sort(key=lambda x: x.sample_time)

    # Calculate the number of sections based on song_duration_samples and section_threshold
    num_sections = int((song_duration_samples - song_start_samples + section_threshold) // section_threshold)

    # Initialize empty sections
    sections = [[] for _ in range(num_sections)]

    # Fill sections with notes
    for note in notes:
        section_index = int((note.sample_time - song_start_samples) // section_threshold)
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

def weighted_average_of_values(values, top_percentage=0.3, top_weight=0.7, bottom_weight=0.3):
    # Find the threshold that separates the top 30% highest densities from the rest
    threshold_index = int(len(values) * (1 - top_percentage))
    moving_averages_sorted = sorted(values, reverse=True)
    threshold = moving_averages_sorted[threshold_index]

    # Calculate the weighted average
    total_weight = 0
    weighted_sum = 0

    for avg in values:
        if avg >= threshold:
            weight = top_weight
        else:
            weight = bottom_weight

        weighted_sum += avg * weight
        total_weight += weight

    weighted_average = weighted_sum / total_weight
    return weighted_average

def get_pattern_weighting(notes: List[Note], sample_rate: int=DEFAULT_SAMPLE_RATE) -> float:
    """Calculates the overall weighting of pattern difficulty

    Gets the pattern group's difficulty which::
    - accounts for pattern group multipliers
    - accounts for pattern group variation multiplier
    - accounts for pattern group length multiplier

    Then gets the average of them.
    
    Args:
        note List[Note]: A list of Notes in order of occurrence

    Returns:
        float: The pattern weighting
    """
    mpg = MapPatternGroups()
    patterns = analyze_patterns(notes, sample_rate)
    groups = mpg.identify_pattern_groups(patterns)

    total_difficulty_score = 0
    scores = []

    for g in groups:
        score = g.calc_pattern_group_difficulty()
        total_difficulty_score += score
        scores.append(score)
    # Gets the average difficulty score across all the pattern groups
    difficulty = weighted_average_of_values(scores, top_percentage=0.4, top_weight=0.9, bottom_weight=0.1)
    average_difficulty_score = total_difficulty_score/len(groups)
    print(f"{'Average Difficulty Score:':>25} {average_difficulty_score}")
    print(f"{'WEIGHTED Average Difficulty Score:':>25} {difficulty}")

    return difficulty

def calculate_difficulty(notes, outfile=None, use_moving_average=True, sample_rate:int=DEFAULT_SAMPLE_RATE):

    print(f"{'Difficulty':_^50}")

    sections = create_sections(notes, 1, sample_rate)

    difficulty = None

    if use_moving_average is True:
        moving_avg = moving_average_note_density(sections, 5)
        if outfile:
            for s in moving_avg:
                outfile.write(f"{s}\n")
        difficulty = weighted_average_of_values(moving_avg)
    
    else:
        nums = []
        for s in sections:
            if outfile:
                outfile.write(f"{len(s)}\n")
            nums.append(len(s))
        difficulty = statistics.mean(nums)
    
    weighting = get_pattern_weighting(notes)
    print(f"{'':.^50}")
    weighted_difficulty = weighting * difficulty
    print(f"{'Final Weighting:':>25} {weighting}")
    print(f"{'Base Difficulty:':>25} {difficulty}")
    print(f"{'Weighted Difficulty:':>25} {weighted_difficulty}")
    print(f"{'':_^50}")
    
    return (weighting, difficulty, weighted_difficulty)


def get_next_pattern_and_required_notes(prev_note: Note, note: Note, time_difference: int, sample_rate:int=DEFAULT_SAMPLE_RATE) -> Tuple[str, int]:
    notes_per_second = sample_rate / time_difference

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


def analyze_patterns(notes: List[Note], sample_rate: int = DEFAULT_SAMPLE_RATE):
    """
    Given a list of `Note` objects, detects patterns in the sequence of notes and returns a list of `Pattern` objects.

    Args:
        notes (List[Note]): A list of `Note` objects representing the sequence of notes to be analyzed.

    Returns:
        A list of `Pattern` objects, each representing a detected pattern in the sequence of notes.
    """
    patterns = []
    current_pattern = None
    tolerance = 10 * sample_rate / 1000  # 10ms in sample time

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
                current_pattern = Pattern(next_pattern_name, [prev_note, note], required_notes=next_required_notes, time_difference=time_difference, sample_rate=sample_rate)
        else: # If the current pair of notes does not belong to the same pattern as the previous pair of notes
            patterns = handle_current_pattern(patterns, current_pattern)
            current_pattern = Pattern(next_pattern_name, [prev_note, note], required_notes=next_required_notes, time_difference=time_difference, sample_rate=sample_rate)

    patterns = handle_current_pattern(patterns, current_pattern)

    return patterns



# Generate output
def print_patterns(patterns: List[Pattern], sample_rate:int=DEFAULT_SAMPLE_RATE):
    sorted_patterns = sorted(patterns, key=lambda pattern: pattern.notes[0].sample_time)
    
    print(f"Sample rate: {sample_rate}")

    for pattern in sorted_patterns:
        start_time = pattern.notes[0].sample_time
        # print(f"FIRST NOTE: {pattern.notes[0].sample_time}")
        end_time = pattern.notes[1].sample_time
        # print(f"SECOND NOTE: {pattern.notes[1].sample_time}")
        time_difference = end_time - start_time
        notes_per_second = sample_rate / abs(pattern.notes[1].sample_time - pattern.notes[0].sample_time)

        print(
            f"{time_difference / sample_rate:.2f} | {start_time/ sample_rate:.2f} - {end_time/ sample_rate:.2f}: "
            f"{pattern.pattern_name} ({notes_per_second:.2f}nps|{(notes_per_second/4)*60:.2f}BPM) | {pattern.time_difference/sample_rate:.2f}s"
        )



if __name__ == "__main__":
    pass