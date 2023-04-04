from patterns.pattern import Pattern
from strategies.default_strategies import DefaultCalcPatternLengthMultiplier
from strategies.even_circles_strategies import (
    EvenCirclesCalcPatternMultiplier, EvenCirclesCalcVariationScore,
    EvenCirclesCheckSegment, EvenCirclesIsAppendable)


class EvenCirclesGroup(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(EvenCirclesCheckSegment(self))
        self.set_is_appendable_strategy(EvenCirclesIsAppendable(self))
        self.set_calc_variation_score_strategy(EvenCirclesCalcVariationScore(self))
        self.set_calc_pattern_multiplier_strategy(EvenCirclesCalcPatternMultiplier(self))
        self.set_calc_pattern_length_multiplier_strategy(DefaultCalcPatternLengthMultiplier(self))
