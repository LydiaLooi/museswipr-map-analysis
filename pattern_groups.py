import math
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from constants import *
from entities import Note, Segment
from pattern_multipliers import even_circle_multiplier, skewed_circle_multiplier, nothing_but_theory_multiplier,stream_multiplier, zig_zag_multiplier, zig_zag_length_multiplier, two_stack_multiplier, four_stack_multiplier, three_stack_multiplier, varying_stacks_multiplier, pattern_stream_length_multiplier

class Pattern(ABC):
    def __init__(self, pattern_name: str, segments: List[Segment], start_sample: int=None, end_sample: int=None, sample_rate: int=DEFAULT_SAMPLE_RATE):
        self.group_name = pattern_name
        self.segments = segments
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.is_active = True
        self.weighting = 1

        self.sample_rate = sample_rate
        self.tolerance = 20 * sample_rate // 1000

        self.variation_weighting = 0.5
        self.pattern_weighting = 0.5

        self.intervals = {
            SHORT_INTERVAL: 0.7,
            MED_INTERVAL: 0.6,
            LONG_INTERVAL: 0.4
        }

        self.end_extra_debuff = 0.9 # For if the interval is at the start or end


    def __repr__(self) -> str:
        if len(self.segments) >= 5:
            p = self.segments[:5]
            extra = f" | Last Five: {self.segments[-5:]}... ({len(self.segments)} total)"
        else:
            p = self.segments
            extra = ""
        if len(self.segments) > 0:
            return f"{self.segments[0].notes[0].sample_time/DEFAULT_SAMPLE_RATE:.2f} | {self.group_name}, {p}{extra}"
        else:
            return f"{self.group_name}, {p}"

    @abstractmethod
    def check_segment(self, current_pattern: Segment) -> Optional[bool]:
        pass


    @abstractmethod
    def is_appendable(self) -> bool:
        pass

    @staticmethod
    def is_n_stack(segment: Segment):
        return segment.segment_name in ("2-Stack", "3-Stack", "4-Stack")

    def segment_is_interval(self, segment: Segment):
        if segment:
            return "Interval" in segment.segment_name
        return False
    
    def time_difference_is_tolerable(self, previous_segment: Segment, current_segment: Segment):
        assert previous_segment.time_difference is not None
        assert current_segment.time_difference is not None

        # If the previous or current segment is an Interval, return True
        if self.segment_is_interval(previous_segment) or self.segment_is_interval(current_segment):
            return True
        
        result = abs(current_segment.time_difference - previous_segment.time_difference) <= self.tolerance

        return result

    def interval_between_segments_is_tolerable(self, previous_segment: Segment, current_segment: Segment) -> bool:
        assert len(previous_segment.notes) > 1
        assert len(current_segment.notes) > 1
        # If the previous or current segment is an Interval, return True
        if self.segment_is_interval(previous_segment) or self.segment_is_interval(current_segment):
            return True
        end_of_first = previous_segment.notes[-1].sample_time
        start_of_second = current_segment.notes[0].sample_time
        time_difference = abs(end_of_first - start_of_second)
        if time_difference <= self.tolerance:
            # The segments pretty much have the same note
            return True
        return False
    
    def reset_group(self, previous_segment: Segment, current_segment: Segment):
        self.is_active = True
        self.segments = []

        # If previous or current_segment is an Interval, then only add that one (prioritise the latest one).
        if self.segment_is_interval(current_segment):
            self.check_segment(current_segment)

        elif self.segment_is_interval(previous_segment):
            self.check_segment(previous_segment)
            self.check_segment(current_segment)
            
        # If not, then attempt to add the previous one first, then the current one too
        # If it fails at any point, set the group to inactive
        else:
            if previous_segment:
                added = self.check_segment(previous_segment)
                if added:
                    added = self.check_segment(current_segment)
                
                if added is False:
                    self.is_active = False

    def add_interval_is_at_start(self, interval_segment: Segment) -> bool:
        """
        Adds the interval segment to the segments list
        Returns True if it is the first element
        Returns False if is not 
        """
        if len(self.segments) == 0:
            self.segments.append(interval_segment)
            return True
        else:
            self.segments.append(interval_segment)
            return False
        
    def _get_segment_type_counts(self, segment_names):
        segment_counts = {
            SWITCH: 0,
            ZIG_ZAG: 0,
            TWO_STACK: 0,
            THREE_STACK: 0,
            FOUR_STACK: 0,
            SINGLE_STREAMS: 0,
            SHORT_INTERVAL: 0,
            MED_INTERVAL: 0,
            LONG_INTERVAL: 0
        }
        for name in segment_names:
            segment_counts[name] += 1
        return segment_counts

    def _calc_switch_debuff(self, segment_counts: Dict[str, int], entropy: float, pls_print=False) -> float:
        """Looks at the number of switches with relation to how many segments there are.
        
        A low segment count (<4) such as [zig zag, switch, zig zag] will be debuffed
        more heavily than a long arrangement of segments with more switches. A higher
        switch proportion results in less debuff.

        Args:
            segment_counts (Dict[str: int]): The dictionary of segment type counts 
            entropy (float): The current entropy value

        Returns:
            float: The entropy affected by the debuff
        """
        switch_proportion = None
        switch_count = segment_counts[SWITCH]
        total_patterns = sum(segment_counts.values())
        if entropy > 1 and switch_count > 0:
            if total_patterns < 4:
                switch_debuff = 0.7
            else:
                switch_proportion = switch_count/total_patterns
                if switch_proportion < 0.5:
                    switch_debuff = 0.8
                else:
                    switch_debuff = 0.9 # if there are more switches, then don't make the buff as hard
            if pls_print:
                print(f">>> Switch (proportion {switch_proportion}) debuff by {switch_debuff:.2f} <<<")
            entropy *= switch_debuff
        return entropy

    def _calc_variation_score(self, pls_print=False) -> float:
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
    
    
    def _calc_pattern_multiplier(self) -> float:
        """Calculates the PatternGroup's multiplier based on notes per secondo
        This method should be overridded to be PatternGroup specific.
        Default returns 1.

        Returns:
            float: The multiplier
        """
        return 1
    
    def _calc_pattern_length_multiplier(self) -> float:
        return 1

    def calc_pattern_difficulty(self, pls_print=False) -> float:
        if pls_print:
            print(f"{self.group_name:.>25} {'Difficulty':.<25}")
        variation_multiplier = self._calc_variation_score()
        pattern_multiplier = self._calc_pattern_multiplier()
        length_multiplier = self._calc_pattern_length_multiplier()

        final = (self.variation_weighting * variation_multiplier) + (self.pattern_weighting * pattern_multiplier)

        if pls_print:
            print(f"{'Variation Multiplier:':>25} {variation_multiplier}")
            print(f"{'Pattern Multiplier:':>25} {pattern_multiplier}")
            print(f"{'Length Multiplier:':>25} {length_multiplier}")
            print(f"{'After Weighting:':>25} {final}")

        return final

class OtherPattern(Pattern):

    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.segments.append(current_segment)
        return True

    def is_appendable(self) -> bool:
        return super().is_appendable()
    
    def _calc_pattern_multiplier(self) -> float:

        for segment in self.segments:
            pass
        
        return 1


class SlowStretchPattern(Pattern):

    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        if not self.is_active:
            return False
        previous_segment: Optional[Segment] = self.segments[-1] if len(self.segments) > 0 else None

        if "Interval" in current_segment.segment_name and (previous_segment is None or "Interval" in previous_segment.segment_name):
            self.segments.append(current_segment)
            return True
        return False
    

    def is_appendable(self) -> bool:
        if len(self.segments) >= 2:
            for p in self.segments:
                if "Interval" not in p.segment_name:
                    raise ValueError(f"Slow Stretch has a: {p.segment_name}!!")
            return True
        return False


    def _calc_variation_score(self, pls_print=False) -> float:
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
    
class VaryingStacksPattern(Pattern):

    def __init__(self, pattern_name: str, segments: List[Segment], start_sample: int = None, end_sample: int = None, sample_rate: int = DEFAULT_SAMPLE_RATE):
        super().__init__(pattern_name, segments, start_sample, end_sample, sample_rate)
        self.pattern_weighting = 0.8
        self.variation_weighting = 0.2

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
    
    def _calc_variation_score(self, pls_print=False) -> float:
        return max(1, super()._calc_variation_score(pls_print))
    
    def _calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second
        multiplier = varying_stacks_multiplier(nps)
        return multiplier

class EvenCirclesGroup(Pattern):
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
    
    def _calc_variation_score(self, pls_print=False) -> float:
        return max(1, super()._calc_variation_score(pls_print))

    
    def _calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second # Even Circle should have consistent NPS
        multiplier = even_circle_multiplier(nps)
        return multiplier

class SkewedCirclesGroup(Pattern):
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
            
        if current_segment.segment_name == ZIG_ZAG and len(current_segment.notes) != 3:
            return False
            
        # Current segment should be valid from here
        self.segments.append(current_segment)

        return True


    def is_appendable(self) -> bool:
        if len(self.segments) >= 3:
            # Sanity check that everything in it is only N-stacks or ZIG ZAGS
            n_stack_count = 0
            for p in self.segments:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.segment_name != ZIG_ZAG and not self.segment_is_interval(p):
                    raise ValueError(f"Skewed Circle has a: {p.segment_name}!!")   
            if n_stack_count >= 2:
                return True
        return False

    def _calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second

        multiplier = skewed_circle_multiplier(nps)
        return multiplier

class NothingButTheoryGroup(Pattern):

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

    def _calc_variation_score(self, pls_print=False) -> float:
        # TODO: Make the calculation method into several helper methods.
        if pls_print:
            print("Note: Nothing but theory overrode _calc_variation_score")
        temp_lst = [f"{s.segment_name} {len(s.notes)}" for s in self.segments] # Zig Zags of different note lengths are considered different
        switch_count = 0
        interval_list = []
        lst = []

        segment_counts = self._get_segment_type_counts([s.segment_name for s in self.segments])

        # Check for intervals:
        for i, name in enumerate(temp_lst):
            if name == SWITCH:
                switch_count += 1
            elif name in self.intervals:
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

    def _calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second

        multiplier = nothing_but_theory_multiplier(nps)
        return multiplier