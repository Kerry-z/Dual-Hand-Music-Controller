from .base_effect import AudioEffect
import numpy as np

class Delay(AudioEffect):
    def __init__(self, sample_rate: int, delay_time: float = 0.1, feedback: float = 0.3, mix: float = 0.2):
        self.sample_rate = sample_rate
        self.delay_samples = int(delay_time * sample_rate)
        self.feedback = np.clip(feedback, 0.0, 0.99)  # Prevent unstable feedback
        self.mix = np.clip(mix, 0.0, 1.0)
        self.buffer = np.zeros(self.delay_samples)
        self.buffer_index = 0
        
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through delay effect"""
        output = np.zeros_like(audio)
        for i in range(len(audio)):
            # Read from delay buffer
            delayed = self.buffer[self.buffer_index]
            
            # Write to delay buffer with feedback
            self.buffer[self.buffer_index] = audio[i] + (delayed * self.feedback)
            
            # Move buffer index
            self.buffer_index = (self.buffer_index + 1) % self.delay_samples
            
            # Mix dry and wet signals
            output[i] = audio[i] * (1 - self.mix) + delayed * self.mix
            
        # Normalize output to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output = output / max_val
            
        return output