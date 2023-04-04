from patterns.pattern import Pattern
from strategies.skewed_circles_strategies import (
    SkewedCirclesCheckSegment,
    SkewedCirclesIsAppendable,
    SkewedCirclesCalcVariationScore,
    SkewedCirclesCalcPatternMultiplier
)

class SkewedCirclesGroup(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(SkewedCirclesCheckSegment(self))
        self.set_is_appendable_strategy(SkewedCirclesIsAppendable(self))
        self.set_calc_variation_score_strategy(SkewedCirclesCalcVariationScore(self))
        self.set_calc_pattern_multiplier_strategy(SkewedCirclesCalcPatternMultiplier(self))