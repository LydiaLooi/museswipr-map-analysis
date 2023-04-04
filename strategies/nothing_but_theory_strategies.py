import math
from typing import Optional

from constants import SWITCH, ZIG_ZAG
from entities import Segment
from pattern_multipliers import nothing_but_theory_multiplier
from patterns.pattern import Pattern


class NothingButTheoryCheckSegment(Pattern):
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
        if not self.is_n_stack(current_segment) and current_segment.segment_name != ZIG_ZAG:
            return False
        
        if current_segment.segment_name == ZIG_ZAG and len(current_segment.notes) not in  [4, 6]:
            return False


        if previous_segment:
            # If the previous segment is an interval, then we can add it.
            if self.segment_is_interval(previous_segment):
                self.segments.append(current_segment)
                return True
            
            if previous_segment.segment_name == ZIG_ZAG and not self.is_n_stack(current_segment):
                return False
            
            if self.is_n_stack(previous_segment) and current_segment.segment_name != ZIG_ZAG:
                return False

            if abs(current_segment.time_difference - previous_segment.time_difference) > self.tolerance:
                return False

            if not self.interval_between_segments_is_tolerable(previous_segment, current_segment):
                return False
            
        # Current segment should be valid from here
        self.segments.append(current_segment)

        return True
    
class NothingButTheoryIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        if len(self.segments) >= 3:
            # Sanity check that everything in it is only N-stacks or ZIG ZAGS
            n_stack_count = 0
            for seg in self.segments:
                if self.is_n_stack(seg):
                    n_stack_count += 1
                if not self.is_n_stack(seg) and seg.segment_name != ZIG_ZAG and not self.segment_is_interval(seg):
                    raise ValueError(f"Nothing but theory has a: {seg.segment_name}!!")   
            if n_stack_count >= 2:
                return True
        return False
    
class NothingButTheoryCalcVariationScore(Pattern):
    def calc_variation_score(self, pls_print=False) -> float:
        # TODO: Make the calculation method into several helper methods.
        if pls_print:
            print("Note: Nothing but theory overrode _calc_variation_score")
        temp_lst = [f"{s.segment_name} {len(s.notes)}" for s in self.segments] # Zig Zags of different note lengths are considered different
        interval_list = []
        lst = []

        segment_counts = self._get_segment_type_counts([s.segment_name for s in self.segments])

        # Check for intervals:
        for i, name in enumerate(temp_lst):
            if name in self.intervals:
                if i == 0 or i == len(temp_lst) - 1: # If it's the firs
                    interval_list.append(self.intervals[name] * self.end_extra_debuff)
                    # Don't add it to the list to check
                else:
                    interval_list.append(self.intervals[name])
                    lst.append("Interval") # Rename all Intervals to the same name
            else:
                lst.append(name)

        if pls_print:
            print(f"Checking entropy of: {lst}")
        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]
        entropy = -sum(p * math.log2(p) for p in freq)

        if len(interval_list) != 0:
            # average interval debuffs and multiply that by the entropy
            average_debuff = sum(interval_list)/len(interval_list)
            entropy *= average_debuff
            if pls_print:
                print(f">>> Debuffing (due to Intervals) by {average_debuff} <<<")

        entropy = self._calc_switch_debuff(segment_counts, entropy)

        return max(1, entropy)

class NothingButTheoryCalcPatternMultiplier(Pattern):
    def calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second

        multiplier = nothing_but_theory_multiplier(nps)
        return multiplier