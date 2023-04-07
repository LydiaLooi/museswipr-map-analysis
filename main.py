import config.logging_config as logging_config

logger = logging_config.logger
import cProfile
import datetime
import os
import subprocess
import time

from musemapalyzr.difficulty_calculation import calculate_difficulty
from musemapalyzr.entities import MuseSwiprMap

DATA_DIR = "data"

OUTPUT_DIR = "difficulty_exports"


def calculate_and_export_filtered_difficulties(string):
    all_files = os.listdir(DATA_DIR)
    filtered = []
    # get only files with string in it
    for f in all_files:
        if string.lower() in f.lower():
            filtered.append(f)

    _process_difficulties(filtered)


def _process_difficulties(files, output_notes=False):
    now = datetime.datetime.now()
    with open(
        f"{OUTPUT_DIR}/{now.strftime('%Y-%m-%d_%H-%M-%S')}_difficulties_data.txt",
        "w",
        encoding="utf-8",
    ) as f:
        for filename in files:
            try:
                char = "\\"
                m_map = MuseSwiprMap(f"{DATA_DIR}/{filename}")
                name = filename.split(char)[-1].split(".asset")[0]
                logger.info(f"Processing: '{filename}'")
                with open(
                    f"analysis/{name}",
                    "w",
                    encoding="utf-8",
                ) as outfile:
                    weight_results = calculate_difficulty(
                        m_map.notes, outfile=outfile, sample_rate=m_map.sample_rate
                    )
                    f.write(
                        f"{filename.split(char)[-1].split('.asset')[0]}||{weight_results.weighted_difficulty:.2f}||{weight_results.weighting:.2f}||{weight_results.difficulty:.2f}\n"
                    )
                if output_notes:
                    m_map.output_notes(
                        f"{name}.txt",
                        m_map.sample_rate,
                    )
            except Exception as e:
                logger.error(f"ERROR parsing a file: {e}")
                continue


def calculate_and_export_all_difficulties():
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    _process_difficulties(all_files)


def run_bottle_neck_analysis():
    cProfile.run("calculate_and_export_all_difficulties()", "profile_stats")
    subprocess.run(["snakeviz", "profile_stats"])


if __name__ == "__main__":
    start_time = time.time()
    logger.info("Running the main file")
    string = "big black"

    # calculate_and_export_filtered_difficulties(string)
    calculate_and_export_all_difficulties()

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
