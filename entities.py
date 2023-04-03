from constants import *
from typing import List, Union
import json

MAP_OUTPUT = "map_outputs"
class Note:
    def __init__(self, lane, sample_time):
        self.lane: Union[0,1] = lane
        self.sample_time: int = sample_time

    def __repr__(self):
        return f"{self.lane},{self.sample_time}"

class Pattern:
    def __init__(self, pattern_name, notes: List[Note], required_notes: int=0, time_difference=None, sample_rate:int=DEFAULT_SAMPLE_RATE):
        self.pattern_name = pattern_name
        self.notes = notes
        self.required_notes = required_notes
        self.time_difference = time_difference
        self.sample_rate = sample_rate

        if self.time_difference is None and len(self.notes) > 1:
            print("Auto setting time difference...")
            self.time_difference = abs(self.notes[1].sample_time - self.notes[0].sample_time)

    @property
    def notes_per_second(self):
        return self.sample_rate / self.time_difference

    def __repr__(self) -> str:
        return f"{self.pattern_name} {len(self.notes)} {self.time_difference}"

class MuseSwiprMap:
    def __init__(self, koreograph_asset_filename):

        data = None
        with open(f"{koreograph_asset_filename}", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.title = list(data.keys())[0]
        self.tempo_sections = data[self.title]["value"]["mTempoSections"]
        self.tracks = data[self.title]["value"]["mTracks"]
        self.notes = []

        self.sample_rate = int(data[self.title]["value"]["mSampleRate"])

        self._parse_notes()

    def _parse_notes(self):
        for t in self.tracks:
            note_times_data = t["mEventList"]
            for d in note_times_data:
                assert d["mStartSample"] == d["mEndSample"]
                if t["mEventID"] != "TimingPoint":
                    note = Note(int(t["mEventID"]), d["mStartSample"])
                    self.notes.append(note)
        
        self.notes = sorted(self.notes, key=lambda note: note.sample_time)

    def output_notes(self, file_path, sample_rate:int=DEFAULT_SAMPLE_RATE):
        """
        Written by ChatGPT. May have errors but it's neat :)
        """
        notes = self.notes
        # Find the smallest time distance between notes
        smallest_time_distance = min(note2.sample_time - note1.sample_time for note1, note2 in zip(notes, notes[1:]))
        
        # Sort the notes by descending time order
        sorted_notes = sorted(notes, key=lambda note: note.sample_time, reverse=True)
        
        # Get the range of time values to iterate over
        start_time = sorted_notes[-1].sample_time
        end_time = sorted_notes[0].sample_time + smallest_time_distance
        time_range = range(start_time, end_time, smallest_time_distance)
        
        # Write the output to the file
        with open(f"{MAP_OUTPUT}/{file_path}", 'w') as file:
            for time in reversed(time_range):
                for note in sorted_notes:
                    if note.sample_time <= time < note.sample_time + smallest_time_distance:
                        if note.lane == 0:
                            file.write(f"{note.sample_time/sample_rate:.2f}| []\n")
                        elif note.lane == 1:
                            file.write(f"{note.sample_time/sample_rate:.2f}|      []\n")
                        break
                else:
                    file.write(f"{time/sample_rate:.2f}|\n")
