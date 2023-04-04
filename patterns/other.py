from patterns.pattern import Pattern
from strategies.other_strategies import (OtherCalcPatternMultiplier,
                                         OtherCalcVariationScore,
                                         OtherCheckSegment, OtherIsAppendable)


class OtherPattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(OtherCheckSegment(self))
        self.set_is_appendable_strategy(OtherIsAppendable(self))
        self.set_calc_variation_score_strategy(OtherCalcVariationScore(self))
        self.set_calc_pattern_multiplier_strategy(OtherCalcPatternMultiplier(self))