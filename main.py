import json

LANE_1_ID = 0
LANE_2_ID = 1

DATA_DIR = "data"

class Note:
    def __init__(self, lane, time):
        self.lane = lane
        self.time = time

    def __repr__(self):
        return f"{self.lane},{self.time}"

class MuseSwiprMap:
    def __init__(self, koreograph_asset_filename):

        data = None
        with open(f"{DATA_DIR}/{koreograph_asset_filename}", "r") as f:
            data = json.load(f)

        self.title = list(data.keys())[0]
        self.tempo_sections = data[self.title]["value"]["mTempoSections"]
        self.tracks = data[self.title]["value"]["mTracks"]
        self.notes = []

        self._parse_notes()

    def _parse_notes(self):
        for t in self.tracks:
            note_times_data = t["mEventList"]
            for d in note_times_data:
                assert d["mStartSample"] == d["mEndSample"]
                note = Note(int(t["mEventID"]), d["mStartSample"])
                self.notes.append(note)
        
        self.notes = sorted(self.notes, key=lambda note: note.time)

    def output_notes(self, file_path):
        """
        Written by ChatGPT. May have errors but it's neat :)
        """
        notes = self.notes
        # Find the smallest time distance between notes
        smallest_time_distance = min(note2.time - note1.time for note1, note2 in zip(notes, notes[1:]))
        
        # Sort the notes by descending time order
        sorted_notes = sorted(notes, key=lambda note: note.time, reverse=True)
        
        # Get the range of time values to iterate over
        start_time = sorted_notes[-1].time
        end_time = sorted_notes[0].time + smallest_time_distance
        time_range = range(start_time, end_time, smallest_time_distance)
        
        # Write the output to the file
        with open(file_path, 'w') as file:
            for time in reversed(time_range):
                for note in sorted_notes:
                    if note.time <= time < note.time + smallest_time_distance:
                        if note.lane == 0:
                            file.write("[]\n")
                        elif note.lane == 1:
                            file.write("     []\n")
                        break
                else:
                    file.write("\n")

if __name__ == "__main__":
    m_map = MuseSwiprMap("Sanguine.asset")

    m_map.output_notes("output.txt")