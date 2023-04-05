from collections import namedtuple
from typing import List, Optional, Tuple

from config.config import get_config
from constants import (
    DEFAULT_SAMPLE_RATE,
    LONG_INTERVAL,
    MED_INTERVAL,
    OTHER,
    SHORT_INTERVAL,
    SINGLE_STREAMS,
    SWITCH,
    ZIG_ZAG,
)
from entities import Note, Segment

conf = get_config()
PatternScore = namedtuple("PatternScore", ["pattern_name", "score", "has_interval", "total_notes"])


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


def weighted_average_of_values(values, top_percentage=0.3, top_weight=0.7, bottom_weight=0.3):
    if not values:
        raise ValueError("The input list 'values' cannot be empty.")

    # Find the threshold that separates the top 30% highest densities from the rest
    moving_averages_sorted = sorted(values, reverse=True)

    threshold_index = int(len(values) * (1 - top_percentage))
    if threshold_index >= len(moving_averages_sorted):
        threshold_index = len(moving_averages_sorted) - 1
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
