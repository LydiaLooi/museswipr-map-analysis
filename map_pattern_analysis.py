from typing import List, Optional

from constants import (
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
from entities import Segment
from patterns.even_circles import EvenCirclesGroup
from patterns.nothing_but_theory import NothingButTheoryGroup
from patterns.other import OtherPattern
from patterns.pattern import Pattern
from patterns.skewed_circles import SkewedCirclesGroup
from patterns.slow_stretch import SlowStretchPattern
from patterns.varying_stacks import VaryingStacksPattern


class MapPatterns:
    def __init__(self):
        # **THE** list of Patterns
        self.patterns: List[Pattern] = []

        # Keeps track during analysis of whether a pattern has been appended
        self.pattern_appended: bool = False
        self.pattern_appended_name: str = ""

        self.groups = []

        self.other_pattern: OtherPattern = OtherPattern(OTHER, [])
        self.reset_groups()

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

    def _return_final_patterns(self, merge_other=True) -> List[Pattern]:
        """
        Returns the final list of Patterns after merging, if merge_other is True.
        """
        if not merge_other:
            return self.patterns

        new_groups = []
        current_other = None
        is_first = True
        for pg in self.patterns:
            if pg.pattern_name != OTHER:
                current_other = self._handle_non_other_group(new_groups, current_other, pg)
                is_first = True
            else:
                current_other, is_first = self._handle_other_group(current_other, pg, is_first)

        if current_other is not None and len(current_other.segments) > 0:
            new_groups.append(current_other)
        return new_groups

    def _handle_non_other_group(self, new_patterns_list, current_other: Optional[Pattern], pg):
        """
        Handles non-OTHER groups while merging Patterns.
        """
        if current_other is not None:
            if not self.segment_is_interval(current_other.segments[-1]):
                current_other.segments = current_other.segments[:-1]
            new_patterns_list.append(current_other)
            current_other = None
        new_patterns_list.append(pg)
        return current_other

    def _handle_other_group(self, current_other: Optional[Pattern], pattern, is_first):
        """
        Handles OTHER groups while merging Patterns.
        """
        if current_other is None:
            current_other = OtherPattern(OTHER, [])
        if is_first:
            current_other = self._handle_first_other_group(current_other, pattern)
        else:
            current_other = self._handle_not_first_other_group(current_other, pattern)
        if current_other:
            is_first = False
        return current_other, is_first

    def _handle_first_other_group(self, current_other, pattern: Pattern):
        """
        Handles the first occurrence of an OTHER group while merging Patterns.
        """
        if (
            len(self.patterns) > 1
            and len(pattern.segments) == 1
            and self.segment_is_interval(pattern.segments[0])
        ):
            current_other = None
        else:
            current_other.segments += pattern.segments
        return current_other

    def _handle_not_first_other_group(self, current_other, pattern: Pattern):
        """
        Handles subsequent occurrences of OTHER groups while merging Patterns.
        """
        if len(pattern.segments) > 2:
            if self.segment_is_interval(pattern.segments[0]):
                current_other.segments += pattern.segments[1:]
            else:
                current_other.segments += pattern.segments[2:]
        return current_other

    def identify_patterns(
        self, segments_list: List[Segment], merge_other: bool = True
    ) -> List[Pattern]:
        for i in range(0, len(segments_list)):
            current_segment = segments_list[i]

            if len(segments_list) > 1 and i != 0:
                previous_segment: Optional[Segment] = segments_list[i - 1]
            else:
                previous_segment: Optional[Segment] = None

            added = False  # has this pattern been added?
            reset = False  # have we done a reset?
            for group in self.groups:
                group: Pattern
                _added = group.check_segment(current_segment)
                if _added == True:
                    added = True
                else:
                    if len(group.segments) > 0:
                        group.is_active = (
                            False  # Only set it to inactive if it's already begun adding stuff
                        )

                    # Check if the group is appendable
                    if group.is_appendable():
                        # Need to first check if OtherGroup has stragglers...
                        if len(group.segments) < len(self.other_pattern.segments):
                            # THERE ARE STRAGGLERS.
                            other_group = OtherPattern(
                                OTHER,
                                self.other_pattern.segments[: -len(group.segments)],
                            )
                            self.patterns.append(other_group)

                        added = True
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
                        self.other_pattern.reset_group(
                            previous_segment, current_segment
                        )  # reset OtherGroup
                        reset = True
                        break  # STOP LOOKING !! WE FOUND SOMETHING
            if not reset:
                self.other_pattern.check_segment(current_segment)

            # We have gone through all the defined groups...
            if not added:
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
                return self._return_final_patterns(merge_other)
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

        return self._return_final_patterns(merge_other)
