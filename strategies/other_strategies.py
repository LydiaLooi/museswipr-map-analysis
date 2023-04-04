from typing import Optional

from entities import Segment
from pattern_multipliers import (
    four_stack_multiplier,
    stream_multiplier,
    three_stack_multiplier,
    two_stack_multiplier,
    zig_zag_multiplier,
)
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategies import (
    CalcPatternLengthMultiplierStrategy,
    CalcPatternMultiplierStrategy,
    CalcVariationScoreStrategy,
    CheckSegmentStrategy,
    IsAppendableStrategy,
)

from constants import (
    ZIG_ZAG,
    TWO_STACK,
    THREE_STACK,
    FOUR_STACK,
    SWITCH,
    SINGLE_STREAMS,
    SHORT_INTERVAL,
    MED_INTERVAL,
    LONG_INTERVAL,
)

from utils import weighted_average_of_values


class OtherCheckSegment(CheckSegmentStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.pattern.segments.append(current_segment)
        return True


class OtherIsAppendable(IsAppendableStrategy):
    def is_appendable(self) -> bool:
        return True


class OtherCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self, pls_print=False) -> float:
        return super().calc_variation_score(pls_print)


class OtherCalcPatternMultiplier(CalcPatternMultiplierStrategy):
    def calc_pattern_multiplier(self) -> float:
        """Other Patterns are calculated based on the weighted average
        of the segment difficulties within the Other pattern.

            Returns:
                float: The multiplier of the pattern.
        """

        multipliers = []

        for segment in self.pattern.segments:
            if segment.segment_name == SWITCH:
                multipliers.append(1)

            elif segment.segment_name == ZIG_ZAG:
                multipliers.append(zig_zag_multiplier(segment.notes_per_second))
            elif segment.segment_name == TWO_STACK:
                multipliers.append(two_stack_multiplier(segment.notes_per_second))
            elif segment.segment_name == THREE_STACK:
                multipliers.append(three_stack_multiplier(segment.notes_per_second))
            elif segment.segment_name == FOUR_STACK:
                multipliers.append(four_stack_multiplier(segment.notes_per_second))
            elif segment.segment_name == SINGLE_STREAMS:
                multipliers.append(stream_multiplier(segment.notes_per_second))
            elif segment.segment_name == SHORT_INTERVAL:
                multipliers.append(0.8)
            elif segment.segment_name == MED_INTERVAL:
                multipliers.append(0.7)
            elif segment.segment_name == LONG_INTERVAL:
                multipliers.append(0.5)
            else:
                print(f"WARNING: Did not recognise pattern: {segment.segment_name}")
                multipliers.append(1)
        # print(f"Other Pattern Multipliers: {multipliers}")
        weighted_average = weighted_average_of_values(multipliers)

        return weighted_average
