from config import get_config

conf = get_config()

DEFAULT_SAMPLE_RATE = 44100  # time_s * TIME_CONVERSION = sample_time

SWITCH = "Switch"
ZIG_ZAG = "Zig Zag"
TWO_STACK = "2-Stack"
THREE_STACK = "3-Stack"
FOUR_STACK = "4-Stack"
SINGLE_STREAMS = "Single Streams"

SHORT_INTERVAL = "Short Interval"
MED_INTERVAL = "Medium Interval"
LONG_INTERVAL = "Long Interval"

SLOW_STRETCH = "Slow Stretch"
EVEN_CIRCLES = "Even Circles"
SKEWED_CIRCLES = "Skewed Circles"
VARYING_STACKS = "Varying Stacks"
NOTHING_BUT_THEORY = "Nothing But Theory"
VARIABLE_STREAM = "Variable Stream"
OTHER = "Other"

TOLERANCE = conf["pattern_tolerance_ms"] * DEFAULT_SAMPLE_RATE // 1000
