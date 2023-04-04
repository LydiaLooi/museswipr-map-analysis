from typing import Optional

from entities import Segment
from patterns.pattern import Pattern

from pattern_multipliers import varying_stacks_multiplier
from strategies.default_strategies import DefaultCalcVariationScore

class VaryingStacksCheckSegment(Pattern):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.is_active:
            return False

        if self.segment_is_interval(current_segment):
            at_start = self.add_interval_is_at_start(current_segment)
            if not at_start:
                return False
            return True
        
        # Check if current segment is straight up invalid
        if not self.is_n_stack(current_segment):
            return False

        # Current segment should be valid from here
        self.segments.append(current_segment)
        return True
    
class VaryingStacksIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        if len(self.segments) >= 2:
            # Needs at least 2 n-stacks to be valid
            n_stack_count = 0
            for p in self.segments:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and not self.segment_is_interval(p):
                    raise ValueError(f"Varying Stack has a: {p.segment_name}!!")   
            if n_stack_count >= 2:
                return True
        return False
    

class VaryingStacksCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self, pls_print=False) -> float:
        variation_score = super().calc_variation_score(pls_print)

        # Make a minor change to the return value
        modified_variation_score = max(1, variation_score)

        return modified_variation_score

class VaryingStacksCalcPatternMultiplier(Pattern):
    def calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second
        multiplier = varying_stacks_multiplier(nps)
        return multiplier