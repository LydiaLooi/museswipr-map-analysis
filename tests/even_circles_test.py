from pattern_analysis import EvenCirclesGroup, Pattern
from constants import EVEN_CIRCLES, TWO_STACK, THREE_STACK, FOUR_STACK, SWITCH, ZIG_ZAG, TIME_CONVERSION


def test_valid_current_four_stack_when_first():
    current_pattern = Pattern(FOUR_STACK, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_current_switch_when_first():
    current_pattern = Pattern(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_first():
    current_pattern = Pattern(ZIG_ZAG, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_valid_current_switch_when_two_stack_previous():
    current_pattern = Pattern(SWITCH, [], 0, 0)
    previous_pattern = Pattern(TWO_STACK, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_current_three_stack_when_switch_previous():
    current_pattern = Pattern(THREE_STACK, [], 0, 0)
    previous_pattern = Pattern(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_valid_previous():
    current_pattern = Pattern(ZIG_ZAG, [], 0, 0)
    previous_pattern = Pattern(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False


def test_valid_current_pattern_with_different_time_difference_not_added():
    current_pattern = Pattern(THREE_STACK, [], 0, 1.1 * TIME_CONVERSION)
    previous_pattern = Pattern(SWITCH, [], 0, 1 * TIME_CONVERSION)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False