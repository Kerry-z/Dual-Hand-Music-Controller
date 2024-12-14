import unittest
import numpy as np
from scipy import signal
from music_controller.effects.base_effect import AudioEffect
from music_controller.effects.delay import Delay
from music_controller.effects.reverb import Reverb

class TestAudioEffect(unittest.TestCase):
    def test_abstract_class(self):
        """Test that AudioEffect cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            AudioEffect()

    def test_process_method(self):
        """Test that derived classes must implement process method"""
        class IncompleteEffect(AudioEffect):
            pass
            
        with self.assertRaises(TypeError):
            IncompleteEffect()

class TestDelay(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.delay_time = 0.1
        self.feedback = 0.3
        self.mix = 0.2
        self.delay = Delay(
            sample_rate=self.sample_rate,
            delay_time=self.delay_time,
            feedback=self.feedback,
            mix=self.mix
        )
        
    def test_initialization(self):
        """Test delay effect initialization"""
        self.assertEqual(self.delay.sample_rate, self.sample_rate)
        self.assertEqual(self.delay.delay_samples, int(self.delay_time * self.sample_rate))
        self.assertEqual(self.delay.feedback, self.feedback)
        self.assertEqual(self.delay.mix, self.mix)
        self.assertEqual(len(self.delay.buffer), self.delay.delay_samples)
        
    def test_feedback_clipping(self):
        """Test that feedback is clipped to safe values"""
        unsafe_delay = Delay(self.sample_rate, feedback=1.5)
        self.assertLess(unsafe_delay.feedback, 1.0)
        
        negative_delay = Delay(self.sample_rate, feedback=-0.5)
        self.assertEqual(negative_delay.feedback, 0.0)
        
    def test_mix_clipping(self):
        """Test that mix parameter is clipped to [0,1]"""
        over_mix = Delay(self.sample_rate, mix=1.5)
        self.assertEqual(over_mix.mix, 1.0)
        
        under_mix = Delay(self.sample_rate, mix=-0.5)
        self.assertEqual(under_mix.mix, 0.0)
        
    def test_process(self):
        """Test delay processing"""
        # Test with simple input
        test_signal = np.ones(1000)
        processed = self.delay.process(test_signal)
        
        # Check output length
        self.assertEqual(len(processed), len(test_signal))
        
        # Check if output is normalized
        self.assertLessEqual(np.max(np.abs(processed)), 1.0)
        
        # Check if delay is applied
        # The delayed signal should be different from the input
        self.assertFalse(np.array_equal(processed, test_signal))

class TestReverb(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 44100
        self.room_size = 0.8
        self.damping = 0.5
        self.mix = 0.3
        self.early_reflections = 8
        self.reverb = Reverb(
            sample_rate=self.sample_rate,
            room_size=self.room_size,
            damping=self.damping,
            mix=self.mix,
            early_reflections=self.early_reflections
        )
        
    def test_initialization(self):
        """Test reverb effect initialization"""
        self.assertEqual(self.reverb.sample_rate, self.sample_rate)
        self.assertEqual(self.reverb.room_size, self.room_size)
        self.assertEqual(self.reverb.damping, self.damping)
        self.assertEqual(self.reverb.mix, self.mix)
        self.assertEqual(self.reverb.early_reflections, self.early_reflections)
        
    def test_parameter_clipping(self):
        """Test that parameters are properly clipped"""
        # Test room size clipping
        big_room = Reverb(self.sample_rate, room_size=1.5)
        self.assertLess(big_room.room_size, 1.0)
        small_room = Reverb(self.sample_rate, room_size=0.05)
        self.assertGreaterEqual(small_room.room_size, 0.1)
        
        # Test damping clipping
        high_damp = Reverb(self.sample_rate, damping=1.5)
        self.assertLess(high_damp.damping, 1.0)
        negative_damp = Reverb(self.sample_rate, damping=-0.5)
        self.assertEqual(negative_damp.damping, 0.0)
        
        # Test mix clipping
        over_mix = Reverb(self.sample_rate, mix=1.5)
        self.assertEqual(over_mix.mix, 1.0)
        under_mix = Reverb(self.sample_rate, mix=-0.5)
        self.assertEqual(under_mix.mix, 0.0)
        
    def test_impulse_response(self):
        """Test impulse response creation"""
        # Check if impulse response is created
        self.assertTrue(hasattr(self.reverb, 'impulse'))
        
        # Check if impulse response is normalized
        self.assertLessEqual(np.max(np.abs(self.reverb.impulse)), 1.0)
        
        # Check if early reflections are present
        # The impulse response should have peaks in the early section
        early_section = self.reverb.impulse[:int(0.1 * self.sample_rate)]
        self.assertTrue(np.any(early_section > 0.1))
        
    def test_process(self):
        """Test reverb processing"""
        # Test with simple input
        test_signal = np.ones(1000)
        processed = self.reverb.process(test_signal)
        
        # Check output length
        self.assertEqual(len(processed), len(test_signal))
        
        # Check if output is normalized
        self.assertLessEqual(np.max(np.abs(processed)), 1.0)
        
        # Check if reverb is applied
        # The reverberated signal should be different from the input
        self.assertFalse(np.array_equal(processed, test_signal))
        
        # Test with silence
        silent_signal = np.zeros(1000)
        silent_processed = self.reverb.process(silent_signal)
        # Output should also be silent
        self.assertTrue(np.allclose(silent_processed, 0, atol=1e-10))

if __name__ == '__main__':
    unittest.main()

# Run all tests
# python -m unittest test_effects.py

# Run specific test class
# python -m unittest test_effects.TestDelay

# Example :

'''
PS E:NYU\Term3\DSPLab\Final\DualHandMusicController> & C:/Users/admin/.conda/envs/mediapipe_env/python.exe -m unittest e:/NYU/Term3/DSPLab/Final/DualHandMusicController/music_controller/tests/test_effects.py
..........
----------------------------------------------------------------------
Ran 10 tests in 0.434s

OK
'''