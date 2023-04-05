from abc import ABC, abstractmethod
from typing import Optional

from entities import Segment
from patterns.pattern import Pattern

ERROR_MSG = "You should replace this with a concrete strategy"


class CheckSegmentStrategy(ABC):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    @abstractmethod
    def check_segment(self, current_segment: Segment) -> Optional[bool]:
        raise NotImplementedError(ERROR_MSG)


class IsAppendableStrategy(ABC):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    @abstractmethod
    def is_appendable(self) -> bool:
        raise NotImplementedError(ERROR_MSG)


class CalcVariationScoreStrategy(ABC):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    @abstractmethod
    def calc_variation_score(self) -> float:
        raise NotImplementedError(ERROR_MSG)


class CalcPatternMultiplierStrategy(ABC):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    @abstractmethod
    def calc_pattern_multiplier(self) -> float:
        raise NotImplementedError(ERROR_MSG)


class CalcPatternLengthMultiplierStrategy(ABC):
    def __init__(self, pattern: Pattern):
        self.pattern = pattern

    @abstractmethod
    def calc_pattern_length_multiplier(self) -> float:
        raise NotImplementedError(ERROR_MSG)
