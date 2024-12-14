import unittest
from instruments.base_instrument import BaseInstrument
from instruments.piano import Piano
from instruments.PluckedString import PluckedString
from instruments.theremin import Theremin
from instruments.drums import Drums
import numpy as np

class TestPiano(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.piano = Piano(sample_rate=self.sample_rate, chunk_size=self.chunk_size)

    def test_generate_sound(self):
        frequency = 440.0  # A4 note
        volume = 0.5
        sound = self.piano.generate_sound(frequency, volume)
        self.assertEqual(len(sound), self.chunk_size)
        self.assertTrue(isinstance(sound, np.ndarray))
        
    def test_volume_range(self):
        frequency = 440.0
        # Test volume boundaries
        sound_max = self.piano.generate_sound(frequency, 1.0)
        sound_min = self.piano.generate_sound(frequency, 0.0)
        self.assertTrue(np.max(np.abs(sound_max)) > np.max(np.abs(sound_min)))

class TestPluckedString(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.plucked = PluckedString(sample_rate=self.sample_rate, chunk_size=self.chunk_size)
    
    def test_generate_sound(self):
        frequency = 220.0  # A3 note
        volume = 0.7
        sound = self.plucked.generate_sound(frequency, volume)
        self.assertEqual(len(sound), self.chunk_size)
        self.assertTrue(isinstance(sound, np.ndarray))

class TestTheremin(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.theremin = Theremin(sample_rate=self.sample_rate, chunk_size=self.chunk_size)
    
    def test_generate_sound(self):
        frequency = 880.0  # A5 note
        volume = 0.6
        sound = self.theremin.generate_sound(frequency, volume)
        self.assertEqual(len(sound), self.chunk_size)
        self.assertTrue(isinstance(sound, np.ndarray))
        
    def test_continuous_frequency(self):
        # Test smooth frequency transition
        freq1 = 440.0
        freq2 = 445.0
        sound1 = self.theremin.generate_sound(freq1, 0.5)
        sound2 = self.theremin.generate_sound(freq2, 0.5)
        self.assertNotEqual(np.array_equal(sound1, sound2), True)

class TestDrums(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.drums = Drums(sample_rate=self.sample_rate, chunk_size=self.chunk_size)
    
    def test_different_drums(self):
        frequency = 880.0  # A5 note
        volume = 0.8
        # Test each drum type
        for drum_type in ['kick', 'snare', 'hihat', 'tom']:
            self.drums.current_drum = drum_type
            sound = self.drums.generate_sound(frequency, volume)  
            self.assertEqual(len(sound), self.chunk_size)
            self.assertTrue(isinstance(sound, np.ndarray))

if __name__ == '__main__':
    unittest.main()

'''
To run specific tests, you can use:

# Run tests for all instruments
python -m unittest test_instruments.py

# Run tests for a specific instrument
python -m unittest test_instruments.TestPiano

May faced problems:
- The term 'python' is not recognized as the name of a cmdlet, function, script file, or operable program.

If there is error about can not regonize 'python', you can run with this "& path/to/your/python/python.exe -m unittest path/to/your/download/project/file/test_instruments.py"

'''