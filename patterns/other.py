from patterns.pattern import Pattern
from strategies.other_strategies import (OtherCalcPatternMultiplier,
                                         OtherCalcVariationScore,
                                         OtherCheckSegment, OtherIsAppendable)


class OtherPattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_check_segment_strategy(OtherCheckSegment(*args, **kwargs))
        self.set_is_appendable_strategy(OtherIsAppendable(*args, **kwargs))
        self.set_calc_variation_score_strategy(OtherCalcVariationScore(*args, **kwargs))
        self.set_calc_pattern_multiplier_strategy(OtherCalcPatternMultiplier(*args, **kwargs))