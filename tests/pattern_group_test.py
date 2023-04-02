from entities import Pattern, Note
from pattern_analysis import MapPatternGroups
from constants import *

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

def test_one_interval_is_other():
    groups = MapPatternGroups().identify_pattern_groups([short_interval])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_two_intervals_is_slow_stretch():
    groups = MapPatternGroups().identify_pattern_groups([short_interval, med_interval])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH

def test_with_differing_intervals_only():
    groups = MapPatternGroups().identify_pattern_groups([
        short_interval,
        short_interval,
        med_interval,
        long_interval,
        short_interval
        ])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH

def test_varying_stacks_only():
    groups = MapPatternGroups().identify_pattern_groups([two, three])
    assert len(groups) == 1
    assert groups[0].group_name == VARYING_STACKS

def test_varying_stacks_with_intervals():
    patterns = [
        short_interval, med_interval,
        three, four, 
        short_interval, long_interval, 
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    # assert groups[0].group_name == VARYING_STACKS
    assert groups[0].group_name == SLOW_STRETCH
    assert groups[1].patterns == VARYING_STACKS
    assert groups[2].group_name == SLOW_STRETCH
    # assert groups[4].group_name == VARYING_STACKS

def test_other_only_one_pattern():
    groups = MapPatternGroups().identify_pattern_groups([switch])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_simple_varying_stacks_end_with_other():
    patterns = [
        short_interval, short_interval, 
        two, three, two,
        switch, zig_zag, switch, two, zig_zag, stream]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 3
    assert groups[0].group_name == SLOW_STRETCH
    assert groups[1].group_name == VARYING_STACKS
    assert groups[2].group_name == OTHER

def test_other_with_multiple_intervals():
    patterns = [
        short_interval, switch, med_interval, switch, long_interval
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER

def test_other_in_between():
    patterns = [
        switch, two, zig_zag,
        two, two,
        switch,
        short_interval, short_interval, short_interval,
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

def test_even_circle_with_intervals_start_and_end():
    patterns = [
        Pattern(LONG_INTERVAL, [Note(0, 0), Note(0, 10 * TIME_CONVERSION)]), 
        Pattern(SWITCH, [Note(0, 10 * TIME_CONVERSION), Note(1, 10.1 * TIME_CONVERSION)]), 
        Pattern(TWO_STACK, [Note(1, 10.1 * TIME_CONVERSION), Note(1, 10.2 * TIME_CONVERSION)]),  
        Pattern(SWITCH, [Note(1, 10.2 * TIME_CONVERSION), Note(0, 10.3 * TIME_CONVERSION)]), 
        Pattern(TWO_STACK, [Note(0, 10.3 * TIME_CONVERSION), Note(0, 10.4 * TIME_CONVERSION)]), 
        Pattern(SWITCH, [Note(0, 10.4 * TIME_CONVERSION), Note(1, 10.5 * TIME_CONVERSION)]), 
        Pattern(TWO_STACK, [Note(1, 10.5 * TIME_CONVERSION), Note(1, 10.6 * TIME_CONVERSION)]), 
        Pattern(MED_INTERVAL, [Note(1, 10.6), Note(0, 12.6 * TIME_CONVERSION)])
        ]
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

def test_even_circles_have_same_time_diff_true():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.4 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(1, 0.4 * TIME_CONVERSION), Note(1, 0.6 * TIME_CONVERSION)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES

def test_even_circles_have_different_time_diffs_not_even_circles():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 0.2 * TIME_CONVERSION), Note(1, 0.3 * TIME_CONVERSION)], 0), # Switch is not same time by 0.1s
        Pattern(TWO_STACK, [Note(1, 0.3 * TIME_CONVERSION), Note(1, 0.5 * TIME_CONVERSION)], 0)
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name != EVEN_CIRCLES

def test_even_circles_same_time_diff_with_intervals_with_diff_time_diff():
    patterns = [
        Pattern(SHORT_INTERVAL, [Note(0, 0), Note(0, 0.5 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(0, 0.5 * TIME_CONVERSION), Note(1, 0.6 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(1, 0.6 * TIME_CONVERSION), Note(1, 0.7 * TIME_CONVERSION)], 0),
        Pattern(SWITCH, [Note(1, 0.7 * TIME_CONVERSION), Note(0, 0.8 * TIME_CONVERSION)], 0),
        Pattern(TWO_STACK, [Note(0, 0.8 * TIME_CONVERSION), Note(0, 0.9 * TIME_CONVERSION)], 0),
        Pattern(LONG_INTERVAL, [Note(0, 0.9 * TIME_CONVERSION), Note(1, 5 * TIME_CONVERSION)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == EVEN_CIRCLES   


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

def test_even_circles_into_nothing_but_theory():
    patterns = [
        Pattern(SHORT_INTERVAL, [_Note(0, 0), _Note(0, 0.5)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Pattern(SWITCH, [_Note(0, 0.6), _Note(0, 0.7)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Pattern(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
        Pattern(LONG_INTERVAL, [_Note(0, 1.5), _Note(0, 10)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == EVEN_CIRCLES
    assert groups[1].group_name == NOTHING_BUT_THEORY