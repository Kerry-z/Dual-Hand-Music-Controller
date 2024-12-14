# utils/note_utils.py

'''
Original used for creating a map for pitch including the note and octave and getting the nearest frequency of a note

Now, it's discarded because the mappinp and control method is changed and implemented in display_manager.py and controller.py

'''
import numpy as np
from typing import Dict, List

class NotePitchMapper:
    def __init__(self):
        self.base_freq = 440.0  # A4
        self.setup_note_mapping()
        
    def setup_note_mapping(self):
        # Create a mapping of positions to musical notes
        self.notes: Dict[str, float] = {}
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        for octave in range(3, 6):  # 3 octaves
            for i, note in enumerate(notes):
                freq = self.base_freq * (2 ** ((i - 9 + (octave - 4) * 12) / 12))
                self.notes[f"{note}{octave}"] = freq
                
        self.note_positions = np.linspace(0, 1, len(self.notes))
        self.frequencies = list(self.notes.values())
        
    def get_nearest_note_frequency(self, position: float) -> float:
        """Maps a continuous position (0-1) to the nearest musical note frequency"""
        idx = np.abs(self.note_positions - position).argmin()
        return self.frequencies[idx]