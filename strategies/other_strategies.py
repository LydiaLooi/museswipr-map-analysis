from typing import Optional

from entities import Segment
from patterns.pattern import Pattern
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategies import (CalcPatternLengthMultiplierStrategy,
                                           CalcPatternMultiplierStrategy,
                                           CalcVariationScoreStrategy,
                                           CheckSegmentStrategy,
                                           IsAppendableStrategy)


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
    # TODO: Complete
    def calc_pattern_multiplier(self) -> float:
        for segment in self.pattern.segments:
            pass
        
        return 1
