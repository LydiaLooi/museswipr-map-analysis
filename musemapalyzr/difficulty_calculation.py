from typing import List, Tuple

import config.logging_config as logging_config
from config.config import get_config
from musemapalyzr.constants import DEFAULT_SAMPLE_RATE, ZIG_ZAG
from musemapalyzr.entities import Note, Segment
from musemapalyzr.map_pattern_analysis import MapPatterns
from musemapalyzr.pattern_multipliers import pattern_stream_length_multiplier
from musemapalyzr.utils import (
    PatternScore,
    analyse_segments,
    create_sections,
    moving_average_note_density,
    weighted_average_of_values,
)
from patterns.pattern import Pattern

logger = logging_config.logger
conf = get_config()


def apply_multiplier_to_pattern_chunk(chunk, pattern_score: PatternScore) -> List[float]:
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


def calculate_difficulty(
    notes, outfile=None, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> Tuple[float, float, float]:

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


# Generate output
def print_segments(segments: List[Segment], sample_rate: int = DEFAULT_SAMPLE_RATE) -> None:
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