import json
from typing import List, Union

import config.logging_config as logging_config
from musemapalyzr.constants import DEFAULT_SAMPLE_RATE

logger = logging_config.logger

MAP_OUTPUT = "map_outputs"


class Note:
    def __init__(self, lane, sample_time):
        self.lane: Union[0, 1] = lane
        self.sample_time: int = sample_time

    def __repr__(self):
        return f"{self.lane},{self.sample_time}"


class Segment:
    def __init__(
        self,
        segment_name,
        notes: List[Note],
        required_notes: int = 0,
        time_difference=None,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ):
        self.segment_name = segment_name
        self.notes = notes
        self.required_notes = required_notes
        self.time_difference = time_difference
        self.sample_rate = sample_rate

        if self.time_difference is None and len(self.notes) > 1:
            self.time_difference = abs(self.notes[1].sample_time - self.notes[0].sample_time)
            logger.debug(f"Auto setting time difference to: {self.time_difference}")

    @property
    def notes_per_second(self):
        if self.time_difference == 0:
            return 0
        return self.sample_rate / self.time_difference

    def __repr__(self) -> str:
        return f"{self.segment_name} {len(self.notes)} {self.time_difference}"


class MuseSwiprMap:
    def __init__(self):
        self.title = None
        self.temp_sections = None
        self.tracks = None
        self.notes = None
        self.sample_rate = None

    @classmethod
    def from_koreograph_asset(cls, koreograph_asset_filename: str):
        muse_map = cls()
        data = None
        with open(f"{koreograph_asset_filename}", "r", encoding="utf-8") as f:
            data = json.load(f)

        muse_map.title = list(data.keys())[0]
        muse_map.tempo_sections = data[muse_map.title]["value"]["mTempoSections"]
        muse_map.tracks = data[muse_map.title]["value"]["mTracks"]
        muse_map.notes = []

        muse_map.sample_rate = int(data[muse_map.title]["value"]["mSampleRate"])

        muse_map._parse_notes()
        return muse_map

    def _parse_notes(self):
        for t in self.tracks:
            note_times_data = t["mEventList"]
            for d in note_times_data:
                assert d["mStartSample"] == d["mEndSample"]
                if t["mEventID"] != "TimingPoint":
                    note = Note(int(t["mEventID"]), d["mStartSample"])
                    self.notes.append(note)

        self.notes = sorted(self.notes, key=lambda note: note.sample_time)

    def output_notes(self, file_path: str):
        """Writes a text file that visualises the map.

        Fun fact, this was written by ChatGPT

        Args:
            file_path (str): The filename to output to.
            sample_rate (int, optional): The map's sample rate. Defaults to DEFAULT_SAMPLE_RATE.
        """
        notes = self.notes
        # Find the smallest time distance between notes
        smallest_time_distance = min(
            note2.sample_time - note1.sample_time for note1, note2 in zip(notes, notes[1:])
        )

        # Sort the notes by descending time order
        sorted_notes = sorted(notes, key=lambda note: note.sample_time, reverse=True)

        # Get the range of time values to iterate over
        start_time = sorted_notes[-1].sample_time
        end_time = sorted_notes[0].sample_time + smallest_time_distance
        time_range = range(start_time, end_time, smallest_time_distance)

        # Write the output to the file
        with open(f"{MAP_OUTPUT}/{file_path}", "w") as file:
            for time in reversed(time_range):
                for note in sorted_notes:
                    if note.sample_time <= time < note.sample_time + smallest_time_distance:
                        if note.lane == 0:
                            file.write(f"{note.sample_time/self.sample_rate:.2f}| []\n")
                        elif note.lane == 1:
                            file.write(f"{note.sample_time/self.sample_rate:.2f}|      []\n")
                        break
                else:
                    file.write(f"{time/self.sample_rate:.2f}|\n")
