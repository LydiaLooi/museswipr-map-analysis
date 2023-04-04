from entities import (
    Note,
    MuseSwiprMap,
    Segment,
)

from map_pattern_analysis import (
    MapPatterns,
)
import os
from constants import *
from difficulty_calculation import (
    analyse_segments,
    print_segments,
    calculate_difficulty,
)

import sys

# set the default encoding to UTF-8
sys.stdout.reconfigure(encoding="utf-8")

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"


def calculate_and_export_difficulties():
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    m = ""
    pls_print = False

    with open(
        "difficulties_data.txt",
        "w",
        encoding="utf-8",
    ) as f:
        for filename in all_files:
            if m in filename.lower():
                try:
                    char = "\\"
                    m_map = MuseSwiprMap(f"{DATA_DIR}/{filename}")
                    # segments = analyse_segments(m_map.notes, m_map.sample_rate)
                    name = filename.split("\\")[-1].split(".asset")[0]
                    # print(name)
                    # print_patterns(patterns, m_map.sample_rate)

                    print(filename)
                    with open(
                        f"analysis/{name}",
                        "w",
                        encoding="utf-8",
                    ) as outfile:
                        (weighting, difficulty, final,) = calculate_difficulty(
                            m_map.notes,
                            outfile=outfile,
                            sample_rate=m_map.sample_rate,
                            pls_print=pls_print,
                        )
                        f.write(
                            f"{filename.split(char)[-1].split('.asset')[0]}||{final:.2f}||{weighting:.2f}||{difficulty:.2f}\n"
                        )
                    m_map.output_notes(
                        f"{name}.txt",
                        m_map.sample_rate,
                    )
                except Exception as e:
                    print(f"ERROR parsing a file: {e}")
                    continue


if __name__ == "__main__":
    calculate_and_export_difficulties()
