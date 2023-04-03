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
    return Note(lane, seconds * DEFAULT_SAMPLE_RATE)

def test_one_interval_is_other():
    groups = MapPatternGroups().identify_pattern_groups([short_interval])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 1

def test_two_intervals_is_slow_stretch():
    groups = MapPatternGroups().identify_pattern_groups([short_interval, med_interval])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].patterns) == 2

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
    assert len(groups[0].patterns) == 5

def test_varying_stacks_only():
    groups = MapPatternGroups().identify_pattern_groups([two, three, two])
    assert len(groups) == 1
    assert groups[0].group_name == VARYING_STACKS
    assert len(groups[0].patterns) == 3

def test_varying_stacks_with_intervals():
    patterns = [
        short_interval, med_interval,
        three, four,
        short_interval, long_interval, 
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == SLOW_STRETCH
    assert groups[1].group_name == VARYING_STACKS
    assert groups[2].group_name == SLOW_STRETCH
    assert len(groups[0].patterns) == 2
    assert len(groups[1].patterns) == 4 # Includes med_interval and short_interval on either side
    assert len(groups[2].patterns) == 2

def test_other_only_one_pattern():
    groups = MapPatternGroups().identify_pattern_groups([switch])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 1

def test_simple_varying_stacks_end_with_other():
    patterns = [
        short_interval, short_interval, 
        two, three, two,
        switch, zig_zag, switch, two, zig_zag, stream]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 3
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].patterns) == 2
    assert groups[1].group_name == VARYING_STACKS
    assert len(groups[1].patterns) == 4
    assert groups[2].group_name == OTHER
    assert len(groups[2].patterns) == 7

def test_other_with_multiple_intervals_in_between():
    patterns = [
        short_interval, switch, med_interval, switch, long_interval
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 5

def test_other_in_between():
    patterns = [
        switch, two, zig_zag,
        two, two, three,
        switch,
        short_interval, short_interval, short_interval,
        switch
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 5
    assert groups[0].group_name	== OTHER
    assert len(groups[0].patterns)	== 4
    assert groups[1].group_name == VARYING_STACKS
    assert len(groups[1].patterns)	== 3
    assert groups[2].group_name == OTHER
    assert len(groups[2].patterns)	== 3
    assert groups[3].group_name == SLOW_STRETCH
    assert len(groups[3].patterns)	== 3
    assert groups[4].group_name == OTHER
    assert len(groups[4].patterns)	== 2



def test_even_circle():
    patterns = [switch, two, switch, two, switch, two]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].patterns) == 6

def test_even_circle_with_intervals_start_and_end():
    patterns = [
        Pattern(LONG_INTERVAL, [Note(0, 0), Note(0, 10 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(SWITCH, [Note(0, 10 * DEFAULT_SAMPLE_RATE), Note(1, 10.1 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(TWO_STACK, [Note(1, 10.1 * DEFAULT_SAMPLE_RATE), Note(1, 10.2 * DEFAULT_SAMPLE_RATE)]),  
        Pattern(SWITCH, [Note(1, 10.2 * DEFAULT_SAMPLE_RATE), Note(0, 10.3 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(TWO_STACK, [Note(0, 10.3 * DEFAULT_SAMPLE_RATE), Note(0, 10.4 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(SWITCH, [Note(0, 10.4 * DEFAULT_SAMPLE_RATE), Note(1, 10.5 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(TWO_STACK, [Note(1, 10.5 * DEFAULT_SAMPLE_RATE), Note(1, 10.6 * DEFAULT_SAMPLE_RATE)]), 
        Pattern(MED_INTERVAL, [Note(1, 10.6), Note(0, 12.6 * DEFAULT_SAMPLE_RATE)])
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].patterns) == 8

def test_invalid_even_circles_pattern():
    patterns = [
        Pattern(SWITCH, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(SWITCH, [Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(1, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(MED_INTERVAL, [Note(1, 0.6 * DEFAULT_SAMPLE_RATE), Note(1, 1.2 * DEFAULT_SAMPLE_RATE)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 4

def test_even_circles_pattern():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 21.42 * DEFAULT_SAMPLE_RATE), Note(0, 21.60 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(SWITCH, [Note(0, 21.60 * DEFAULT_SAMPLE_RATE), Note(0, 21.78 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(0, 21.78 * DEFAULT_SAMPLE_RATE), Note(0, 21.96 * DEFAULT_SAMPLE_RATE)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].patterns) == 3


def test_even_circles_have_different_time_diffs_not_even_circles():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(SWITCH, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.3 * DEFAULT_SAMPLE_RATE)], 0), # Switch is not same time by 0.1s
        Pattern(TWO_STACK, [Note(1, 0.3 * DEFAULT_SAMPLE_RATE), Note(1, 0.5 * DEFAULT_SAMPLE_RATE)], 0)
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 3

def test_even_circles_same_time_diff_with_intervals_with_diff_time_diff():
    patterns = [
        Pattern(SHORT_INTERVAL, [Note(0, 0), Note(0, 0.5 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(SWITCH, [Note(0, 0.5 * DEFAULT_SAMPLE_RATE), Note(1, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(1, 0.6 * DEFAULT_SAMPLE_RATE), Note(1, 0.7 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(SWITCH, [Note(1, 0.7 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(0, 0.8 * DEFAULT_SAMPLE_RATE), Note(0, 0.9 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(LONG_INTERVAL, [Note(0, 0.9 * DEFAULT_SAMPLE_RATE), Note(1, 5 * DEFAULT_SAMPLE_RATE)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == EVEN_CIRCLES   
    assert len(groups[0].patterns) == 6


def test_skewed_circles_with_invalid_zigzag_is_other():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(ZIG_ZAG, [
            Note(0, 0.2 * DEFAULT_SAMPLE_RATE), 
            Note(1, 0.4 * DEFAULT_SAMPLE_RATE), 
            Note(0, 0.6 * DEFAULT_SAMPLE_RATE), 
            Note(1, 0.8 * DEFAULT_SAMPLE_RATE), 
            Note(0, 1 * DEFAULT_SAMPLE_RATE),
            ], 0),
        Pattern(TWO_STACK, [Note(0, 1.2 * DEFAULT_SAMPLE_RATE), Note(0, 1.4 * DEFAULT_SAMPLE_RATE)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == OTHER
    assert len(groups[0].patterns) == 3

def test_skewed_circles_valid():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(0, 0.6 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].patterns) == 3

def test_skewed_circles_with_start_end_intervals_valid():
    patterns = [
        Pattern(LONG_INTERVAL, [_Note(0, 0), _Note(0, 10)], 0),
        Pattern(TWO_STACK, [_Note(0, 10), _Note(0, 10.1)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 10.1), _Note(0, 10.2), _Note(0, 10.3)], 0),
        Pattern(TWO_STACK, [_Note(0, 10.3), _Note(0, 10.4)], 0),
        Pattern(SHORT_INTERVAL, [_Note(0, 10.4), _Note(0, 11)], 0)
        ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].patterns) == 5

def test_skewed_circles_valid_multi_zigs():
    patterns = [
        Pattern(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(TWO_STACK, [Note(0, 0.6 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0),
        Pattern(ZIG_ZAG, [Note(0, 0.8 * DEFAULT_SAMPLE_RATE), Note(1, 1 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
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
    assert len(groups[0].patterns) == 4
    assert groups[1].group_name == NOTHING_BUT_THEORY
    assert len(groups[1].patterns) == 5

def test_skewed_circles_into_even_circles():
    patterns = [
        Pattern(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 0.6), _Note(0, 0.7), _Note(0, 0.8)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.8), _Note(0, 0.9)], 0),
        Pattern(SWITCH, [_Note(0, 0.9), _Note(0, 1)], 0),
        Pattern(TWO_STACK, [_Note(0, 1), _Note(0, 1.1)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].patterns) == 3
    assert groups[1].group_name == EVEN_CIRCLES
    assert len(groups[1].patterns) == 3

def test_skewed_circles_into_even_circles_with_interval_sandwich():
    patterns = [
        Pattern(SHORT_INTERVAL, [_Note(0, 0), _Note(0, 0.5)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 0.6), _Note(0, 0.7), _Note(0, 0.8)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.8), _Note(0,0.9)], 0),
        Pattern(SWITCH, [_Note(0, 0.9), _Note(0, 1)], 0),
        Pattern(TWO_STACK, [_Note(0, 1), _Note(0, 1.1)], 0),
        Pattern(LONG_INTERVAL, [_Note(0, 1.1), _Note(0, 10)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].patterns) == 4
    assert groups[1].group_name == EVEN_CIRCLES
    assert len(groups[1].patterns) == 4

def test_nothing_but_theory_valid():
    patterns = [
        Pattern(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Pattern(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == NOTHING_BUT_THEORY
    assert len(groups[0].patterns) == 4

def test_nothing_but_theory_with_start_end_interval_valid():
    patterns = [
        Pattern(SHORT_INTERVAL, [_Note(0, 0.0), _Note(0, 0.7)], 0),
        Pattern(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Pattern(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Pattern(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
        Pattern(LONG_INTERVAL, [_Note(0, 1.5), _Note(0, 20)], 0),
    ]
    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == NOTHING_BUT_THEORY
    assert len(groups[0].patterns) == 6


def test_slow_stretch_with_varying_intervals():
    # Taken from Eyes half closed 128.11s
    patterns = [
        Pattern(SHORT_INTERVAL, [Note(0, 5669300), Note(0, 5679100)], 0),
        Pattern(SHORT_INTERVAL, [Note(0, 5688900), Note(0, 5695433), Note(0, 5701966)], 0),
        Pattern(SHORT_INTERVAL, [Note(0, 5708500), Note(0, 5715033)], 0),
        Pattern(SHORT_INTERVAL, [Note(0, 5721566), Note(0, 5728100), Note(0, 5747700)], 0),
        Pattern(SHORT_INTERVAL, [Note(0, 5757500), Note(0, 5767300)], 0)
    ]

    groups = MapPatternGroups().identify_pattern_groups(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].patterns) == 5