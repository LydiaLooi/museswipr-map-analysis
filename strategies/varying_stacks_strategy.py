from typing import Optional

from entities import Segment
from pattern_multipliers import varying_stacks_multiplier
from patterns.pattern import Pattern
from strategies.default_strategies import DefaultCalcVariationScore
from strategies.pattern_strategies import (
    CalcPatternLengthMultiplierStrategy,
    CalcPatternMultiplierStrategy,
    CalcVariationScoreStrategy,
    CheckSegmentStrategy,
    IsAppendableStrategy,
)


class VaryingStacksCheckSegment(CheckSegmentStrategy):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.pattern.is_active:
            return False

        if self.pattern.segment_is_interval(current_segment):
            at_start = self.pattern.add_interval_is_at_start(current_segment)
            if not at_start:
                return False
            return True

        # Check if current segment is straight up invalid
        if not self.pattern.is_n_stack(current_segment):
            return False

        # Current segment should be valid from here
        self.pattern.segments.append(current_segment)
        return True


class VaryingStacksIsAppendable(IsAppendableStrategy):
    def is_appendable(self) -> bool:
        if len(self.pattern.segments) >= 2:
            # Needs at least 2 n-stacks to be valid
            n_stack_count = 0
            for p in self.pattern.segments:
                if self.pattern.is_n_stack(p):
                    n_stack_count += 1
                if not self.pattern.is_n_stack(p) and not self.pattern.segment_is_interval(p):
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


class VaryingStacksCalcPatternMultiplier(CalcPatternMultiplierStrategy):
    def calc_pattern_multiplier(self) -> float:
        nps = self.pattern.segments[0].notes_per_second
        multiplier = varying_stacks_multiplier(nps)
        return multiplier
