from pattern_analysis import VaryingStacksGroup, Note, Pattern
from constants import VARYING_STACKS, TWO_STACK, THREE_STACK, FOUR_STACK, SWITCH, ZIG_ZAG, DEFAULT_SAMPLE_RATE, SINGLE_STREAMS, SHORT_INTERVAL, MED_INTERVAL, LONG_INTERVAL


valid_note1 = Note(0, 0)
valid_note2 = Note(0, 0.1 * DEFAULT_SAMPLE_RATE)
valid_note3 = Note(0, 0.2 * DEFAULT_SAMPLE_RATE)
valid_note4 = Note(0, 0.3 * DEFAULT_SAMPLE_RATE) 
valid_note5 = Note(0, 0.4 * DEFAULT_SAMPLE_RATE) 
valid_note6 = Note(0, 0.5 * DEFAULT_SAMPLE_RATE) 
valid_note7 = Note(0, 0.6 * DEFAULT_SAMPLE_RATE) 
valid_note8 = Note(0, 0.7 * DEFAULT_SAMPLE_RATE) 



def test_valid_current_two_stack_when_first():
    current_pattern = Pattern(TWO_STACK, [], 0, 0)

    group = VaryingStacksGroup(VARYING_STACKS, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_interval_when_first():
    current_pattern = Pattern(SHORT_INTERVAL, [], 0, 0)

    group = VaryingStacksGroup(VARYING_STACKS, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_stack_when_interval_previous():
    previous_pattern = Pattern(SHORT_INTERVAL, [], 0, 0)
    current_pattern = Pattern(TWO_STACK, [], 0, 0)

    group = VaryingStacksGroup(VARYING_STACKS, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_stack_when_stack_previous():
    previous_pattern = Pattern(TWO_STACK, [], 0, 0)
    current_pattern = Pattern(FOUR_STACK, [], 0, 0)

    group = VaryingStacksGroup(VARYING_STACKS, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added


def test_valid_stack_when_ends_with_interval_returns_False_but_adds():
    current_pattern = Pattern(LONG_INTERVAL, [], 0, 0)

    patterns = [
        Pattern(SHORT_INTERVAL, [], 0, 0),
        Pattern(TWO_STACK, [], 0, 0),
        Pattern(THREE_STACK, [], 0, 0)
    ]

    group = VaryingStacksGroup(VARYING_STACKS, patterns)
    added = group.check_pattern(current_pattern)
    assert added is False
    assert group.patterns[-1].pattern_name == LONG_INTERVAL

