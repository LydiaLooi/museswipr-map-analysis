from typing import List, Optional

from constants import *
from entities import Note, Pattern

from pattern_groups import PatternGroup, EvenCirclesGroup, SkewedCirclesGroup, VaryingStacksGroup, NothingButTheoryGroup, SlowStretch, OtherGroup


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
        return pattern.pattern_name in (TWO_STACK, THREE_STACK, FOUR_STACK)
    
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
                            other_group = OtherGroup(OTHER, self.other_group.patterns[:-len(group.patterns)])
                            self.pattern_groups.append(other_group)

                        added = True
                        group_copy = group.__class__(group.group_name, group.patterns, group.start_sample, group.end_sample)
                        self.pattern_groups.append(group_copy)
                        # Reset all groups with current pattern.
                        for group in self.groups:
                            group.reset_group(previous_pattern, current_pattern)
                        self.other_group.reset_group(previous_pattern, current_pattern) # reset OtherGroup
                        reset = True
                        break # STOP LOOKING !! WE FOUND SOMETHING
            if not reset:
                self.other_group.check_pattern(current_pattern)

            # We have gone through all the defined groups...
            if not added: 
                # Append OtherGroup if no other groups were appendale
                self.pattern_groups.append(OtherGroup(OTHER, self.other_group.patterns, self.other_group.start_sample, self.other_group.end_sample))
                self.other_group.reset_group(previous_pattern, current_pattern) # reset OtherGroup
                # Reset all groups with current pattern.
                for group in self.groups:
                    group.reset_group(previous_pattern, current_pattern)

        # Do last check
        for last_check_group in self.groups:
            if last_check_group.is_appendable():
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