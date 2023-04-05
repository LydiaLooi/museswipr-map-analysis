import math
from typing import Optional

from musemapalyzr.entities import Segment
from patterns.pattern import Pattern
from strategies.default_strategies import DefaultCalcPatternMultiplier
from strategies.pattern_strategies import (
    CalcPatternLengthMultiplierStrategy,
    CalcPatternMultiplierStrategy,
    CalcVariationScoreStrategy,
    CheckSegmentStrategy,
    IsAppendableStrategy,
)


class SlowStretchCheckSegment(CheckSegmentStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.pattern.is_active:
            return False
        previous_segment: Optional[Segment] = (
            self.pattern.segments[-1] if len(self.pattern.segments) > 0 else None
        )

        if "Interval" in current_segment.segment_name and (
            previous_segment is None or "Interval" in previous_segment.segment_name
        ):
            self.pattern.segments.append(current_segment)
            return True
        return False


class SlowStretchIsAppendable(IsAppendableStrategy):
    def is_appendable(self) -> bool:
        if len(self.pattern.segments) >= 2:
            for p in self.pattern.segments:
                if "Interval" not in p.segment_name:
                    raise ValueError(f"Slow Stretch has a: {p.segment_name}!!")
            return True
        return False


class SlowStretchCalcVariation(CalcVariationScoreStrategy):
    def calc_variation_score(self) -> float:
        # Variation score for Slow Stretches is based on column variation rather than segment variation

        lst = []
        unique_sample_times = set()
        for p in self.pattern.segments:
            for n in p.notes:
                if n.sample_time not in unique_sample_times:
                    lst.append(n.lane)
                    unique_sample_times.add(n.sample_time)
        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]

        entropy = -sum(p * math.log2(p) for p in freq)
        if int(entropy) == 0:
            return 1
        return entropy


class SlowStretchPatternMultiplier(DefaultCalcPatternMultiplier):
    def calc_pattern_multiplier(self) -> float:
        return super().calc_pattern_multiplier()
