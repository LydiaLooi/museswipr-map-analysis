from typing import Optional

from constants import SWITCH
from entities import Segment
from pattern_multipliers import even_circle_multiplier
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategies import (CalcPatternLengthMultiplierStrategy,
                                           CalcPatternMultiplierStrategy,
                                           CalcVariationScoreStrategy,
                                           CheckSegmentStrategy,
                                           IsAppendableStrategy)


class EvenCirclesCheckSegment(CheckSegmentStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.pattern.is_active:
            return False

        previous_segment: Optional[Segment] = self.pattern.segments[-1] if len(self.pattern.segments) > 0 else None

        if self.pattern.segment_is_interval(current_segment):
            at_start = self.pattern.add_interval_is_at_start(current_segment)
            if not at_start:
                return False
            return True

        # Check for invalid combinations of previous segment and current segment
        if not self.pattern.is_n_stack(current_segment) and current_segment.segment_name != SWITCH:
            return False

        if previous_segment:
            # If the previous segment is an interval, then we can add it.
            if self.pattern.segment_is_interval(previous_segment):
                self.pattern.segments.append(current_segment)
                return True
            
            if previous_segment.segment_name == SWITCH and not self.pattern.is_n_stack(current_segment):
                return False
            
            if self.pattern.is_n_stack(previous_segment) and current_segment.segment_name != SWITCH:
                return False

            if not self.pattern.time_difference_is_tolerable(previous_segment, current_segment):
                return False

            if not self.pattern.interval_between_segments_is_tolerable(previous_segment, current_segment):
                return False
        # Current segment should be valid from here
        self.pattern.segments.append(current_segment)
        return True
    
class EvenCirclesIsAppendable(IsAppendableStrategy):
    def is_appendable(self) -> bool:
        if len(self.pattern.segments) >= 3:
            # Sanity check that everything in it is only N-stacks or Switches
            n_stack_count = 0
            for p in self.pattern.segments:
                if self.pattern.is_n_stack(p):
                    n_stack_count += 1
                if not self.pattern.is_n_stack(p) and p.segment_name != SWITCH and not self.pattern.segment_is_interval(p):
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
    
class EvenCirclesCalcPatternMultiplier(CalcPatternMultiplierStrategy):
    def calc_pattern_multiplier(self) -> float:
        nps = self.pattern.segments[0].notes_per_second # Even Circle should have consistent NPS
        multiplier = even_circle_multiplier(nps)
        return multiplier