from musemapalyzr.constants import EVEN_CIRCLES, OTHER, SLOW_STRETCH
from musemapalyzr.entities import Segment
from musemapalyzr.map_pattern_analysis import MapPatterns
from patterns.even_circles import EvenCirclesGroup
from patterns.other import OtherPattern
from patterns.slow_stretch import SlowStretchPattern


def test_merges_others_together():
    mp = MapPatterns()

    # B, C overlapped. C, D overlapped.
    o2 = OtherPattern(OTHER, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o3 = OtherPattern(OTHER, [Segment("C", []), Segment("D", []), Segment("E", [])])
    o1 = OtherPattern(OTHER, [Segment("A", []), Segment("B", []), Segment("C", [])])
    mp.patterns = [o1, o2, o3]
    results = mp._return_final_patterns()
    assert len(results) == 1
    assert results[0].pattern_name == OTHER
    assert len(results[0].segments) == 5


def test_does_not_merge_with_patterns_between():
    mp = MapPatterns()

    # B, C overlapped. C, D overlapped.
    o1 = OtherPattern(OTHER, [Segment("A", []), Segment("B", []), Segment("C", [])])
    o2 = EvenCirclesGroup(EVEN_CIRCLES, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o3 = OtherPattern(OTHER, [Segment("C", []), Segment("D", []), Segment("E", [])])
    mp.patterns = [o1, o2, o3]
    results = mp._return_final_patterns()
    assert len(results) == 3
    assert results[0].pattern_name == OTHER
    assert results[1].pattern_name == EVEN_CIRCLES
    assert results[2].pattern_name == OTHER
    assert len(results[0].segments) == 2  # A, B
    assert len(results[1].segments) == 3  # B, C, D
    assert len(results[2].segments) == 3  # C, D, E
    assert results[2].segments[0].segment_name == "C"
    assert results[2].segments[1].segment_name == "D"
    assert results[2].segments[2].segment_name == "E"


def test_merges_with_patterns_either_side():
    mp = MapPatterns()

    # B, C overlapped. C, D overlapped. E overlapped.
    o1 = EvenCirclesGroup(EVEN_CIRCLES, [Segment("A", []), Segment("B", []), Segment("C", [])])
    o2 = OtherPattern(OTHER, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o3 = OtherPattern(OTHER, [Segment("C", []), Segment("D", []), Segment("E", [])])
    o4 = EvenCirclesGroup(EVEN_CIRCLES, [Segment("E", []), Segment("F", []), Segment("G", [])])
    mp.patterns = [o1, o2, o3, o4]
    results = mp._return_final_patterns()
    assert len(results) == 3
    assert results[0].pattern_name == EVEN_CIRCLES
    assert results[1].pattern_name == OTHER
    assert results[2].pattern_name == EVEN_CIRCLES
    assert len(results[0].segments) == 3  # A, B, C
    assert len(results[1].segments) == 3  # B, C, D
    assert results[1].segments[0].segment_name == "B"
    assert results[1].segments[1].segment_name == "C"
    assert results[1].segments[2].segment_name == "D"
    assert len(results[2].segments) == 3  # E, F, G


def test_merges_slow_stretches():
    mp = MapPatterns()

    o1 = SlowStretchPattern(SLOW_STRETCH, [Segment("A", []), Segment("B", [])])
    o2 = SlowStretchPattern(SLOW_STRETCH, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o3 = SlowStretchPattern(SLOW_STRETCH, [Segment("D", []), Segment("E", [])])
    mp.patterns = [o1, o2, o3]
    results = mp._return_final_patterns()
    assert len(results) == 1
    assert results[0].pattern_name == SLOW_STRETCH
    assert len(results[0].segments) == 5  # A, B, C, D, E


def test_merges_slow_stretches_and_others():
    mp = MapPatterns()

    o1 = SlowStretchPattern(SLOW_STRETCH, [Segment("A", []), Segment("B", [])])
    o2 = SlowStretchPattern(SLOW_STRETCH, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o3 = OtherPattern(OTHER, [Segment("D", []), Segment("E", []), Segment("F", [])])
    o4 = OtherPattern(OTHER, [Segment("E", []), Segment("F", []), Segment("G", [])])
    mp.patterns = [o1, o2, o3, o4]
    results = mp._return_final_patterns()
    assert len(results) == 2
    assert results[0].pattern_name == SLOW_STRETCH
    assert len(results[0].segments) == 4  # A, B, C, D
    assert results[1].pattern_name == OTHER
    assert results[1].segments[0].segment_name == "D"
    assert results[1].segments[-1].segment_name == "G"


def test_merges_slow_stretches_and_ignores_others_with_1_segment_only():
    # Weird race condition. See we luv lama for a real example of 1 Other between slow stretches
    mp = MapPatterns()

    o1 = SlowStretchPattern(SLOW_STRETCH, [Segment("A", []), Segment("B", [])])
    o2 = OtherPattern(OTHER, [Segment("B", [])])
    o3 = SlowStretchPattern(SLOW_STRETCH, [Segment("B", []), Segment("C", []), Segment("D", [])])
    o4 = OtherPattern(OTHER, [Segment("D", [])])
    o5 = SlowStretchPattern(SLOW_STRETCH, [Segment("D", []), Segment("E", []), Segment("F", [])])

    mp.patterns = [o1, o2, o3, o4, o5]
    results = mp._return_final_patterns()
    assert len(results) == 1
    assert results[0].pattern_name == SLOW_STRETCH
    assert len(results[0].segments) == 6  # A, B, C, D, E, F


def test_merges_slow_stretches_with_many_patterns():
    mp = MapPatterns()

    o0 = EvenCirclesGroup(EVEN_CIRCLES, [Segment("A", []), Segment("B", []), Segment("C", [])])

    o1 = SlowStretchPattern(SLOW_STRETCH, [Segment("C", []), Segment("D", [])])
    o2 = SlowStretchPattern(SLOW_STRETCH, [Segment("D", []), Segment("E", []), Segment("F", [])])
    o3 = SlowStretchPattern(SLOW_STRETCH, [Segment("F", []), Segment("G", [])])

    o4 = OtherPattern(OTHER, [Segment("G", []), Segment("H", []), Segment("I", [])])
    o5 = OtherPattern(OTHER, [Segment("H", []), Segment("I", []), Segment("J", [])])

    o6 = EvenCirclesGroup(EVEN_CIRCLES, [Segment("J", []), Segment("K", []), Segment("L", [])])

    o7 = SlowStretchPattern(SLOW_STRETCH, [Segment("L", []), Segment("M", [])])
    o8 = SlowStretchPattern(SLOW_STRETCH, [Segment("M", []), Segment("N", [])])

    mp.patterns = [o0, o1, o2, o3, o4, o5, o6, o7, o8]

    results = mp._return_final_patterns()

    assert len(results) == 5
    assert results[0].pattern_name == EVEN_CIRCLES
    assert results[1].pattern_name == SLOW_STRETCH
    assert results[2].pattern_name == OTHER
    assert results[3].pattern_name == EVEN_CIRCLES
    assert results[4].pattern_name == SLOW_STRETCH

    assert len(results[1].segments) == 5  # C, D, E, F, G
    assert len(results[2].segments) == 3  # G, H, I
    assert len(results[4].segments) == 3  # L, M, N
