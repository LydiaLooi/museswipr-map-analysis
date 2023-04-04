from typing import Optional

from entities import Segment
from patterns.pattern import Pattern

from pattern_multipliers import even_circle_multiplier
from strategies.default_strategies import DefaultCalcVariationScore

from constants import SWITCH

class EvenCirclesCheckSegment(Pattern):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_segment: Optional[Segment] = self.segments[-1] if len(self.segments) > 0 else None

        if self.segment_is_interval(current_segment):
            at_start = self.add_interval_is_at_start(current_segment)
            if not at_start:
                return False
            return True

        # Check for invalid combinations of previous segment and current segment
        if not self.is_n_stack(current_segment) and current_segment.segment_name != SWITCH:
            return False

        if previous_segment:
            # If the previous segment is an interval, then we can add it.
            if self.segment_is_interval(previous_segment):
                self.segments.append(current_segment)
                return True
            
            if previous_segment.segment_name == SWITCH and not self.is_n_stack(current_segment):
                return False
            
            if self.is_n_stack(previous_segment) and current_segment.segment_name != SWITCH:
                return False

            if not self.time_difference_is_tolerable(previous_segment, current_segment):
                return False

            if not self.interval_between_segments_is_tolerable(previous_segment, current_segment):
                return False
        # Current segment should be valid from here
        self.segments.append(current_segment)
        return True
    
class EvenCirclesIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        if len(self.segments) >= 3:
            # Sanity check that everything in it is only N-stacks or Switches
            n_stack_count = 0
            for p in self.segments:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.segment_name != SWITCH and not self.segment_is_interval(p):
                    raise ValueError(f"Even Circle has a: {p.segment_name}!!")   
            if n_stack_count >= 2: # There must be at least 2 n_stacks to be valid
                return True
        return False
    

class EvenCirclesCalcVariationScore(DefaultCalcVariationScore):
    def calc_variation_score(self, pls_print=False) -> float:
        variation_score = super().calc_variation_score(pls_print)

        # Make a minor change to the return value
        modified_variation_score = max(1, variation_score)

        return modified_variation_score
    
class EvenCirclesCalcPatternMultiplier(Pattern):
    def calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second # Even Circle should have consistent NPS
        multiplier = even_circle_multiplier(nps)
        return multiplier