import math
from typing import Optional

from entities import Segment
from patterns.pattern import Pattern

from strategies.default_strategies import DefaultCalcPatternMultiplier

class SlowStretchCheckSegment(Pattern):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.is_active:
            return False
        previous_segment: Optional[Segment] = self.segments[-1] if len(self.segments) > 0 else None

        if "Interval" in current_segment.segment_name and (previous_segment is None or "Interval" in previous_segment.segment_name):
            self.segments.append(current_segment)
            return True
        return False
    

class SlowStretchIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        if len(self.segments) >= 2:
            for p in self.segments:
                if "Interval" not in p.segment_name:
                    raise ValueError(f"Slow Stretch has a: {p.segment_name}!!")
            return True
        return False
    
class SlowStretchCalcVariation(Pattern):
    def calc_variation_score(self, pls_print=False) -> float:
        # Variation score for Slow Stretches is based on column variation rather than segment variation

        lst = []
        unique_sample_times = set()
        for p in self.segments:
            for n in p.notes:
                if n.sample_time not in unique_sample_times:
                    lst.append(n.lane)
                    unique_sample_times.add(n.sample_time)
        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]

        entropy = -sum(p * math.log2(p) for p in freq)
        if int(entropy) == 0 :
            return 1
        return entropy
    
class SlowStretchPatternMultiplier(DefaultCalcPatternMultiplier):
    def calc_pattern_multiplier(self) -> float:
        return super().calc_pattern_multiplier()