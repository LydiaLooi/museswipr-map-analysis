import math
from abc import ABC, abstractmethod
from typing import List, Optional

from constants import *
from entities import Note, Segment
from pattern_multipliers import stream_multiplier, zig_zag_multiplier, even_circle_multiplier, skewed_circle_multiplier, zig_zag_length_multiplier, nothing_but_theory_multiplier

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

        self.entropy_weighting = 0.5
        self.distance_weighting = 0.5

    @property
    def approx_total_notes(self): # because i cbf make it accurate ((:
        note_count = 0
        for p in self.segments:
            note_count += len(p.notes)
            if len(p.notes) >= 3:
                note_count -= 2 # -2 for the overlap of segments approx
        return note_count

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
    def is_n_stack(pattern: Segment):
        return pattern.segment_name in ("2-Stack", "3-Stack", "4-Stack")

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
        
    def _calc_variation_score(self) -> float:
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
        end_extra_debuff = 0.75 # For if the interval is at the start or end

        intervals = {
            SHORT_INTERVAL: 0.7,
            MED_INTERVAL: 0.6,
            LONG_INTERVAL: 0.4
        }
        # Thanks to ChatGPT for writing this for me
        temp_lst = [s.segment_name for s in self.segments]
        switch_count = 0
        interval_list = []
        lst = []

        # Check for intervals:
        for i, name in enumerate(temp_lst):
            if name == SWITCH:
                switch_count += 1
            if name in intervals:
                if i == 0 or i == len(temp_lst) - 1: # If it's the firs
                    interval_list.append(intervals[name] * end_extra_debuff)
                    # Don't add it to the list to check
                else:
                    interval_list.append(intervals[name])
                    lst.append("Interval") # Rename all Intervals to the same name
            else:
                lst.append(name)

        
        print(f"Checking entropy of: {lst}")
        n = len(lst)
        unique_vals = set(lst)
        freq = [lst.count(x) / n for x in unique_vals]
        entropy = -sum(p * math.log2(p) for p in freq)

        if len(interval_list) != 0:
            # average interval debuffs and multiply that by the entropy
            average_debuff = sum(interval_list)/len(interval_list)
            entropy *= average_debuff
            print(f">>> Debuffing (due to Intervals) by {average_debuff} <<<")

        if entropy > 1 and switch_count > 0:
            # switch_debuff = switch_count/len(lst)
            switch_debuff = 0.75
            print(f">>> Debuffing (Die to Switches) by {switch_debuff:.2f} <<<")
            entropy *= switch_debuff

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

    def calc_pattern_difficulty(self) -> float:

        print(f"{self.group_name:.>25} {'Difficulty':.<25}")
        variation_multiplier = self._calc_variation_score()
        group_multiplier = self._calc_pattern_multiplier()
        length_multiplier = self._calc_pattern_length_multiplier()

        print(f"{'Variation Multiplier:':>25} {variation_multiplier}")
        print(f"{'Group Multiplier:':>25} {group_multiplier}")
        print(f"{'Length Multiplier:':>25} {length_multiplier}")

        print(f"Segments: {self.segments}")

        return variation_multiplier * group_multiplier * length_multiplier

class OtherPattern(Pattern):

    def __init__(self, group_name: str, patterns: List[Segment], start_sample: int = None, end_sample: int = None):
        super().__init__(group_name, patterns, start_sample, end_sample)
        self.weighting = 5

    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        self.segments.append(current_segment)
        return True

    def is_appendable(self) -> bool:
        return super().is_appendable()


class SlowStretchPattern(Pattern):
    def __init__(self, group_name: str, segments: List[Segment], start_sample: int = None, end_sample: int = None):
        super().__init__(group_name, segments, start_sample, end_sample)

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


    def _calc_variation_score(self) -> float:
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
    
    def _calc_variation_score(self) -> float:
        # TODO:Variation should be between the variation of N-stacks
        return super()._calc_variation_score()
    
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
        if current_segment.segment_name != TWO_STACK and current_segment.segment_name != ZIG_ZAG:
            return False
        
        if current_segment.segment_name == ZIG_ZAG and len(current_segment.notes) not in  [4, 6]:
            return False


        if previous_segment:
            # If the previous segment is an interval, then we can add it.
            if self.segment_is_interval(previous_segment):
                self.segments.append(current_segment)
                return True
            
            if previous_segment.segment_name == ZIG_ZAG and current_segment.segment_name != TWO_STACK:
                return False
            
            if previous_segment.segment_name == TWO_STACK and current_segment.segment_name != ZIG_ZAG:
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
            for p in self.segments:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if p.segment_name != TWO_STACK and p.segment_name != ZIG_ZAG and not self.segment_is_interval(p):
                    raise ValueError(f"Nothing but theory has a: {p.segment_name}!!")   
            if n_stack_count >= 2:
                return True
        return False

    def _calc_variation_score(self) -> float:
        # TODO: Variation is in the form of variation between ZigZag 4 and ZigZag 6
        return super()._calc_variation_score()

    def _calc_pattern_multiplier(self) -> float:
        nps = self.segments[0].notes_per_second

        multiplier = nothing_but_theory_multiplier(nps)
        return multiplier