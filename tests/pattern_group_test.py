from entities import Pattern, Note
from pattern_analysis import MapPatternGroups
from constants import *

dummy_note = Note(0, 0)

simple = Pattern(SHORT_INTERVAL, [dummy_note, dummy_note], 0, 0)
two = Pattern(TWO_STACK, [dummy_note, dummy_note], 0, 0)
three = Pattern(THREE_STACK, [dummy_note, dummy_note], 0, 0)
four = Pattern(FOUR_STACK, [dummy_note, dummy_note], 0, 0)
switch = Pattern(SWITCH, [dummy_note, dummy_note], 0, 0)
zig_zag = Pattern(ZIG_ZAG, [dummy_note, dummy_note], 0, 0)
stream = Pattern(SINGLE_STREAMS, [dummy_note, dummy_note], 0, 0)

def test_simple_only():
    groups = MapPatternGroups().identify_pattern_groups([simple])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH

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
    assert groups[0].group_name == VARYING_STACKS
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
    assert groups[0].group_name == SLOW_STRETCH
    assert groups[1].group_name == VARYING_STACKS
    assert groups[2].group_name == OTHER

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


def test_even_circle():
    patterns = [switch, two, switch, two, switch, two]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES

def test_invalid_even_circles_pattern():
    patterns = [
        Pattern(SWITCH, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.4 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(1, 0.4 * TIME_CONVERSION), Note(1, 0.6 * TIME_CONVERSION)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_even_circles_pattern():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 21.42 * TIME_CONVERSION), Note(0, 21.60 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 21.60 * TIME_CONVERSION), Note(0, 21.78 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(0, 21.78 * TIME_CONVERSION), Note(0, 21.96 * TIME_CONVERSION)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES

def test_even_circles_have_same_intervals_true():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.4 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(1, 0.4 * TIME_CONVERSION), Note(1, 0.6 * TIME_CONVERSION)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES

def test_even_circles_have_different_intervals_not_even_circles():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.3 * TIME_CONVERSION)], 0), # Switch is not same time by 0.1s
        Pattern(TWO_STACK, [Note(1, 0.3 * TIME_CONVERSION), Note(1, 0.5 * TIME_CONVERSION)], 0)
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name != EVEN_CIRCLES


def test_skewed_circles_invalid_is_other():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(ZIG_ZAG, [
            Note(0, 0.2 * TIME_CONVERSION), 
            Note(1, 0.4 * TIME_CONVERSION), 
            Note(0, 0.6 * TIME_CONVERSION), 
            Note(1, 0.8 * TIME_CONVERSION), 
            Note(0, 1 * TIME_CONVERSION),
            ], 0),
        Pattern(TWO_STACK, [Note(0, 1.2 * TIME_CONVERSION), Note(0, 1.4 * TIME_CONVERSION)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name != SKEWED_CIRCLES

def test_skewed_circles_valid():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.4 * TIME_CONVERSION), Note(0, 0.6 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(0, 0.6 * TIME_CONVERSION), Note(0, 0.8 * TIME_CONVERSION)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES


def test_skewed_circles_valid_multi_zigs():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.4 * TIME_CONVERSION), Note(0, 0.6 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(0, 0.6 * TIME_CONVERSION), Note(0, 0.8 * TIME_CONVERSION)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.8 * TIME_CONVERSION), Note(1, 1 * TIME_CONVERSION), Note(0, 0.6 * TIME_CONVERSION)], 0),
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES