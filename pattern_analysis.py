from entities import Pattern, Note
from typing import List, Optional
from abc import ABC, abstractmethod
from constants import *

class PatternGroup(ABC):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int=None, end_sample: int=None):
        self.group_name = group_name
        self.patterns = patterns
        self.start_sample = start_sample
        self.end_sample = end_sample
        self.is_active = True
    def __repr__(self) -> str:
        if len(self.patterns) >= 5:
            p = self.patterns[:5]
            extra = f" | Last Five: {self.patterns[-5:]}... ({len(self.patterns)} total)"
        else:
            p = self.patterns
            extra = ""
        return f"{self.group_name}, {p}{extra}"
    @abstractmethod
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        pass

    @abstractmethod
    def reset_group(self, current_pattern: Pattern):
        pass

    @abstractmethod
    def is_appendable(self) -> bool:
        pass

    def is_n_stack(self, pattern: Pattern):
        return pattern.pattern_name in ("2-Stack", "3-Stack", "4-Stack")

    def interval_between_patterns_is_tolerable(self, previous_pattern: Pattern, current_pattern: Pattern) -> bool:
        assert len(previous_pattern.notes) > 1
        assert len(current_pattern.notes) > 1
        end_of_first = previous_pattern.notes[-1].sample_time
        start_of_second = current_pattern.notes[0].sample_time
        time_difference = abs(end_of_first - start_of_second)
        if time_difference <= TOLERANCE:
            # The patterns pretty much have the same note
            return True
        return False
        # interval = abs(time_difference - previous_pattern.time_difference)
        # return interval <= TOLERANCE
class OtherGroup(PatternGroup):

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        # if current_pattern.pattern_name != SIMPLE_NOTE:
        self.patterns.append(current_pattern)
        return True
        # return False
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []

    def is_appendable(self) -> bool:
        return super().is_appendable()
class SimpleGroup(PatternGroup):

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False
        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if current_pattern.pattern_name == SIMPLE_NOTE and (previous_pattern is None or previous_pattern.pattern_name == SIMPLE_NOTE):
            print(f"added {current_pattern.pattern_name} to SimpleGroup")
            self.patterns.append(current_pattern)
            return True
        return False
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)
        self.is_active = True

    def is_appendable(self) -> bool:
        if len(self.patterns) > 0:
            for p in self.patterns:
                if p.pattern_name !=  SIMPLE_NOTE:
                    raise ValueError(f"Simple Group has a: {p.pattern_name}!!")
            return True
        return False

class VaryingStacksGroup(PatternGroup):

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if (previous_pattern is None or self.is_n_stack(previous_pattern)) and self.is_n_stack(current_pattern):
            self.patterns.append(current_pattern)
            print(f"added {current_pattern.pattern_name} to VaryingStacks")
            return True
        return False
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)
        self.is_active = True

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 2:
            # Sanity check that everything in it is only N-stacks
            for p in self.patterns:
                if not self.is_n_stack(p):
                    raise ValueError(f"Varying Stack has a: {p.pattern_name}!!")   
            return True
        return False

class EvenCirclesGroup(PatternGroup):
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        # Check for invalid combinations of previous pattern and current pattern
        if not self.is_n_stack(current_pattern) and current_pattern.pattern_name != SWITCH:
            return False
        if previous_pattern:
            if previous_pattern.pattern_name == SWITCH and not self.is_n_stack(current_pattern):
                return False
            
            if self.is_n_stack(previous_pattern) and current_pattern.pattern_name != SWITCH:
                return False

            if abs(current_pattern.time_difference - previous_pattern.time_difference) > TOLERANCE:
                return False

            if not self.interval_between_patterns_is_tolerable(previous_pattern, current_pattern):
                return False
        # Current pattern should be valid from here
        self.patterns.append(current_pattern)
        print(f"added {current_pattern.pattern_name} to EvenCirclesGroup")
        return True
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)
        self.is_active = True

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 3:
            # Sanity check that everything in it is only N-stacks or Switches
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.pattern_name != SWITCH:
                    raise ValueError(f"Even Circle has a: {p.pattern_name}!!")   
            if n_stack_count >= 2:
                return True
        return False
    

class SkewedCirclesGroup(PatternGroup):
    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:
        if not self.is_active:
            return False

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        # Check for invalid combinations of previous pattern and current pattern
        if not self.is_n_stack(current_pattern) and current_pattern.pattern_name != ZIG_ZAG:
            return False
        
        if previous_pattern:
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
        print(f"added {current_pattern.pattern_name} to SkewedCirclesGroup")
        return True



    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)
        self.is_active = True


    def is_appendable(self) -> bool:
        if len(self.patterns) >= 3:
            # Sanity check that everything in it is only N-stacks or ZIG ZAGS
            n_stack_count = 0
            for p in self.patterns:
                if self.is_n_stack(p):
                    n_stack_count += 1
                if not self.is_n_stack(p) and p.pattern_name != ZIG_ZAG:
                    raise ValueError(f"Skewed Circle has a: {p.pattern_name}!!")   
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
    
    def reset_groups(self):
        self.groups = [
            EvenCirclesGroup(EVEN_CIRCLES, []),
            SkewedCirclesGroup(SKEWED_CIRCLES, []),
            VaryingStacksGroup(VARYING_STACKS, []),
            SimpleGroup(SIMPLE_ONLY, []),
        ]
        self.other_group = OtherGroup(OTHER, [])

    def _return_final_groups(self, merge_other=True) -> List[PatternGroup]:
        if merge_other:
            new_groups = []
            current_other = None
            for pg in self.pattern_groups:
                if pg.group_name != OTHER:
                    if current_other is not None:
                        new_groups.append(current_other)
                        # TODO, set the start and end times
                        current_other = None
                    new_groups.append(pg)
                else:
                    if current_other is None:
                        current_other = OtherGroup(OTHER, [])
                    current_other.patterns += pg.patterns
            if current_other is not None:
                new_groups.append(current_other)
            return new_groups
        else:
            return self.pattern_groups


    def identify_pattern_groups(self, patterns_list: List[Pattern]) -> List[PatternGroup]:

        # TODO: account f or the duration between patterns too.
        # Lets just first identify Single Notes and Varying Stacks only
    
        for i in range(0, len(patterns_list)):
            current_pattern = patterns_list[i]
            print(f"\nCurrent pattern: {current_pattern.pattern_name}")
            added = False # has this pattern been added?

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
                        self.other_group.reset_group(current_pattern) # reset OtherGroup
                        print(f"{type(group_copy).__name__} | Appended {group_copy.group_name} with groups: {group_copy.patterns}")
                        # Reset all groups with current pattern.
                        for group in self.groups:
                            group.reset_group(current_pattern)

            self.other_group.check_pattern(current_pattern)
            # print(f"Added = True... Other Group is {self.other_group.patterns}")

            # We have gone through all the defined groups...
            if not added: 
                # Append OtherGroup if no other groups were appendale
                print(f"No other group appendable... appending Other with {self.other_group.patterns}")
                self.pattern_groups.append(OtherGroup(OTHER, self.other_group.patterns, self.other_group.start_sample, self.other_group.end_sample))
                self.other_group.reset_group(current_pattern) # reset OtherGroup
                # Reset all groups with current pattern.
                for group in self.groups:
                    group.reset_group(current_pattern)

        # Do last check
        for last__check_group in self.groups:
            if last__check_group.is_appendable():
                print(f"{last__check_group.group_name} is appendable with {last__check_group.patterns}")
                last_group_copy = last__check_group.__class__(last__check_group.group_name, last__check_group.patterns, last__check_group.start_sample, last__check_group.end_sample)
                self.pattern_groups.append(last_group_copy)
                return self._return_final_groups()
        if len(self.other_group.patterns) > 0: 
            last_group_copy = OtherGroup(OTHER, self.other_group.patterns, self.other_group.start_sample, self.other_group.end_sample)
            self.pattern_groups.append(last_group_copy)

        

        return self._return_final_groups()


        


if __name__ == "__main__":
    simple = Pattern(SIMPLE_NOTE, [], 0, 1 * TIME_CONVERSION)
    two = Pattern(TWO_STACK, [], 0, 1 * TIME_CONVERSION)
    three = Pattern(THREE_STACK, [], 0, 1 * TIME_CONVERSION)
    four = Pattern(FOUR_STACK, [], 0, 1 * TIME_CONVERSION)
    switch = Pattern(SWITCH, [], 0, 1 * TIME_CONVERSION)
    zig_zag = Pattern(ZIG_ZAG, [], 0, 1 * TIME_CONVERSION)
    stream = Pattern(SINGLE_STREAMS, [], 0, 1 * TIME_CONVERSION)

    patterns = [
        Pattern(TWO_STACK, [Note(0, 21.42 * TIME_CONVERSION), Note(0, 21.60 * TIME_CONVERSION)]),
        Pattern(SWITCH, [Note(0, 21.60 * TIME_CONVERSION), Note(0, 21.78 * TIME_CONVERSION)]),
        Pattern(TWO_STACK, [Note(0, 21.78 * TIME_CONVERSION), Note(0, 21.96 * TIME_CONVERSION)])
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)

    print("="*25)
    for  g in groups:
        print(f"{g.group_name} | {g.patterns}")