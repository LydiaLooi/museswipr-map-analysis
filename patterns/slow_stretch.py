from patterns.pattern import Pattern
from strategies.slow_stretch_strategies import (
    SlowStretchCheckSegment,
    SlowStretchIsAppendable,
    SlowStretchCalcVariation,
    SlowStretchPatternMultiplier
)
from strategies.default_strategies import DefaultCalcPatternLengthMultiplier
class SlowStretchPattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(SlowStretchCheckSegment(self))
        self.set_is_appendable_strategy(SlowStretchIsAppendable(self))
        self.set_calc_variation_score_strategy(SlowStretchCalcVariation(self))
        self.set_calc_pattern_multiplier_strategy(SlowStretchPatternMultiplier(self))
        self.set_calc_pattern_length_multiplier_strategy(DefaultCalcPatternLengthMultiplier(self))