from typing import Optional

from entities import Segment
from patterns.pattern import Pattern
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategy import PatternStrategy


class OtherCheckSegment(PatternStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.pattern.segments.append(current_segment)
        return True
    

class OtherIsAppendable(PatternStrategy):
    def is_appendable(self) -> bool:
        return True
    
class OtherCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self, pls_print=False) -> float:
        return super().calc_variation_score(pls_print)

class OtherCalcPatternMultiplier(PatternStrategy):
    # TODO: Complete
    def calc_pattern_multiplier(self) -> float:
        for segment in self.pattern.segments:
            pass
        
        return 1
