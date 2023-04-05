from config.config import get_config
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategies import (
    CalcPatternLengthMultiplierStrategy,
    CalcPatternMultiplierStrategy,
    CalcVariationScoreStrategy,
    CheckSegmentStrategy,
    IsAppendableStrategy,
)

conf = get_config()
from typing import Optional

import config.logging_config as logging_config
from musemapalyzr.constants import (
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
from musemapalyzr.pattern_multipliers import (
    four_stack_multiplier,
    stream_multiplier,
    three_stack_multiplier,
    two_stack_multiplier,
    zig_zag_multiplier,
)
from musemapalyzr.utils import weighted_average_of_values

logger = logging_config.logger


class OtherCheckSegment(CheckSegmentStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.pattern.segments.append(current_segment)
        return True


class OtherIsAppendable(IsAppendableStrategy):
    def is_appendable(self) -> bool:
        return True


class OtherCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self) -> float:
        return super().calc_variation_score()


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
                multipliers.append(conf["other_switch_multiplier"])

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
                multipliers.append(conf["other_short_int_multiplier"])
            elif segment.segment_name == MED_INTERVAL:
                multipliers.append(conf["other_med_int_multiplier"])
            elif segment.segment_name == LONG_INTERVAL:
                multipliers.append(conf["other_long_int_multiplier"])
            else:
                logger.warning(f"WARNING: Did not recognise pattern: {segment.segment_name}")
                multipliers.append(1)
        logger.debug(f"Other Pattern Multipliers: {multipliers}")
        weighted_average = weighted_average_of_values(multipliers)

        return weighted_average
