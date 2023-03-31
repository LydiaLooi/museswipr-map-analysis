from entities import Pattern
from typing import List, Optional

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

class PatternGroup:
    def __init__(self, group_name: str, patterns: List[Pattern], start_sample: int, end_sample: int):
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

class MapPatternGroups:

    def __init__(self):
        # **THE** list of PatternGroups
        self.pattern_groups: List[PatternGroup] = []

        # Keeps track during analysis of whether a pattern has been appended
        self.pattern_group_appended: bool = False
        self.pattern_group_appended_name: str = ""

        self.groups = []
        self.reset_groups()

    def is_n_stack(self, pattern: Pattern):
        return pattern.pattern_name in ("2-Stack", "3-Stack", "4-Stack")
    

    def reset_groups(self):
        self.groups = [
            PatternGroup(SIMPLE_ONLY, [], None, None),
            PatternGroup(VARYING_STACKS, [], None, None),
            PatternGroup(OTHER, [], None, None)
        ]

    def check_simple_notes(self, group: PatternGroup, current_pattern: Pattern, previous_pattern: Optional[Pattern]):
        # This should ensure that the Simple Only group only has simple notes
        if (previous_pattern is None or previous_pattern.pattern_name is SIMPLE_NOTE) and current_pattern.pattern_name == SIMPLE_NOTE :
            group.patterns.append(current_pattern)

            # Set the start sample initially. Always update the end sample
            if group.start_sample is None:
                group.start_sample = current_pattern.notes[0].sample_time
            group.end_sample = current_pattern.notes[-1].sample_time
            return True

        # The current pattern is NON-Simple Notes from here on out
        # We have found a pattern that doesn't fit this group. 
        if len(group.patterns) > 0:
            # Sufficient notes in this group to be a valid group
            for p in group.patterns: # Sanity check that everything in it is only Simple notes
                if p.pattern_name != SIMPLE_NOTE:
                    raise ValueError(f"There is a non-simple note in the simple only group: {p.pattern_name}")
            
            
            # Update the end sample to the previous note
            group.end_sample = previous_pattern.notes[-1].sample_time
            
            # Append and reset Other
            # group.patterns.append(current_pattern)
            self.groups[-1].patterns = []
            self.pattern_groups.append(group)
            self.pattern_group_appended = True
            self.pattern_group_appended_name = group.group_name
            return True
        else: 
            # Insufficient notes in this group
            # Reset this group and add the current pattern if valid
            group.patterns = []
            if current_pattern.pattern_name == SIMPLE_NOTE:
                group.patterns.append(current_pattern)
            
        

    def check_varying_stacks(self, group: PatternGroup, current_pattern: Pattern, previous_pattern: Optional[Pattern]):
        # This should ensure that this group only has n stacks
        if (previous_pattern is None or self.is_n_stack(previous_pattern)) and self.is_n_stack(current_pattern):
            group.patterns.append(current_pattern)
            # Set the start sample initially. Always update the end sample
            if group.start_sample is None:
                group.start_sample = current_pattern.notes[0].sample_time
            group.end_sample = current_pattern.notes[-1].sample_time
            return True
        
        # The current pattern should only be NON-n-stacks from here on out
        if len(group.patterns) >= 2:
            # Sanity check that everything in it is only N-stacks
            for p in group.patterns:
                if self.is_n_stack(p):
                    raise ValueError("There is a non-N-stack note in the varying stack group :(")   

            self.pattern_groups.append(group)
            self.pattern_group_appended = True
            self.pattern_group_appended_name = group.group_name
            group.end_sample = previous_pattern.notes[-1].sample_time
            return True
        else:
            # Insufficient notes to be valid group
            group.patterns = []
            if self.is_n_stack(current_pattern):
                group.patterns.append(current_pattern)



        


    def identify_pattern_groups(self, patterns_list: List[Pattern]) -> List[PatternGroup]:
        
        # TODO: account f or the duration between patterns too.
        added = False
        index_start = 0
        # Lets just first identify Single Notes and Varying Stacks only
    


        for i in range(index_start, len(patterns_list)):
            current_pattern = patterns_list[i]

            # Check for the defined patterns
            for j in range(len(self.groups)):
                group = self.groups[j]
                previous_pattern = group.patterns[-1] if len(group.patterns) > 0 else None

                if group.group_name == SIMPLE_ONLY:
                    added = self.check_simple_notes(group, current_pattern, previous_pattern)
                elif group.group_name == VARYING_STACKS:
                    added = self.check_varying_stacks(group, current_pattern, previous_pattern)

            # Always add to the other_group - incase we go through all patterns, and nothing can be added.
            # This should mean 
            other_group = self.groups[-1]
            other_group.patterns.append(current_pattern)
            if added is False:
                if len(other_group.patterns) > 1:
                    # Reset ALL groups
                    self.pattern_groups.append(other_group)
                    self.reset_groups()
                    print("OTHER???")
                else:
                    raise ValueError("No pattern was 'added'. Less than 2 patterns are in Other which doesnt seem right.")

        return self.pattern_groups


