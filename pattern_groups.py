import math
from abc import ABC, abstractmethod
from typing import List, Optional

from constants import *
from entities import Note, Pattern


class PatternGroup(ABC):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int=None, end_sample: int=None):
        self.group_name = group_name
        self.patterns = patterns
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.is_active = True
        self.weighting = 1

        self.entropy_weighting = 0.5
        self.distance_weighting = 0.5

    @property
    def approx_total_notes(self): # because i cbf make it accurate ((:
        note_count = 0
        for p in self.patterns:
            note_count += len(p.notes)
            if len(p.notes) >= 3:
                note_count -= 2 # -2 for the overlap of patterns approx
        return note_count

    def __repr__(self) -> str:
        if len(self.patterns) >= 5:
            p = self.patterns[:5]
            extra = f" | Last Five: {self.patterns[-5:]}... ({len(self.patterns)} total)"
        else:
            p = self.patterns
            extra = ""
        if len(self.patterns) > 0:
            return f"{self.patterns[0].notes[0].sample_time/TIME_CONVERSION:.2f} | {self.group_name}, {p}{extra}"
        else:
            return f"{self.group_name}, {p}"

    @abstractmethod
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        pass


    @abstractmethod
    def is_appendable(self) -> bool:
        pass

    @staticmethod
    def is_n_stack(pattern: Pattern):
        return pattern.pattern_name in ("2-Stack", "3-Stack", "4-Stack")

    def pattern_is_interval(self, pattern: Pattern):
        if pattern:
            return "Interval" in pattern.pattern_name
        return False
    
    def time_difference_is_tolerable(self, previous_pattern: Pattern, current_pattern: Pattern):
        assert previous_pattern.time_difference is not None
        assert current_pattern.time_difference is not None

        # If the previous or current pattern is an Interval, return True
        if self.pattern_is_interval(previous_pattern) or self.pattern_is_interval(current_pattern):
            return True
        
        result = abs(current_pattern.time_difference - previous_pattern.time_difference) <= TOLERANCE

        return result

    def interval_between_patterns_is_tolerable(self, previous_pattern: Pattern, current_pattern: Pattern) -> bool:
        assert len(previous_pattern.notes) > 1
        assert len(current_pattern.notes) > 1
        # If the previous or current pattern is an Interval, return True
        if self.pattern_is_interval(previous_pattern) or self.pattern_is_interval(current_pattern):
            return True
        end_of_first = previous_pattern.notes[-1].sample_time
        start_of_second = current_pattern.notes[0].sample_time
        time_difference = abs(end_of_first - start_of_second)
        if time_difference <= TOLERANCE:
            # The patterns pretty much have the same note
            return True
        return False
    
    def reset_group(self, previous_pattern: Pattern, current_pattern: Pattern):
        self.is_active = True
        self.patterns = []

        # If previous or current_pattern is an Interval, then only add that one (prioritise the latest one).
        if self.pattern_is_interval(current_pattern):
            self.check_pattern(current_pattern)

        elif self.pattern_is_interval(previous_pattern):
            self.check_pattern(previous_pattern)
            self.check_pattern(current_pattern)
            
        # If not, then attempt to add the previous one first, then the current one too
        # If it fails at any point, set the group to inactive
        else:
            if previous_pattern:
                added = self.check_pattern(previous_pattern)
                if added:
                    added = self.check_pattern(current_pattern)
                
                if added is False:
                    self.is_active = False

    def add_interval_is_at_start(self, interval_pattern: Pattern) -> bool:
        """
        Adds the interval pattern to the patterns list
        Returns True if it is the first element
        Returns False if is not 
        """
        if len(self.patterns) == 0:
            self.patterns.append(interval_pattern)
            return True
        else:
            self.patterns.append(interval_pattern)
            return False
        
    def _calc_variation_score(self) -> float:
        """Calculates the variation score of the pattern group based on the patterns within.

        The entropy score measures the amount of uncertainty or randomness in the distribution 
        of values in the list. It takes into account the relative frequencies of 
        the different values, and it increases as the distribution becomes more 
        even or diverse. A list with low entropy has a dominant or repetitive value, 
        while a list with high entropy has no dominant value and the values are more 
        evenly distributed.

        Returns:
            entropy: The calculated amount of uncertainty or randomness in the patterns
        """
        intervals = {
            SHORT_INTERVAL: 0.7,
            MED_INTERVAL: 0.6,
            LONG_INTERVAL: 0.4
        }
        # Thanks to ChatGPT for writing this for me
        lst = [p.pattern_name for p in self.patterns]

        interval_list = []

        # Check for intervals:
        for name in lst:
            if name in intervals:
                interval_list.append(intervals[name])

        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]
        entropy = -sum(p * math.log2(p) for p in freq)

        if len(interval_list) != 0:
            # average interval debuffs and multiply that by the entropy
            average_debuff = sum(interval_list)/len(interval_list)
            entropy *= average_debuff

        return entropy
    
    
    def _calc_pattern_group_multiplier(self) -> float:
        """Calculates the PatternGroup's multiplier based on notes per secondo
        This method should be overridded to be PatternGroup specific.
        Default returns 1.

        Returns:
            float: The multiplier
        """
        return 1
    
    def _calc_pattern_length_multiplier(self) -> float:
        return 1

    def calc_pattern_group_difficulty(self) -> float:

        print(f"{self.group_name:.>25} {'Difficulty':.<25}")
        variation_multiplier = self._calc_variation_score()
        group_multiplier = self._calc_pattern_group_multiplier()
        length_multiplier = self._calc_pattern_length_multiplier()

        print(f"{'Variation Multiplier:':>25} {variation_multiplier}")
        print(f"{'Group Multiplier:':>25} {group_multiplier}")
        print(f"{'Length Multiplier:':>25} {length_multiplier}")

        print(f"Patterns: {self.patterns}")

        return variation_multiplier * group_multiplier

class OtherGroup(PatternGroup):

    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int = None, end_sample: int = None):
        super().__init__(group_name, patterns, start_sample, end_sample)
        self.weighting = 5

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        # if current_pattern.pattern_name != SIMPLE_NOTE:
        self.patterns.append(current_pattern)
        return True
        # return False

    def is_appendable(self) -> bool:
        return super().is_appendable()


class SlowStretch(PatternGroup):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int = None, end_sample: int = None):
        super().__init__(group_name, patterns, start_sample, end_sample)

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False
        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if "Interval" in current_pattern.pattern_name and (previous_pattern is None or "Interval" in previous_pattern.pattern_name):
            self.patterns.append(current_pattern)
            return True
        return False
    

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 2:
            for p in self.patterns:
                if "Interval" not in p.pattern_name:
                    raise ValueError(f"Slow Stretch has a: {p.pattern_name}!!")
            return True
        return False


    def _calc_variation_score(self) -> float:
        # Variation score for Slow Stretches is based on column variation rather than pattern variation

        lst = []
        unique_sample_times = set()
        for p in self.patterns:
            for n in p.notes:
                if n.sample_time not in unique_sample_times:
                    lst.append(n.lane)
                    unique_sample_times.add(n.sample_time)
        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]

        entropy = -sum(p * math.log2(p) for p in freq)

        return entropy
    
class VaryingStacksGroup(PatternGroup):

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        if self.pattern_is_interval(current_pattern):
            at_start = self.add_interval_is_at_start(current_pattern)
            if not at_start:
                # We end the pattern here.
                return False
            return True
        
        # Check if current pattern is straight up invalid
        if not self.is_n_stack(current_pattern):
            return False

        # Current pattern should be valid from here
        self.patterns.append(current_pattern)
        return True

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 2:
            # Needs at least 2 n-stacks to be valid
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and not self.pattern_is_interval(p):
                    raise ValueError(f"Varying Stack has a: {p.pattern_name}!!")   
            if n_stack_count >= 2:
                return True
        return False

class EvenCirclesGroup(PatternGroup):
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if self.pattern_is_interval(current_pattern):
            at_start = self.add_interval_is_at_start(current_pattern)
            if not at_start:
                # We end the pattern here.
                return False
            return True

        # Check for invalid combinations of previous pattern and current pattern
        if not self.is_n_stack(current_pattern) and current_pattern.pattern_name != SWITCH:
            return False

        if previous_pattern:
            # If the previous pattern is an interval, then we can add it.
            if self.pattern_is_interval(previous_pattern):
                self.patterns.append(current_pattern)
                return True
            
            if previous_pattern.pattern_name == SWITCH and not self.is_n_stack(current_pattern):
                return False
            
            if self.is_n_stack(previous_pattern) and current_pattern.pattern_name != SWITCH:
                return False

            if not self.time_difference_is_tolerable(previous_pattern, current_pattern):
                return False

            if not self.interval_between_patterns_is_tolerable(previous_pattern, current_pattern):
                return False
        # Current pattern should be valid from here
        self.patterns.append(current_pattern)
        return True
        

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 3:
            # Sanity check that everything in it is only N-stacks or Switches
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.pattern_name != SWITCH and not self.pattern_is_interval(p):
                    raise ValueError(f"Even Circle has a: {p.pattern_name}!!")   
            if n_stack_count >= 2: # There must be at least 2 n_stacks to be valid
                return True
        return False
    
    def _calc_variation_score(self) -> float:
        # TODO:Variation should be between the variation of N-stacks
        return super()._calc_variation_score()

class SkewedCirclesGroup(PatternGroup):
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if self.pattern_is_interval(current_pattern):
            at_start = self.add_interval_is_at_start(current_pattern)
            if not at_start:
                # We end the pattern here.
                return False
            return True

        # Check for invalid combinations of previous pattern and current pattern
        if not self.is_n_stack(current_pattern) and current_pattern.pattern_name != ZIG_ZAG:
            return False
        
        if previous_pattern:
            # If the previous pattern is an interval, then we can add it.
            if self.pattern_is_interval(previous_pattern):
                self.patterns.append(current_pattern)
                return True
            
            if previous_pattern.pattern_name == ZIG_ZAG and not self.is_n_stack(current_pattern):
                return False
            
            if self.is_n_stack(previous_pattern) and current_pattern.pattern_name != ZIG_ZAG:
                return False

            if abs(current_pattern.time_difference - previous_pattern.time_difference) > TOLERANCE:
                return False

            if not self.interval_between_patterns_is_tolerable(previous_pattern, current_pattern):
                return False
            
        if current_pattern.pattern_name == ZIG_ZAG and len(current_pattern.notes) != 3:
            return False
            
        # Current pattern should be valid from here
        self.patterns.append(current_pattern)

        return True


    def is_appendable(self) -> bool:
        if len(self.patterns) >= 3:
            # Sanity check that everything in it is only N-stacks or ZIG ZAGS
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.pattern_name != ZIG_ZAG and not self.pattern_is_interval(p):
                    raise ValueError(f"Skewed Circle has a: {p.pattern_name}!!")   
            if n_stack_count >= 2:
                return True
        return False


class NothingButTheoryGroup(PatternGroup):
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if self.pattern_is_interval(current_pattern):
            at_start = self.add_interval_is_at_start(current_pattern)
            if not at_start:
                # We end the pattern here.
                return False
            return True

        # Check for invalid combinations of previous pattern and current pattern
        if current_pattern.pattern_name != TWO_STACK and current_pattern.pattern_name != ZIG_ZAG:
            return False
        
        if current_pattern.pattern_name == ZIG_ZAG and len(current_pattern.notes) not in  [4, 6]:
            return False


        if previous_pattern:
            # If the previous pattern is an interval, then we can add it.
            if self.pattern_is_interval(previous_pattern):
                self.patterns.append(current_pattern)
                return True
            
            if previous_pattern.pattern_name == ZIG_ZAG and current_pattern.pattern_name != TWO_STACK:
                return False
            
            if previous_pattern.pattern_name == TWO_STACK and current_pattern.pattern_name != ZIG_ZAG:
                return False

            if abs(current_pattern.time_difference - previous_pattern.time_difference) > TOLERANCE:
                return False

            if not self.interval_between_patterns_is_tolerable(previous_pattern, current_pattern):
                return False
            

            
        # Current pattern should be valid from here
        self.patterns.append(current_pattern)

        return True


    def is_appendable(self) -> bool:

        if len(self.patterns) >= 3:
            # Sanity check that everything in it is only N-stacks or ZIG ZAGS
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if p.pattern_name != TWO_STACK and p.pattern_name != ZIG_ZAG and not self.pattern_is_interval(p):
                    raise ValueError(f"Nothing but theory has a: {p.pattern_name}!!")   
            if n_stack_count >= 2:
                return True
        return False

    def _calc_variation_score(self) -> float:
        # TODO: Variation is in the form of variation between ZigZag 4 and ZigZag 6
        return super()._calc_variation_score()
