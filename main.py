import config.logging_config as logging_config

logger = logging_config.logger
import os

from musemapalyzr.difficulty_calculation import calculate_difficulty
from musemapalyzr.entities import MuseSwiprMap

DATA_DIR = "data"


def calculate_and_export_filtered_difficulties(string):
    all_files = os.listdir(DATA_DIR)
    filtered = []
    # get only files with string in it
    for f in all_files:
        if string.lower() in f.lower():
            filtered.append(f)

    _process_difficulties(filtered)


def _process_difficulties(files):

    with open(
        "difficulties_data.txt",
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
                    (weighting, difficulty, final,) = calculate_difficulty(
                        m_map.notes, outfile=outfile, sample_rate=m_map.sample_rate
                    )
                    f.write(
                        f"{filename.split(char)[-1].split('.asset')[0]}||{final:.2f}||{weighting:.2f}||{difficulty:.2f}\n"
                    )
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


if __name__ == "__main__":
    logger.info("Running the main file")
    string = "the pressure - tension"
    calculate_and_export_filtered_difficulties(string)
    # calculate_and_export_all_difficulties()
