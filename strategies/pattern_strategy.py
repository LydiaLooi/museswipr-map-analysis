
from typing import Optional
from entities import Segment
from patterns.pattern import Pattern

ERROR_MSG = "You should replace this with a concrete strategy"

class PatternStrategy(Pattern):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        raise NotImplementedError(ERROR_MSG)
    
    def is_appendable(self) -> bool:
        raise NotImplementedError(ERROR_MSG)
    
    def calc_variation_score(self, pls_print=False) -> float:
        raise NotImplementedError(ERROR_MSG)
    
    def calc_pattern_multiplier(self) -> float:
        raise NotImplementedError(ERROR_MSG)