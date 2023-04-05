from collections import namedtuple
from typing import List, Optional, Tuple

import logging_config
from config import get_config
from constants import *
from constants import DEFAULT_SAMPLE_RATE
from entities import MuseSwiprMap, Note, Segment
from map_pattern_analysis import MapPatterns
from pattern_multipliers import pattern_stream_length_multiplier
from patterns.pattern import Pattern
from utils import weighted_average_of_values

logger = logging_config.logger
conf = get_config()

PatternScore = namedtuple("PatternScore", ["pattern_name", "score", "has_interval", "total_notes"])


def create_sections(notes, section_threshold_seconds=1, sample_rate: int = DEFAULT_SAMPLE_RATE):
    section_threshold = section_threshold_seconds * sample_rate
    song_start_samples = min(note.sample_time for note in notes)
    song_duration_samples = max(note.sample_time for note in notes)

    # First, sort the notes by sample_time
    notes.sort(key=lambda x: x.sample_time)

    # Calculate the number of sections based on song_duration_samples and section_threshold
    num_sections = int(
        (song_duration_samples - song_start_samples + section_threshold) // section_threshold
    )

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


def apply_multiplier_to_pattern_chunk(chunk, pattern_score: PatternScore):
    multiplier = 1
    if len(chunk) > 2:
        multiplier = pattern_stream_length_multiplier(pattern_score.total_notes)
    multiplied = [
        c_ps.score * multiplier if c_ps.pattern_name != ZIG_ZAG else c_ps.score for c_ps in chunk
    ]
    return multiplied


def calculate_scores_from_patterns(patterns: List[Pattern]) -> List[float]:
    pattern_scores = []
    for pattern in patterns:
        if pattern.segments:  # check if pattern has segments
            score = pattern.calc_pattern_difficulty()
            pattern_scores.append(
                PatternScore(
                    pattern.pattern_name,
                    score,
                    pattern.has_interval_segment,
                    pattern.total_notes,
                )
            )

    scores = []
    chunk = []
    for pattern_score in pattern_scores:
        if pattern_score.has_interval and chunk:
            multiplied = apply_multiplier_to_pattern_chunk(chunk, pattern_score)
            scores += multiplied
            chunk = []
        else:
            chunk.append(pattern_score)

    if chunk:
        multiplied = apply_multiplier_to_pattern_chunk(chunk, pattern_score)
        scores += multiplied

    return scores


def get_pattern_weighting(notes: List[Note], sample_rate: int = DEFAULT_SAMPLE_RATE) -> float:
    """Calculates the overall weighting of pattern difficulty

    Gets the Pattern's difficulty which::
    - accounts for Pattern multipliers
    - accounts for Pattern variation multiplier
    - accounts for Pattern length multiplier (If there is one, otherwise it's just 1)

    Then gets the average of them.

    Args:
        note List[Note]: A list of Notes in order of occurrence

    Returns:
        float: The pattern weighting
    """
    mpg = MapPatterns()
    segments = analyse_segments(notes, sample_rate)
    patterns = mpg.identify_patterns(segments)

    scores = calculate_scores_from_patterns(patterns)

    # Gets the average difficulty score across all the Patterns
    difficulty = weighted_average_of_values(
        scores,
        top_percentage=conf["get_pattern_weighting_top_percentage"],
        top_weight=conf["get_pattern_weighting_top_weight"],
        bottom_weight=conf["get_pattern_weighting_bottom_weight"],
    )
    logger.debug(f"{'WEIGHTED Average Difficulty Score:':>25} {difficulty}")

    return difficulty


def calculate_difficulty(notes, outfile=None, sample_rate: int = DEFAULT_SAMPLE_RATE):

    sections = create_sections(notes, conf["sample_window_secs"], sample_rate)

    moving_avg = moving_average_note_density(sections, conf["moving_avg_window"])
    if outfile:
        for s in moving_avg:
            outfile.write(f"{s}\n")
    difficulty = weighted_average_of_values(moving_avg)

    weighting = get_pattern_weighting(notes)
    weighted_difficulty = weighting * difficulty
    logger.info(
        f"Final Weighting: {weighting:<10.5f}| Base Difficulty: {difficulty:<10.5f}| Weighted Difficulty: {weighted_difficulty:<10.5f}"
    )
    return (weighting, difficulty, weighted_difficulty)


def get_next_segment_and_required_notes(
    prev_note: Note,
    note: Note,
    time_difference: int,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> Tuple[str, int]:
    notes_per_second = sample_rate / time_difference

    if notes_per_second >= conf["short_interval_nps"]:
        if note.lane != prev_note.lane:
            return ZIG_ZAG, 2
        else:
            return SINGLE_STREAMS, 2
    elif notes_per_second < conf["long_interval_nps"]:
        return LONG_INTERVAL, 0
    elif notes_per_second < conf["med_interval_nps"]:
        return MED_INTERVAL, 0
    elif notes_per_second < conf["short_interval_nps"]:
        return SHORT_INTERVAL, 0
    else:
        return OTHER, 0


def handle_current_segment(
    segments: List[Segment], current_segment: Optional[Segment]
) -> List[Segment]:
    if current_segment:
        if current_segment.segment_name == OTHER:
            segments.append(current_segment)
        elif len(current_segment.notes) >= current_segment.required_notes:
            if current_segment.segment_name == ZIG_ZAG and len(current_segment.notes) == 2:
                current_segment.segment_name = SWITCH
            elif current_segment.segment_name == SINGLE_STREAMS and len(current_segment.notes) < 5:
                current_segment.segment_name = f"{len(current_segment.notes)}-Stack"
            segments.append(current_segment)
    return segments


def analyse_segments(notes: List[Note], sample_rate: int = DEFAULT_SAMPLE_RATE):
    """
    Given a list of `Note` objects, detects segments in the sequence of notes and returns a list of `Segment` objects.

    Args:
        notes (List[Note]): A list of `Note` objects representing the sequence of notes to be analysed.

    Returns:
        A list of `Segment` objects, each representing a detected segment in the sequence of notes.
    """
    segments = []
    current_segment = None
    tolerance = conf["segment_tolerance_ms"] * sample_rate / 1000  # 10ms in sample time

    for i in range(1, len(notes)):  # Starts at second note
        prev_note = notes[i - 1]
        note = notes[i]

        time_difference = note.sample_time - prev_note.sample_time

        # Get the name of the next segment and the notes required to complete it
        next_segment_name, next_required_notes = get_next_segment_and_required_notes(
            prev_note, note, time_difference
        )

        # If the current pair of notes belongs to the same segment as the previous pair of notes
        if current_segment and current_segment.segment_name == next_segment_name:
            base_time_difference = (
                current_segment.notes[1].sample_time - current_segment.notes[0].sample_time
            )

            # If the time difference between the current pair of notes is within the tolerance of the base time difference of the current segmen
            if abs(time_difference - base_time_difference) <= tolerance:
                current_segment.notes.append(note)
            else:  # The time difference between the current pair of notes is not within the tolerance of the base time difference of the current segmen
                segments = handle_current_segment(segments, current_segment)
                current_segment = Segment(
                    next_segment_name,
                    [prev_note, note],
                    required_notes=next_required_notes,
                    time_difference=time_difference,
                    sample_rate=sample_rate,
                )
        else:  # If the current pair of notes does not belong to the same segmen as the previous pair of notes
            segments = handle_current_segment(segments, current_segment)
            current_segment = Segment(
                next_segment_name,
                [prev_note, note],
                required_notes=next_required_notes,
                time_difference=time_difference,
                sample_rate=sample_rate,
            )

    segments = handle_current_segment(segments, current_segment)

    return segments


# Generate output
def print_segments(segments: List[Segment], sample_rate: int = DEFAULT_SAMPLE_RATE):
    sorted_segments = sorted(segments, key=lambda segment: segment.notes[0].sample_time)

    logger.info(f"Sample rate: {sample_rate}")

    for segment in sorted_segments:
        start_time = segment.notes[0].sample_time
        end_time = segment.notes[1].sample_time
        time_difference = end_time - start_time
        notes_per_second = sample_rate / abs(
            segment.notes[1].sample_time - segment.notes[0].sample_time
        )

        logger.info(
            f"{time_difference / sample_rate:.2f} | {start_time/ sample_rate:.2f} - {end_time/ sample_rate:.2f}: "
            f"{segment.segment_name} ({notes_per_second:.2f}nps|{(notes_per_second/4)*60:.2f}BPM) | {segment.time_difference/sample_rate:.2f}s"
        )


if __name__ == "__main__":
    pass
