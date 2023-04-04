from typing import List

from constants import DEFAULT_SAMPLE_RATE
from entities import Segment
from patterns.pattern import Pattern
from strategies.nothing_but_theory_strategies import (
    NothingButTheoryCalcPatternMultiplier, NothingButTheoryCalcVariationScore,
    NothingButTheoryCheckSegment, NothingButTheoryIsAppendable)


class NothingButTheoryGroup(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(NothingButTheoryCheckSegment(*args, **kwargs))
        self.set_is_appendable_strategy(NothingButTheoryIsAppendable(*args, **kwargs))
        self.set_calc_variation_score_strategy(NothingButTheoryCalcVariationScore(*args, **kwargs))
        self.set_calc_pattern_multiplier_strategy(NothingButTheoryCalcPatternMultiplier(*args, **kwargs))