from musemapalyzr.constants import EVEN_CIRCLES, OTHER
from musemapalyzr.entities import Segment
from musemapalyzr.map_pattern_analysis import MapPatterns
from patterns.even_circles import EvenCirclesGroup
from patterns.other import OtherPattern


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


def test_does_not_merge_with_patterns_between():
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
    assert len(results[1].segments) == 3  # C, D, E
    assert len(results[2].segments) == 3  # E, F, G
