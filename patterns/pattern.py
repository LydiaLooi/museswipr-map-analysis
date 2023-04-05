from typing import Dict, List, Optional

import config.logging_config as logging_config
from config.config import get_config
from musemapalyzr.constants import (
    DEFAULT_SAMPLE_RATE,
    FOUR_STACK,
    LONG_INTERVAL,
    MED_INTERVAL,
    SHORT_INTERVAL,
    SINGLE_STREAMS,
    SWITCH,
    THREE_STACK,
    TWO_STACK,
    ZIG_ZAG,
)
from musemapalyzr.entities import Segment

logger = logging_config.logger
conf = get_config()


class Pattern:
    def __init__(
        self,
        pattern_name: str,
        segments: List[Segment],
        start_sample: int = None,
        end_sample: int = None,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ):
        self.pattern_name = pattern_name
        self.segments = segments
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.is_active = True

        self.sample_rate = sample_rate
        self.tolerance = conf["pattern_tolerance_ms"] * sample_rate // 1000

        self.variation_weighting = conf["default_variation_weighting"]
        self.pattern_weighting = conf["default_pattern_weighting"]

        self.intervals = {
            SHORT_INTERVAL: conf["short_int_debuff"],
            MED_INTERVAL: conf["med_int_debuff"],
            LONG_INTERVAL: conf["long_int_debuff"],
        }

        self.end_extra_debuff = conf["extra_int_end_debuff"]

        # Use composition to add functionality
        self.check_segment_strategy = None
        self.is_appendable_strategy = None
        self.calc_variation_score_strategy = None
        self.calc_pattern_multiplier_strategy = None
        self.calc_pattern_length_multiplier_strategy = None

        self._total_notes = None

    @property
    def total_notes(self):
        if self._total_notes:
            return self._total_notes
        count = 0
        unique_timestamps = set()
        for segment in self.segments:
            for note in segment.notes:
                if note.sample_time not in unique_timestamps:
                    count += 1
                    unique_timestamps.add(note.sample_time)

        self._total_notes = count
        return self._total_notes

    @property
    def has_interval_segment(self):
        for seg in self.segments:
            if "Interval" in seg.segment_name:
                return True
        return False

    # General helper methods
    def is_n_stack(self, segment: Segment):
        return segment.segment_name in ("2-Stack", "3-Stack", "4-Stack")

    def segment_is_interval(self, segment: Segment):
        if segment:
            return "Interval" in segment.segment_name
        return False

    def time_difference_is_tolerable(self, previous_segment: Segment, current_segment: Segment):
        assert previous_segment.time_difference is not None
        assert current_segment.time_difference is not None

        # If the previous or current segment is an Interval, return True
        if self.segment_is_interval(previous_segment) or self.segment_is_interval(current_segment):
            return True

        result = (
            abs(current_segment.time_difference - previous_segment.time_difference)
            <= self.tolerance
        )

        return result

    def interval_between_segments_is_tolerable(
        self, previous_segment: Segment, current_segment: Segment
    ) -> bool:
        assert len(previous_segment.notes) > 1
        assert len(current_segment.notes) > 1
        # If the previous or current segment is an Interval, return True
        if self.segment_is_interval(previous_segment) or self.segment_is_interval(current_segment):
            return True
        end_of_first = previous_segment.notes[-1].sample_time
        start_of_second = current_segment.notes[0].sample_time
        time_difference = abs(end_of_first - start_of_second)
        if time_difference <= self.tolerance:
            # The segments pretty much have the same note
            return True
        return False

    def reset_group(self, previous_segment: Segment, current_segment: Segment):
        self.is_active = True
        self.segments = []

        # If previous or current_segment is an Interval, then only add that one (prioritise the latest one).
        if self.segment_is_interval(current_segment):
            self.check_segment(current_segment)

        elif self.segment_is_interval(previous_segment):
            self.check_segment(previous_segment)
            self.check_segment(current_segment)

        # If not, then attempt to add the previous one first, then the current one too
        # If it fails at any point, set the group to inactive
        else:
            if previous_segment:
                added = self.check_segment(previous_segment)
                if added:
                    added = self.check_segment(current_segment)

                if added is False:
                    self.is_active = False

    def add_interval_is_at_start(self, interval_segment: Segment) -> bool:
        """
        Adds the interval segment to the segments list
        Returns True if it is the first element
        Returns False if is not
        """
        if len(self.segments) == 0:
            self.segments.append(interval_segment)
            return True
        else:
            self.segments.append(interval_segment)
            return False

    def _get_segment_type_counts(self, segment_names):
        segment_counts = {
            SWITCH: 0,
            ZIG_ZAG: 0,
            TWO_STACK: 0,
            THREE_STACK: 0,
            FOUR_STACK: 0,
            SINGLE_STREAMS: 0,
            SHORT_INTERVAL: 0,
            MED_INTERVAL: 0,
            LONG_INTERVAL: 0,
        }
        for name in segment_names:
            segment_counts[name] += 1
        return segment_counts

    def _calc_switch_debuff(self, segment_counts: Dict[str, int], entropy: float) -> float:
        """Looks at the number of switches with relation to how many segments there are.

        A low segment count (<4) such as [zig zag, switch, zig zag] will be debuffed
        more heavily than a long arrangement of segments with more switches. A higher
        switch proportion results in less debuff.

        Args:
            segment_counts (Dict[str: int]): The dictionary of segment type counts
            entropy (float): The current entropy value

        Returns:
            float: The entropy affected by the debuff
        """
        switch_proportion = None
        switch_count = segment_counts[SWITCH]
        total_patterns = sum(segment_counts.values())
        if entropy > 1 and switch_count > 0:

            if total_patterns < 4:

                switch_debuff = 0.7
            else:

                switch_proportion = switch_count / total_patterns
                if switch_proportion < 0.5:

                    switch_debuff = 0.8
                else:
                    switch_debuff = (
                        0.9  # if there are more switches, then don't make the buff as hard
                    )
            logger.debug(
                f">>> Switch (proportion {switch_proportion}) debuff by {switch_debuff:.2f} <<<"
            )
            entropy *= switch_debuff
        return entropy

    def calc_pattern_difficulty(self) -> float:
        logger.debug(f"{self.pattern_name:.>25} {'Difficulty':.<25}")
        variation_multiplier = self.calc_variation_score()
        pattern_multiplier = self.calc_pattern_multiplier()

        final = (self.variation_weighting * variation_multiplier) + (
            self.pattern_weighting * pattern_multiplier
        )

        logger.debug(f"{'Variation Multiplier:':>25} {variation_multiplier}")
        logger.debug(f"{'Pattern Multiplier:':>25} {pattern_multiplier}")
        logger.debug(f"{'After Weighting:':>25} {final}")

        return final

    # Strategy setters
    def set_check_segment_strategy(self, strategy):
        self.check_segment_strategy = strategy

    def set_is_appendable_strategy(self, strategy):
        self.is_appendable_strategy = strategy

    def set_calc_variation_score_strategy(self, strategy):
        self.calc_variation_score_strategy = strategy

    def set_calc_pattern_multiplier_strategy(self, strategy):
        self.calc_pattern_multiplier_strategy = strategy

    def set_calc_pattern_length_multiplier_strategy(self, strategy):
        self.calc_pattern_length_multiplier_strategy = strategy

    # Use strategy pattern to delegate method calls
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        return self.check_segment_strategy.check_segment(current_segment)

    def is_appendable(self) -> bool:
        return self.is_appendable_strategy.is_appendable()

    def calc_variation_score(self) -> float:
        return self.calc_variation_score_strategy.calc_variation_score()

    def calc_pattern_multiplier(self) -> float:
        return self.calc_pattern_multiplier_strategy.calc_pattern_multiplier()

    def calc_pattern_length_multiplier(self) -> float:
        return self.calc_pattern_length_multiplier_strategy.calc_pattern_length_multiplier()

    def __repr__(self) -> str:
        if len(self.segments) >= 5:
            p = self.segments[:5]
            extra = f" | Last Five: {self.segments[-5:]}... ({len(self.segments)} total)"
        else:
            p = self.segments
            extra = ""
        if len(self.segments) > 0:
            return f"{self.segments[0].notes[0].sample_time/DEFAULT_SAMPLE_RATE:.2f} | {self.pattern_name}, {p}{extra}"
        else:
            return f"{self.pattern_name}, {p}"
