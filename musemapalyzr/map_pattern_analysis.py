from typing import List, Optional

from config.logging_config import logger
from musemapalyzr.constants import (
    EVEN_CIRCLES,
    FOUR_STACK,
    NOTHING_BUT_THEORY,
    OTHER,
    SKEWED_CIRCLES,
    SLOW_STRETCH,
    THREE_STACK,
    TWO_STACK,
    VARYING_STACKS,
)
from musemapalyzr.entities import Segment
from patterns.even_circles import EvenCirclesGroup
from patterns.nothing_but_theory import NothingButTheoryGroup
from patterns.other import OtherPattern
from patterns.pattern import Pattern
from patterns.skewed_circles import SkewedCirclesGroup
from patterns.slow_stretch import SlowStretchPattern
from patterns.varying_stacks import VaryingStacksPattern


class Mapalyzr:
    def __init__(self):
        # **THE** list of Patterns
        self.patterns: List[Pattern] = []

        # Keeps track during analysis of whether a pattern has been appended
        self.pattern_appended: bool = False
        self.pattern_appended_name: str = ""

        self.groups = []

        self.other_pattern: OtherPattern = OtherPattern(OTHER, [])
        self.reset_groups()

        self.added = False
        self.reset = False

    def is_n_stack(self, segment: Segment):
        return segment.segment_name in (TWO_STACK, THREE_STACK, FOUR_STACK)

    def segment_is_interval(self, pattern: Segment):
        return "Interval" in pattern.segment_name

    def reset_groups(self):
        self.groups = [
            EvenCirclesGroup(EVEN_CIRCLES, []),
            SkewedCirclesGroup(SKEWED_CIRCLES, []),
            VaryingStacksPattern(VARYING_STACKS, []),
            NothingButTheoryGroup(NOTHING_BUT_THEORY, []),
            SlowStretchPattern(SLOW_STRETCH, []),
        ]
        self.other_pattern = OtherPattern(OTHER, [])

    def _return_final_patterns(self, merge_mergable=True) -> List[Pattern]:
        """
        Returns the final list of Patterns after merging, if merge_patterns is True.
        Merges Other patterns
        Merges Slow Stretch patterns
        Note that these have different merging strategies
        """
        logger.debug(f"_return_final_patterns : {merge_mergable}")
        logger.debug(
            f"Patterns ({len(self.patterns)}): {[f'{p.pattern_name} ({len(p.segments)})' for p in self.patterns]}"
        )
        if not merge_mergable:
            return self.patterns

        new_groups = []
        current_mergable = None
        is_first = True
        for pg in self.patterns:
            if pg.pattern_name not in [OTHER, SLOW_STRETCH]:
                current_mergable = self._handle_non_mergable_group(new_groups, current_mergable, pg)
                is_first = True
            else:
                current_mergable, is_first = self._handle_mergable_group(
                    new_groups, current_mergable, pg, is_first
                )

        if current_mergable is not None and len(current_mergable.segments) > 0:
            new_groups.append(current_mergable)

        logger.debug(
            f"Merged patterns ({len(new_groups)}): {[f'{p.pattern_name} ({len(p.segments)})' for p in new_groups]}"
        )
        return new_groups

    def _handle_non_mergable_group(
        self, new_patterns_list, current_mergable: Optional[Pattern], pg
    ):
        """
        Handles non-OTHER groups while merging Patterns.
        """
        if current_mergable is not None:
            # If OTHER
            if current_mergable.pattern_name == OTHER:
                # Special OTHER case where if it doesn't end in an interval, then don't include the final segment as it is an overlap
                if not self.segment_is_interval(current_mergable.segments[-1]):
                    current_mergable.segments = current_mergable.segments[:-1]
                new_patterns_list.append(current_mergable)
            # If Slow stretch
            elif current_mergable.pattern_name == SLOW_STRETCH:
                new_patterns_list.append(current_mergable)
            else:
                raise ValueError(
                    f"Unsupported mergable pattern of: {current_mergable.pattern_name}"
                )
            current_mergable = None
        new_patterns_list.append(pg)
        return current_mergable

    def _get_empty_mergable_pattern(self, pattern: Pattern):
        if pattern.pattern_name == OTHER:
            return OtherPattern(OTHER, [])
        elif pattern.pattern_name == SLOW_STRETCH:
            return SlowStretchPattern(SLOW_STRETCH, [])
        else:
            raise ValueError(f"Unsupported mergable pattern of: {pattern.pattern_name}")

    def _handle_mergable_group(
        self, new_groups, current_mergable: Optional[Pattern], pattern: Pattern, is_first: bool
    ):
        """
        Handles OTHER groups while merging Patterns.
        """
        # Need to see whether the current mergable is same type

        if current_mergable is None:
            current_mergable = self._get_empty_mergable_pattern(pattern)

        # if DIFFERENT type, add the current mergable and is_first becomes True
        if current_mergable.pattern_name != pattern.pattern_name:
            # Race condition where Other is of length 1... we want to just ignore this and move on...
            if pattern.pattern_name == OTHER and len(pattern.segments) == 1:
                return current_mergable, is_first
            new_groups.append(current_mergable)
            is_first = True
            if pattern.pattern_name in [OTHER, SLOW_STRETCH]:
                current_mergable = self._get_empty_mergable_pattern(pattern)
            else:
                current_mergable = None
        if is_first:
            current_mergable = self._handle_first_mergable_group(current_mergable, pattern)
        else:
            current_mergable = self._handle_not_first_mergable_group(current_mergable, pattern)
        if current_mergable:
            is_first = False
        return current_mergable, is_first

    def _handle_first_mergable_group(self, current_mergable, pattern: Pattern):
        """
        Handles the first occurrence of a MERGABLE group while merging Patterns.
        """
        if (
            len(self.patterns) > 1
            and len(pattern.segments) == 1
            and self.segment_is_interval(pattern.segments[0])
        ):
            current_mergable = None
        else:
            current_mergable.segments += pattern.segments
        return current_mergable

    def _handle_not_first_mergable_group(self, current_mergable: Pattern, pattern: Pattern):
        """
        Handles subsequent occurrences of OTHER groups while merging Patterns.
        """

        # IF OTHER
        if current_mergable.pattern_name == OTHER:
            if len(pattern.segments) > 2:
                if self.segment_is_interval(pattern.segments[0]):
                    current_mergable.segments += pattern.segments[1:]
                else:
                    current_mergable.segments += pattern.segments[2:]
        # If SLOW STRETCH - add all but the first segments
        elif current_mergable.pattern_name == SLOW_STRETCH:
            current_mergable.segments += pattern.segments[1:]
        else:
            raise ValueError(f"Unsupported mergable pattern: {current_mergable.pattern_name}")
        return current_mergable

    def _handle_last_paterns(self, merge_mergable=True):
        # Do last check
        for last_check_pattern in self.groups:
            if last_check_pattern.is_appendable():
                last_pattern_copy = last_check_pattern.__class__(
                    last_check_pattern.pattern_name,
                    last_check_pattern.segments,
                    last_check_pattern.start_sample,
                    last_check_pattern.end_sample,
                )
                self.patterns.append(last_pattern_copy)
                return self._return_final_patterns(merge_mergable)
        if len(self.other_pattern.segments) > 0:
            # If there is a hanging SINGLE Interval at the end of the pattern, don't add it... unless it is the only one in the group list
            if len(self.patterns) == 0 or not (
                len(self.other_pattern.segments) == 1
                and self.segment_is_interval(self.other_pattern.segments[0])
            ):
                last_pattern_copy = OtherPattern(
                    OTHER,
                    self.other_pattern.segments,
                    self.other_pattern.start_sample,
                    self.other_pattern.end_sample,
                )
                self.patterns.append(last_pattern_copy)

    def _handle_appendable_group(
        self, group: Pattern, previous_segment: Segment, current_segment: Segment
    ):
        # Need to first check if OtherGroup has stragglers...
        if len(group.segments) < len(self.other_pattern.segments):
            # THERE ARE STRAGGLERS.
            other_group = OtherPattern(
                OTHER,
                self.other_pattern.segments[: -len(group.segments)],
            )
            self.patterns.append(other_group)

        group_copy = group.__class__(
            group.pattern_name,
            group.segments,
            group.start_sample,
            group.end_sample,
        )
        self.patterns.append(group_copy)
        # Reset all groups with current pattern.
        for group in self.groups:
            group.reset_group(previous_segment, current_segment)
        self.other_pattern.reset_group(previous_segment, current_segment)  # reset OtherGroup

    def _handle_each_group(self, previous_segment: Segment, current_segment: Segment):
        self.added = False  # has this pattern been added?
        self.reset = False  # have we done a reset?
        for group in self.groups:
            group: Pattern
            _added = group.check_segment(current_segment)
            if _added == True:
                self.added = True
            else:
                # Only set it to inactive if it's already begun adding stuff
                if len(group.segments) > 0:
                    group.is_active = False

                # Check if the group is appendable
                if group.is_appendable():
                    self.added = True
                    self._handle_appendable_group(
                        group=group,
                        previous_segment=previous_segment,
                        current_segment=current_segment,
                    )
                    self.reset = True
                    return  # STOP LOOKING !! WE FOUND SOMETHING

    def identify_patterns(
        self, segments_list: List[Segment], merge_mergable: bool = True
    ) -> List[Pattern]:
        """Identifies Patterns from a list of Segments.

        Args:
            segments_list (List[Segment]): The list of segments to identify Patterns from.
            merge_mergable (bool, optional): If True, merges mergable consecutive patterns together. Defaults to True.

        Returns:
            List[Pattern]: The list of identified Patterns.
        """
        for i in range(0, len(segments_list)):
            current_segment = segments_list[i]

            previous_segment: Optional[Segment] = (
                segments_list[i - 1] if len(segments_list) > 1 and i != 0 else None
            )

            self._handle_each_group(previous_segment, current_segment)
            if not self.reset:
                self.other_pattern.check_segment(current_segment)

            # We have gone through all the defined groups...
            if not self.added:
                # Append OtherGroup if no other groups were appendable
                if len(self.other_pattern.segments) > 0:
                    self.patterns.append(
                        OtherPattern(
                            OTHER,
                            self.other_pattern.segments,
                            self.other_pattern.start_sample,
                            self.other_pattern.end_sample,
                        )
                    )
                self.other_pattern.reset_group(
                    previous_segment, current_segment
                )  # reset OtherGroup
                # Reset all groups with current pattern.
                for group in self.groups:
                    group.reset_group(previous_segment, current_segment)

        self._handle_last_paterns(merge_mergable=merge_mergable)

        return self._return_final_patterns(merge_mergable)
