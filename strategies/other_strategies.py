from patterns.pattern import Pattern
from entities import Segment
from typing import Optional

from strategies.default_strategies import DefaultCalcVariationScore

class OtherCheckSegment(Pattern):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.segments.append(current_segment)
        return True
    

class OtherIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        return True
    
class OtherCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self, pls_print=False) -> float:
        return super().calc_variation_score(pls_print)

class OtherCalcPatternMultiplier(Pattern):
    # TODO: Complete
    def calc_pattern_multiplier(self) -> float:
        for segment in self.segments:
            pass
        
        return 1
