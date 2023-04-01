from entities import Pattern
from pattern_analysis import MapPatternGroups

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

simple = Pattern(SIMPLE_NOTE, [], 0)
two = Pattern(TWO_STACK, [], 0)
three = Pattern(THREE_STACK, [], 0)
four = Pattern(FOUR_STACK, [], 0)
switch = Pattern(SWITCH, [], 0)
zig_zag = Pattern(ZIG_ZAG, [], 0)
stream = Pattern(SINGLE_STREAMS, [], 0)

def test_simple_only():
    groups = MapPatternGroups().identify_pattern_groups([simple])
    assert len(groups) == 1
    assert groups[0].group_name == SIMPLE_ONLY

def test_varying_stacks_only():
    groups = MapPatternGroups().identify_pattern_groups([two, three])
    assert len(groups) == 1
    assert groups[0].group_name == VARYING_STACKS

def test_varying_stacks_and_simple():
    patterns = [
        two, three, 
        simple, 
        three, four, 
        simple, simple, 
        two, four, two, two]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 5



def test_other_only_one_pattern():
    groups = MapPatternGroups().identify_pattern_groups([switch])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_simple_varying_stacks_end_with_other():
    patterns = [
        simple, simple, 
        two, three, 
        switch, zig_zag, switch, two, zig_zag, stream]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 3
    assert groups[0].group_name == SIMPLE_ONLY
    assert groups[1].group_name == VARYING_STACKS
    assert groups[2].group_name == OTHER

def test_other_with_two_stacks_between():
    patterns = [switch, two, switch, two, switch, two]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_other_in_between():
    patterns = [
        switch, two, zig_zag,
        two, two,
        switch,
        simple, simple, simple,
        switch
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 5
    assert groups[2].group_name == OTHER