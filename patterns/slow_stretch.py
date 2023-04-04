from patterns.pattern import Pattern
from strategies.slow_stretch_strategies import (
    SlowStretchCheckSegment,
    SlowStretchIsAppendable,
    SlowStretchCalcVariation,
    SlowStretchPatternMultiplier
)

class SlowStretchPattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(SlowStretchCheckSegment(*args, **kwargs))
        self.set_is_appendable_strategy(SlowStretchIsAppendable(*args, **kwargs))
        self.set_calc_variation_score_strategy(SlowStretchCalcVariation(*args, **kwargs))
        self.set_calc_pattern_multiplier_strategy(SlowStretchPatternMultiplier(*args, **kwargs))