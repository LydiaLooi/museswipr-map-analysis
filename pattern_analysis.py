from entities import Pattern, Note
from typing import List, Optional
from abc import ABC, abstractmethod
from constants import *

class PatternGroup(ABC):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int=None, end_sample: int=None):
        self.group_name = group_name
        self.patterns = patterns
        self.start_sample = start_sample # (UNUSED)
        self.end_sample = end_sample # (UNUSED)
        self.is_active = True
        self.is_interval = False # This is to identify the "Simple Only" equivalent classes (UNUSED)
        self.weighting = 1

    @property
    def approx_total_notes(self): # because i cbf make it accurate ((:
        note_count = 0
        for p in patterns:
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
    def get_difficulty_score(self):
        return 1

    @abstractmethod
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        pass

    def reset_group(self, previous_pattern: Pattern, current_pattern: Pattern):
        
        # print(f"==== RESETTING {self.group_name} ===")
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

        # print(f"-----DONE... {self.patterns}")

    @abstractmethod
    def is_appendable(self) -> bool:
        pass

    def is_n_stack(self, pattern: Pattern):
        return pattern.pattern_name in ("2-Stack", "3-Stack", "4-Stack")

    def pattern_is_interval(self, pattern: Pattern):
        return "Interval" in pattern.pattern_name

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
    
    def get_difficulty_score(self) -> float:
        # Create a mapping of pattern names to difficulty scores
        pattern_difficulty = {
            SWITCH: 1.9,
            ZIG_ZAG: 1.3,
            TWO_STACK: 1.2,
            THREE_STACK: 1.3,
            FOUR_STACK: 1.4,
            SINGLE_STREAMS: 1.4,
            SHORT_INTERVAL: 0.7,
            MED_INTERVAL: 0.6,
            LONG_INTERVAL: 0.5,
        }

        HAS_INTERVAL = 0.8
        NO_INTERVAL = 1.2

        # Calculate the total weighted difficulty score of the group's patterns
        total_weighted_difficulty = 0
        total_weighting = 0
        for pattern in self.patterns:
            # Look up the difficulty score for the pattern name
            difficulty_score = pattern_difficulty.get(pattern.pattern_name, 0)
            
            # Calculate the weighted difficulty score for the pattern
            weighted_difficulty = difficulty_score * self.weighting
            
            # Add the weighted difficulty score to the total
            total_weighted_difficulty += weighted_difficulty
            total_weighting += self.weighting

        # Calculate the average weighted difficulty score
        if total_weighting > 0:
            average_weighted_difficulty = total_weighted_difficulty / total_weighting
            print(f"AVERAGE WEIGHTED DIFFICULTY: {average_weighted_difficulty}")
        else:
            average_weighted_difficulty = 0

        # Apply any adjustment factors based on the group's properties or context
        # Here you can add any heuristics that you believe can adjust the difficulty score based on the context
        # For example, you might adjust the difficulty score based on the speed of the music or the number of notes in the patterns

        # Clamp the difficulty score to the range [0, 1]
        difficulty_score = max(0, min(2, average_weighted_difficulty))

        return difficulty_score

class SlowStretch(PatternGroup):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int = None, end_sample: int = None):
        super().__init__(group_name, patterns, start_sample, end_sample)
        self.is_interval = True

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False
        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if "Interval" in current_pattern.pattern_name and (previous_pattern is None or "Interval" in previous_pattern.pattern_name):
            # print(f"added {current_pattern.pattern_name} to SlowStretch")
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

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        # Check if current pattern is straight up invalid
        if not self.is_n_stack(current_pattern):
            return False

        # Current pattern should be valid from here
        self.patterns.append(current_pattern)
        # print(f"added {current_pattern.pattern_name} to VaryingStacksGroup")
        return True

    def is_appendable(self) -> bool:
        # print(f"@@@CHECKING IF VARYING STACK IS APPENDABLE with {self.patterns}")
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
                # print(f"added {current_pattern.pattern_name} to EvenCirclesGroup")
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
        # print(f"added {current_pattern.pattern_name} to EvenCirclesGroup")
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
                # print(f"added {current_pattern.pattern_name} to SkewedCirclesGroup")
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
        # print(f"added {current_pattern.pattern_name} to SkewedCirclesGroup")
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
                # print(f"added {current_pattern.pattern_name} to SkewedCirclesGroup")
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
        # print(f"added {current_pattern.pattern_name} to NothingButTheory")
        return True


    def is_appendable(self) -> bool:
        # print(f"+++Checking if nothing but theory is appendable with: {self.patterns}")

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

class MapPatternGroups:

    def __init__(self):
        # **THE** list of PatternGroups
        self.pattern_groups: List[PatternGroup] = []

        # Keeps track during analysis of whether a pattern has been appended
        self.pattern_group_appended: bool = False
        self.pattern_group_appended_name: str = ""

        self.groups = []

        self.other_group = OtherGroup(OTHER, [])
        self.reset_groups()

    def is_n_stack(self, pattern: Pattern):
        return pattern.pattern_name in ("2-Stack", "3-Stack", "4-Stack")
    
    def pattern_is_interval(self, pattern: Pattern):
        return "Interval" in pattern.pattern_name

    def reset_groups(self):
        self.groups = [
            EvenCirclesGroup(EVEN_CIRCLES, []),
            SkewedCirclesGroup(SKEWED_CIRCLES, []),
            VaryingStacksGroup(VARYING_STACKS, []),
            NothingButTheoryGroup(NOTHING_BUT_THEORY, []),
            SlowStretch(SLOW_STRETCH, []),
        ]
        self.other_group = OtherGroup(OTHER, [])

    def _return_final_groups(self, merge_other=True) -> List[PatternGroup]:
        """
        Returns the final list of pattern groups after merging, if merge_other is True.
        """
        if not merge_other:
            return self.pattern_groups

        new_groups = []
        current_other = None
        is_first = True
        for pg in self.pattern_groups:
            if pg.group_name != OTHER:
                current_other = self._handle_non_other_group(new_groups, current_other, pg)
                is_first = True
            else:
                current_other, is_first = self._handle_other_group(current_other, pg, is_first)

        if current_other is not None and len(current_other.patterns) > 0:
            new_groups.append(current_other)
        return new_groups

    def _handle_non_other_group(self, new_groups, current_other, pg):
        """
        Handles non-OTHER groups while merging pattern groups.
        """
        if current_other is not None:
            if not self.pattern_is_interval(current_other.patterns[-1]):
                current_other.patterns = current_other.patterns[:-1]
            new_groups.append(current_other)
            current_other = None
        new_groups.append(pg)
        return current_other

    def _handle_other_group(self, current_other, pg, is_first):
        """
        Handles OTHER groups while merging pattern groups.
        """
        if current_other is None:
            current_other = OtherGroup(OTHER, [])
        if is_first:
            current_other = self._handle_first_other_group(current_other, pg)
        else:
            current_other = self._handle_not_first_other_group(current_other, pg)
        if current_other:
            is_first = False
        return current_other, is_first

    def _handle_first_other_group(self, current_other, pg):
        """
        Handles the first occurrence of an OTHER group while merging pattern groups.
        """
        if len(self.pattern_groups) > 1 and len(pg.patterns) == 1 and self.pattern_is_interval(pg.patterns[0]):
            current_other = None
        else:
            current_other.patterns += pg.patterns
        return current_other

    def _handle_not_first_other_group(self, current_other, pg):
        """
        Handles subsequent occurrences of OTHER groups while merging pattern groups.
        """
        if len(pg.patterns) > 2:
            if self.pattern_is_interval(pg.patterns[0]):
                current_other.patterns += pg.patterns[1:]
            else:
                current_other.patterns += pg.patterns[2:]
        return current_other




    def identify_pattern_groups(self, patterns_list: List[Pattern], merge_other: bool = True) -> List[PatternGroup]:
        for i in range(0, len(patterns_list)):
            current_pattern = patterns_list[i]

            if len(patterns_list) > 1 and i != 0:
                previous_pattern: Optional[Pattern] = patterns_list[i-1]
            else:
                previous_pattern: Optional[Pattern]  = None

            # if previous_pattern:
                # print(f"\nPrevious pattern: {previous_pattern.pattern_name}")
            # else:
                # print("\nPrevious pattern: NONE")
            # print(f"Current pattern: {current_pattern.pattern_name}")
            added = False # has this pattern been added?
            reset = False # have we done a reset?
            for group in self.groups:
                group: PatternGroup
                _added = group.check_pattern(current_pattern)
                if _added == True:
                    added = True
                else: 
                    if len(group.patterns) > 0:
                        group.is_active = False # Only set it to inactive if it's already begun adding stuff

                    # Check if the group is appendable
                    if group.is_appendable():
                        # Need to first check if OtherGroup has stragglers...
                        if len(group.patterns) < len(self.other_group.patterns):
                            # THERE ARE STRAGGLERS. 
                            # print(f"THERE ARE STRAGGLERS {group.patterns} | {self.other_group.patterns}")
                            other_group = OtherGroup(OTHER, self.other_group.patterns[:-len(group.patterns)])
                            self.pattern_groups.append(other_group)

                        added = True
                        group_copy = group.__class__(group.group_name, group.patterns, group.start_sample, group.end_sample)
                        self.pattern_groups.append(group_copy)
                        # print(f"{type(group_copy).__name__} | Appended {group_copy.group_name} with groups: {group_copy.patterns}")
                        # Reset all groups with current pattern.
                        for group in self.groups:
                            group.reset_group(previous_pattern, current_pattern)
                        self.other_group.reset_group(previous_pattern, current_pattern) # reset OtherGroup
                        reset = True
                        break # STOP LOOKING !! WE FOUND SOMETHING
            if not reset:
                self.other_group.check_pattern(current_pattern)
                # print(f"...Adding {current_pattern.pattern_name} to other...: {self.other_group.patterns}")
            # else:
                # print("...Already reset... so not adding to other_group")
            # print(f"Added = True... Other Group is {self.other_group.patterns}")

            # We have gone through all the defined groups...
            if not added: 
                # Append OtherGroup if no other groups were appendale
                # print(f"No other group appendable... appending Other with {self.other_group.patterns}")
                self.pattern_groups.append(OtherGroup(OTHER, self.other_group.patterns, self.other_group.start_sample, self.other_group.end_sample))
                self.other_group.reset_group(previous_pattern, current_pattern) # reset OtherGroup
                # Reset all groups with current pattern.
                for group in self.groups:
                    group.reset_group(previous_pattern, current_pattern)

        # Do last check
        for last_check_group in self.groups:
            if last_check_group.is_appendable():
                # print(f"{last_check_group.group_name} is appendable with {last_check_group.patterns}")
                last_group_copy = last_check_group.__class__(last_check_group.group_name, last_check_group.patterns, last_check_group.start_sample, last_check_group.end_sample)
                self.pattern_groups.append(last_group_copy)
                return self._return_final_groups(merge_other)
        if len(self.other_group.patterns) > 0:

            # If there is a hanging SINGLE Interval at the end of the pattern, don't add it... unless it is the only one in the group list
            if len(self.pattern_groups) == 0 or not (len(self.other_group.patterns) == 1 and self.pattern_is_interval(self.other_group.patterns[0])):
                last_group_copy = OtherGroup(OTHER, self.other_group.patterns, self.other_group.start_sample, self.other_group.end_sample)
                self.pattern_groups.append(last_group_copy)
        

        return self._return_final_groups(merge_other)


        


if __name__ == "__main__":
    dummy_note = Note(0, 0)

    short_interval = Pattern(SHORT_INTERVAL, [dummy_note, dummy_note], 0, 0)
    med_interval = Pattern(MED_INTERVAL, [dummy_note, dummy_note], 0, 0)
    long_interval = Pattern(LONG_INTERVAL, [dummy_note, dummy_note], 0, 0)
    two = Pattern(TWO_STACK, [dummy_note, dummy_note], 0, 0)
    three = Pattern(THREE_STACK, [dummy_note, dummy_note], 0, 0)
    four = Pattern(FOUR_STACK, [dummy_note, dummy_note], 0, 0)
    switch = Pattern(SWITCH, [dummy_note, dummy_note], 0, 0)
    zig_zag = Pattern(ZIG_ZAG, [dummy_note, dummy_note], 0, 0)
    stream = Pattern(SINGLE_STREAMS, [dummy_note, dummy_note], 0, 0)

    def _Note(lane, seconds):
        return Note(lane, seconds * TIME_CONVERSION)
    

    # patterns = [
    #     short_interval, switch, med_interval, switch, long_interval
    # ]

    patterns = [
        Pattern(LONG_INTERVAL, [_Note(0, 0), _Note(0, 10)], 0),
        Pattern(TWO_STACK, [_Note(0, 10), _Note(0, 10.1)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 10.1), _Note(0, 10.2), _Note(0, 10.3)], 0),
        Pattern(TWO_STACK, [_Note(0, 10.3), _Note(0, 10.4)], 0),
        Pattern(SHORT_INTERVAL, [_Note(0, 10.4), _Note(0, 11)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)

    # groups = MapPatternGroups().identify_pattern_groups(patterns)

    print("="*25)
    for  g in groups:
        print(f"{g.group_name} | {g.patterns}")