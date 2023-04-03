from entities import Note, MuseSwiprMap, Pattern

from pattern_analysis import MapPatternGroups
import os
from constants import *
from difficulty_calculation import analyze_patterns, print_patterns, calculate_difficulty

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

    p = analyze_patterns(notes)
    print_patterns(p)

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

    m = "sweetheart"

    for filename in file_list:
        try:
            char = "\\"
            mpg = MapPatternGroups()
            m_map = MuseSwiprMap(filename)

            name = filename.split("\\")[-1].split(".asset")[0]
            if m in name.lower():
                # for n in m_map.notes:
                #     print(n)
                p = analyze_patterns(m_map.notes)
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
    
    with open("difficulties_data.txt", "w", encoding="utf-8") as f:

        for filename in all_files:
            if m in filename.lower():
                try:
                    char = "\\"
                    m_map = MuseSwiprMap(f"{DATA_DIR}/{filename}")

                    name = filename.split("\\")[-1].split(".asset")[0]
                    print(filename)
                    with open(f"analysis/{name}", "w", encoding="utf-8") as outfile:
                        weighting, difficulty, final = calculate_difficulty(m_map.notes, outfile=outfile)
                        f.write(f"{filename.split(char)[-1].split('.asset')[0]}||{final:.2f}||{weighting:.2f}||{difficulty:.2f}\n")
                except Exception as e:
                    print(f"ERROR parsing a file: {e}")
                    continue
                
