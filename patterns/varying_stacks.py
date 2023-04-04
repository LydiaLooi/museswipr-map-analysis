from patterns.pattern import Pattern
from strategies.varying_stacks_strategy import (
    VaryingStacksCheckSegment,
    VaryingStacksIsAppendable,
    VaryingStacksCalcVariationScore,
    VaryingStacksCalcPatternMultiplier
)

class VaryingStacksPattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern_weighting = 0.8
        self.variation_weighting = 0.2

        self.set_check_segment_strategy(VaryingStacksCheckSegment(self))
        self.set_is_appendable_strategy(VaryingStacksIsAppendable(self))
        self.set_calc_variation_score_strategy(VaryingStacksCalcVariationScore(self))
        self.set_calc_pattern_multiplier_strategy(VaryingStacksCalcPatternMultiplier(self))