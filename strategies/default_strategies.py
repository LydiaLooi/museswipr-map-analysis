import math
from typing import Optional

from constants import SWITCH
from patterns.pattern import Pattern
from entities import Segment


class DefaultCalcVariationScore(Pattern):
    def calc_variation_score(self, pls_print=False) -> float:
        """Calculates the variation score of the Pattern based on the segments within.

        The entropy score measures the amount of uncertainty or randomness in the distribution 
        of values in the list. It takes into account the relative frequencies of 
        the different values, and it increases as the distribution becomes more 
        even or diverse. A list with low entropy has a dominant or repetitive value, 
        while a list with high entropy has no dominant value and the values are more 
        evenly distributed.

        Returns:
            entropy: The calculated amount of uncertainty or randomness in the segments
        """

        # Thanks to ChatGPT for writing this for me
        temp_lst = [s.segment_name for s in self.segments]
        switch_count = 0
        interval_list = []
        segment_names = []

        pattern_counts = self._get_segment_type_counts(temp_lst)


        # Check for intervals:
        for i, name in enumerate(temp_lst):
            if name == SWITCH:
                switch_count += 1
            if name in self.intervals:
                if i == 0 or i == len(temp_lst) - 1: # If it's the firs
                    interval_list.append(self.intervals[name] * self.end_extra_debuff)
                    # Don't add it to the list to check
                else:
                    interval_list.append(self.intervals[name])
                    segment_names.append("Interval") # Rename all Intervals to the same name
            else:
                segment_names.append(name)

        if pls_print:
            print(f"Checking entropy of: {segment_names}")
        n = len(segment_names)
        unique_vals = set(segment_names)
        freq = [segment_names.count(x) / n for x in unique_vals]
        entropy = -sum(p * math.log2(p) for p in freq)

        if len(interval_list) != 0:
            # average interval debuffs and multiply that by the entropy
            average_debuff = sum(interval_list)/len(interval_list)
            entropy *= average_debuff
            if pls_print:
                print(f">>> Debuffing (due to Intervals) by {average_debuff} <<<")

        entropy = self._calc_switch_debuff(pattern_counts, entropy)

        if entropy == 0: # Temp?
            return 1

        return entropy
    
class DefaultCalcPatternMultiplier(Pattern):
    def _calc_pattern_multiplier(self) -> float:
        """Calculates the PatternGroup's multiplier based on notes per secondo
        This method should be overridded to be PatternGroup specific.
        Default returns 1.

        Returns:
            float: The multiplier
        """
        return 1
    
class DefaultCalcPatternLengthMultiplier(Pattern):
    def _calc_pattern_length_multiplier(self) -> float:
        return 1
    
class DefaultCheckSegment(Pattern):
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        raise NotImplementedError("You should use an actual strategy!")
    
class DefaultIsAppendable(Pattern):
    def is_appendable(self) -> bool:
        raise NotImplementedError("You should use an actual strategy!")
