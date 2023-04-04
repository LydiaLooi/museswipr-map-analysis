from entities import Segment, Note
from map_pattern_analysis import MapPatterns
from constants import *

dummy_note = Note(0, 0)

short_interval = Segment(SHORT_INTERVAL, [dummy_note, dummy_note], 0, 0)
med_interval = Segment(MED_INTERVAL, [dummy_note, dummy_note], 0, 0)
long_interval = Segment(LONG_INTERVAL, [dummy_note, dummy_note], 0, 0)
two = Segment(TWO_STACK, [dummy_note, dummy_note], 0, 0)
three = Segment(THREE_STACK, [dummy_note, dummy_note], 0, 0)
four = Segment(FOUR_STACK, [dummy_note, dummy_note], 0, 0)
switch = Segment(SWITCH, [dummy_note, dummy_note], 0, 0)
zig_zag = Segment(ZIG_ZAG, [dummy_note, dummy_note], 0, 0)
stream = Segment(SINGLE_STREAMS, [dummy_note, dummy_note], 0, 0)

def _Note(lane, seconds):
    return Note(lane, seconds * DEFAULT_SAMPLE_RATE)

def test_one_interval_is_other():
    groups = MapPatterns().identify_patterns([short_interval])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 1

def test_two_intervals_is_slow_stretch():
    groups = MapPatterns().identify_patterns([short_interval, med_interval])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].segments) == 2

def test_with_differing_intervals_only():
    groups = MapPatterns().identify_patterns([
        short_interval,
        short_interval,
        med_interval,
        long_interval,
        short_interval
        ])
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].segments) == 5

def test_varying_stacks_only():
    groups = MapPatterns().identify_patterns([two, three, two])
    assert len(groups) == 1
    assert groups[0].group_name == VARYING_STACKS
    assert len(groups[0].segments) == 3

def test_varying_stacks_with_intervals():
    patterns = [
        short_interval, med_interval,
        three, four,
        short_interval, long_interval, 
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == SLOW_STRETCH
    assert groups[1].group_name == VARYING_STACKS
    assert groups[2].group_name == SLOW_STRETCH
    assert len(groups[0].segments) == 2
    assert len(groups[1].segments) == 4 # Includes med_interval and short_interval on either side
    assert len(groups[2].segments) == 2

def test_other_only_one_pattern():
    groups = MapPatterns().identify_patterns([switch])
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 1

def test_simple_varying_stacks_end_with_other():
    patterns = [
        short_interval, short_interval, 
        two, three, two,
        switch, zig_zag, switch, two, zig_zag, stream]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 3
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].segments) == 2
    assert groups[1].group_name == VARYING_STACKS
    assert len(groups[1].segments) == 4
    assert groups[2].group_name == OTHER
    assert len(groups[2].segments) == 7

def test_other_with_multiple_intervals_in_between():
    patterns = [
        short_interval, switch, med_interval, switch, long_interval
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 5

def test_other_in_between():
    patterns = [
        switch, two, zig_zag,
        two, two, three,
        switch,
        short_interval, short_interval, short_interval,
        switch
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 5
    assert groups[0].group_name	== OTHER
    assert len(groups[0].segments)	== 4
    assert groups[1].group_name == VARYING_STACKS
    assert len(groups[1].segments)	== 3
    assert groups[2].group_name == OTHER
    assert len(groups[2].segments)	== 3
    assert groups[3].group_name == SLOW_STRETCH
    assert len(groups[3].segments)	== 3
    assert groups[4].group_name == OTHER
    assert len(groups[4].segments)	== 2



def test_even_circle():
    patterns = [switch, two, switch, two, switch, two]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].segments) == 6

def test_even_circle_with_intervals_start_and_end():
    patterns = [
        Segment(LONG_INTERVAL, [Note(0, 0), Note(0, 10 * DEFAULT_SAMPLE_RATE)]), 
        Segment(SWITCH, [Note(0, 10 * DEFAULT_SAMPLE_RATE), Note(1, 10.1 * DEFAULT_SAMPLE_RATE)]), 
        Segment(TWO_STACK, [Note(1, 10.1 * DEFAULT_SAMPLE_RATE), Note(1, 10.2 * DEFAULT_SAMPLE_RATE)]),  
        Segment(SWITCH, [Note(1, 10.2 * DEFAULT_SAMPLE_RATE), Note(0, 10.3 * DEFAULT_SAMPLE_RATE)]), 
        Segment(TWO_STACK, [Note(0, 10.3 * DEFAULT_SAMPLE_RATE), Note(0, 10.4 * DEFAULT_SAMPLE_RATE)]), 
        Segment(SWITCH, [Note(0, 10.4 * DEFAULT_SAMPLE_RATE), Note(1, 10.5 * DEFAULT_SAMPLE_RATE)]), 
        Segment(TWO_STACK, [Note(1, 10.5 * DEFAULT_SAMPLE_RATE), Note(1, 10.6 * DEFAULT_SAMPLE_RATE)]), 
        Segment(MED_INTERVAL, [Note(1, 10.6), Note(0, 12.6 * DEFAULT_SAMPLE_RATE)])
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].segments) == 8

def test_invalid_even_circles_pattern():
    patterns = [
        Segment(SWITCH, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(SWITCH, [Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(1, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(MED_INTERVAL, [Note(1, 0.6 * DEFAULT_SAMPLE_RATE), Note(1, 1.2 * DEFAULT_SAMPLE_RATE)], 0)
    ]

    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 4

def test_even_circles_pattern():
    patterns = [
        Segment(TWO_STACK, [Note(0, 21.42 * DEFAULT_SAMPLE_RATE), Note(0, 21.60 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(SWITCH, [Note(0, 21.60 * DEFAULT_SAMPLE_RATE), Note(0, 21.78 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(0, 21.78 * DEFAULT_SAMPLE_RATE), Note(0, 21.96 * DEFAULT_SAMPLE_RATE)], 0)
    ]

    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].segments) == 3


def test_even_circles_have_different_time_diffs_not_even_circles():
    patterns = [
        Segment(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(SWITCH, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.3 * DEFAULT_SAMPLE_RATE)], 0), # Switch is not same time by 0.1s
        Segment(TWO_STACK, [Note(1, 0.3 * DEFAULT_SAMPLE_RATE), Note(1, 0.5 * DEFAULT_SAMPLE_RATE)], 0)
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 3

def test_even_circles_same_time_diff_with_intervals_with_diff_time_diff():
    patterns = [
        Segment(SHORT_INTERVAL, [Note(0, 0), Note(0, 0.5 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(SWITCH, [Note(0, 0.5 * DEFAULT_SAMPLE_RATE), Note(1, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(1, 0.6 * DEFAULT_SAMPLE_RATE), Note(1, 0.7 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(SWITCH, [Note(1, 0.7 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(0, 0.8 * DEFAULT_SAMPLE_RATE), Note(0, 0.9 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(LONG_INTERVAL, [Note(0, 0.9 * DEFAULT_SAMPLE_RATE), Note(1, 5 * DEFAULT_SAMPLE_RATE)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == EVEN_CIRCLES   
    assert len(groups[0].segments) == 6


def test_skewed_circles_with_invalid_zigzag_is_other():
    patterns = [
        Segment(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(ZIG_ZAG, [
            Note(0, 0.2 * DEFAULT_SAMPLE_RATE), 
            Note(1, 0.4 * DEFAULT_SAMPLE_RATE), 
            Note(0, 0.6 * DEFAULT_SAMPLE_RATE), 
            Note(1, 0.8 * DEFAULT_SAMPLE_RATE), 
            Note(0, 1 * DEFAULT_SAMPLE_RATE),
            ], 0),
        Segment(TWO_STACK, [Note(0, 1.2 * DEFAULT_SAMPLE_RATE), Note(0, 1.4 * DEFAULT_SAMPLE_RATE)], 0)
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == OTHER
    assert len(groups[0].segments) == 3

def test_skewed_circles_valid():
    patterns = [
        Segment(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(ZIG_ZAG, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(0, 0.6 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0)
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].segments) == 3

def test_skewed_circles_with_start_end_intervals_valid():
    patterns = [
        Segment(LONG_INTERVAL, [_Note(0, 0), _Note(0, 10)], 0),
        Segment(TWO_STACK, [_Note(0, 10), _Note(0, 10.1)], 0),
        Segment(ZIG_ZAG, [_Note(0, 10.1), _Note(0, 10.2), _Note(0, 10.3)], 0),
        Segment(TWO_STACK, [_Note(0, 10.3), _Note(0, 10.4)], 0),
        Segment(SHORT_INTERVAL, [_Note(0, 10.4), _Note(0, 11)], 0)
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].segments) == 5

def test_skewed_circles_valid_multi_zigs():
    patterns = [
        Segment(TWO_STACK, [Note(0, 0), Note(0, 0.2 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(ZIG_ZAG, [Note(0, 0.2 * DEFAULT_SAMPLE_RATE), Note(1, 0.4 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(TWO_STACK, [Note(0, 0.6 * DEFAULT_SAMPLE_RATE), Note(0, 0.8 * DEFAULT_SAMPLE_RATE)], 0),
        Segment(ZIG_ZAG, [Note(0, 0.8 * DEFAULT_SAMPLE_RATE), Note(1, 1 * DEFAULT_SAMPLE_RATE), Note(0, 0.6 * DEFAULT_SAMPLE_RATE)], 0),
        ]
    groups = MapPatterns().identify_patterns(patterns)
    assert groups[0].group_name == SKEWED_CIRCLES

def test_even_circles_into_nothing_but_theory():
    patterns = [
        Segment(SHORT_INTERVAL, [_Note(0, 0), _Note(0, 0.5)], 0),
        Segment(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Segment(SWITCH, [_Note(0, 0.6), _Note(0, 0.7)], 0),
        Segment(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Segment(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Segment(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
        Segment(LONG_INTERVAL, [_Note(0, 1.5), _Note(0, 10)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == EVEN_CIRCLES
    assert len(groups[0].segments) == 4
    assert groups[1].group_name == NOTHING_BUT_THEORY
    assert len(groups[1].segments) == 5

def test_skewed_circles_into_even_circles():
    patterns = [
        Segment(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.6), _Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(TWO_STACK, [_Note(0, 0.8), _Note(0, 0.9)], 0),
        Segment(SWITCH, [_Note(0, 0.9), _Note(0, 1)], 0),
        Segment(TWO_STACK, [_Note(0, 1), _Note(0, 1.1)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].segments) == 3
    assert groups[1].group_name == EVEN_CIRCLES
    assert len(groups[1].segments) == 3

def test_skewed_circles_into_even_circles_with_interval_sandwich():
    patterns = [
        Segment(SHORT_INTERVAL, [_Note(0, 0), _Note(0, 0.5)], 0),
        Segment(TWO_STACK, [_Note(0, 0.5), _Note(0, 0.6)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.6), _Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(TWO_STACK, [_Note(0, 0.8), _Note(0,0.9)], 0),
        Segment(SWITCH, [_Note(0, 0.9), _Note(0, 1)], 0),
        Segment(TWO_STACK, [_Note(0, 1), _Note(0, 1.1)], 0),
        Segment(LONG_INTERVAL, [_Note(0, 1.1), _Note(0, 10)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 2
    assert groups[0].group_name == SKEWED_CIRCLES
    assert len(groups[0].segments) == 4
    assert groups[1].group_name == EVEN_CIRCLES
    assert len(groups[1].segments) == 4

def test_nothing_but_theory_valid():
    patterns = [
        Segment(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Segment(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Segment(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == NOTHING_BUT_THEORY
    assert len(groups[0].segments) == 4


def test_nothing_but_theory_valid_other_stacks():
    patterns = [
        Segment(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Segment(THREE_STACK, [_Note(0, 1.1), _Note(0, 1.2), _Note(0, 1.3)], 0),
        Segment(ZIG_ZAG, [_Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5), _Note(0, 1.6)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == NOTHING_BUT_THEORY
    assert len(groups[0].segments) == 4

def test_nothing_but_theory_with_start_end_interval_valid():
    patterns = [
        Segment(SHORT_INTERVAL, [_Note(0, 0.0), _Note(0, 0.7)], 0),
        Segment(TWO_STACK, [_Note(0, 0.7), _Note(0, 0.8)], 0),
        Segment(ZIG_ZAG, [_Note(0, 0.8), _Note(0, 0.9), _Note(0, 1), _Note(0, 1.1)], 0),
        Segment(TWO_STACK, [_Note(0, 1.1), _Note(0, 1.2)], 0),
        Segment(ZIG_ZAG, [_Note(0, 1.2), _Note(0, 1.3), _Note(0, 1.4), _Note(0, 1.5)], 0),
        Segment(LONG_INTERVAL, [_Note(0, 1.5), _Note(0, 20)], 0),
    ]
    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == NOTHING_BUT_THEORY
    assert len(groups[0].segments) == 6


def test_slow_stretch_with_varying_intervals():
    # Taken from Eyes half closed 128.11s
    patterns = [
        Segment(SHORT_INTERVAL, [Note(0, 5669300), Note(0, 5679100)], 0),
        Segment(SHORT_INTERVAL, [Note(0, 5688900), Note(0, 5695433), Note(0, 5701966)], 0),
        Segment(SHORT_INTERVAL, [Note(0, 5708500), Note(0, 5715033)], 0),
        Segment(SHORT_INTERVAL, [Note(0, 5721566), Note(0, 5728100), Note(0, 5747700)], 0),
        Segment(SHORT_INTERVAL, [Note(0, 5757500), Note(0, 5767300)], 0)
    ]

    groups = MapPatterns().identify_patterns(patterns)
    assert len(groups) == 1
    assert groups[0].group_name == SLOW_STRETCH
    assert len(groups[0].segments) == 5