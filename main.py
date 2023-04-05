import config.logging_config as logging_config

logger = logging_config.logger
import os

from difficulty_calculation import calculate_difficulty
from entities import MuseSwiprMap

DATA_DIR = "data"


def calculate_and_export_difficulties():
    # get a list of all files in the directory
    all_files = os.listdir(DATA_DIR)

    m = ""

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


if __name__ == "__main__":
    logger.info("Running the main file")
    calculate_and_export_difficulties()
