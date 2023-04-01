from entities import Pattern
from typing import List, Optional
from abc import ABC, abstractmethod

SWITCH = "Switch"
ZIG_ZAG = "Zig Zag"
TWO_STACK = "2-Stack"
THREE_STACK = "3-Stack"
FOUR_STACK = "4-Stack"
SINGLE_STREAMS = "Single Streams"
SIMPLE_NOTE = "Simple Notes"

SIMPLE_ONLY = "Simple Only"
EVEN_CIRCLES = "Even Circles"
SKEWED_CIRCLES = "Skewed Circles"
VARYING_STACKS = "Varying Stacks"
NOTHING_BUT_THEORY = "Nothing But Theory"
VARIABLE_STREAM = "Variable Stream"
OTHER = "Other"

class PatternGroup(ABC):
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int=None, end_sample: int=None):
        self.group_name = group_name
        self.patterns = patterns
        self.start_sample = start_sample
        self.end_sample = end_sample
    def __repr__(self) -> str:
        if len(self.patterns) >= 5:
            p = self.patterns[:5]
            extra = f" ({len(self.patterns)} total)"
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

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if current_pattern.pattern_name == SIMPLE_NOTE and (previous_pattern is None or previous_pattern.pattern_name == SIMPLE_NOTE):
            print(f"added {current_pattern.pattern_name} to SimpleGroup")
            self.patterns.append(current_pattern)
            return True
        return False
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)

    def is_appendable(self) -> bool:
        if len(self.patterns) > 0:
            for p in self.patterns:
                if p.pattern_name !=  SIMPLE_NOTE:
                    raise ValueError(f"Simple Group has a: {p.pattern_name}!!")
            return True
        return False

class VaryingStacksGroup(PatternGroup):

    def check_pattern(self, current_pattern: Pattern) -> Optional[bool]:

        previous_pattern: Optional[Pattern] = self.patterns[-1] if len(self.patterns) > 0 else None

        if (previous_pattern is None or self.is_n_stack(previous_pattern)) and self.is_n_stack(current_pattern):
            self.patterns.append(current_pattern)
            print(f"added {current_pattern.pattern_name} to VaryingStacks")
            return True
        return False
    
    def reset_group(self, current_pattern: Pattern):
        self.patterns = []
        self.check_pattern(current_pattern)

    def is_appendable(self) -> bool:
        if len(self.patterns) >= 2:
            # Sanity check that everything in it is only N-stacks
            for p in self.patterns:
                if not self.is_n_stack(p):
                    raise ValueError(f"Varying Stack has a: {p.pattern_name}!!")   
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
            SimpleGroup(SIMPLE_ONLY, []),
            VaryingStacksGroup(VARYING_STACKS, [])
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
    simple = Pattern(SIMPLE_NOTE, [], 0)
    two = Pattern(TWO_STACK, [], 0)
    three = Pattern(THREE_STACK, [], 0)
    four = Pattern(FOUR_STACK, [], 0)
    switch = Pattern(SWITCH, [], 0)
    zig_zag = Pattern(ZIG_ZAG, [], 0)
    stream = Pattern(SINGLE_STREAMS, [], 0)


    
    patterns = [
        simple, simple, 
        two, three, 
        switch, zig_zag, switch, two, zig_zag, stream]
    groups = MapPatternGroups().identify_pattern_groups(patterns)

    print("="*25)
    for  g in groups:
        print(f"{g.group_name} | {g.patterns}")