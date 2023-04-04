from entities import Note, MuseSwiprMap, Segment

from map_pattern_analysis import MapPatterns
import os
from constants import *
from difficulty_calculation import analyse_segments, print_segments, calculate_difficulty

import sys

# set the default encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"

def mini_test():

    notes = [
        Note(1,5669300),
        Note(1,5679100),
        Note(0,5688900),
        Note(1,5695433),
        Note(0,5701966),
        Note(1,5708500),
        Note(0,5715033),
        Note(1,5721566),
        Note(0,5728100),
        Note(1,5747700),
        Note(1,5757500),
        Note(1,5767300),
        Note(0,5773833),
        Note(1,5780366),
        Note(0,5786900),
        Note(1,5793433),
        Note(0,5799966),
    ]

    p = analyse_segments(notes)
    print_segments(p)

def run_analysis():

    # filter out any non-file entries
    file_list = []

    # maps_of_interest = ["kill the beat", "nothing but theory", "gimme da blood", "surf", "big black", "everything will freeze"]
    # maps_of_interest = ["surf"]

    # walk through all the directories and files in the specified path
    for root, directories, files in os.walk(DATA_DIR):
        for filename in files:
            # construct the full file path
            file_path = os.path.join(root, filename)
            # append the file path to the list
            file_list.append(file_path)

    m = "goodbounce"

    for filename in file_list:
        try:
            char = "\\"
            mpg = MapPatterns()
            m_map = MuseSwiprMap(filename)

            name = filename.split("\\")[-1].split(".asset")[0]
            if m in name.lower():
                # for n in m_map.notes:
                #     print(n)
                p = analyse_segments(m_map.notes)
                # groups = mpg.identify_pattern_groups(p)
                # # print(name)
                # for g in groups:
                #     print(g)
                # print("=" * 25)
                # print_patterns(p)
                calculate_difficulty(m_map.notes)
                m_map.output_notes(f"{name}.txt")
        except Exception as e:
            print(f"error parsing file: {filename}: {e}")
            continue

if __name__ == "__main__":
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    # mini_test()
    # run_analysis()

    m = ""
    pls_print = False
    
    with open("difficulties_data.txt", "w", encoding="utf-8") as f:

        for filename in all_files:
            if m in filename.lower():
                try:
                    char = "\\"
                    m_map = MuseSwiprMap(f"{DATA_DIR}/{filename}")
                    patterns = analyse_segments(m_map.notes, m_map.sample_rate)
                    name = filename.split("\\")[-1].split(".asset")[0]
                    # print(name)
                    # print_patterns(patterns, m_map.sample_rate)

                    print(filename) #  Printing filename might cause issues due to encoding stuff
                    with open(f"analysis/{name}", "w", encoding="utf-8") as outfile:
                        weighting, difficulty, final = calculate_difficulty(m_map.notes, outfile=outfile, sample_rate=m_map.sample_rate, pls_print=pls_print)
                        f.write(f"{filename.split(char)[-1].split('.asset')[0]}||{final:.2f}||{weighting:.2f}||{difficulty:.2f}\n")
                    m_map.output_notes(f"{name}.txt", m_map.sample_rate)
                except Exception as e:
                    print(f"ERROR parsing a file: {e}")
                    # raise e
                
