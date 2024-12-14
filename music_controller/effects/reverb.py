# effects/reverb.py
from .base_effect import AudioEffect
import numpy as np
from scipy import signal

class Reverb(AudioEffect):
    def __init__(self, 
                 sample_rate: int, 
                 room_size: float = 0.8, 
                 damping: float = 0.5, 
                 mix: float = 0.3,
                 early_reflections: int = 8):
        """
        Initialize reverb effect
        
        Args:
            sample_rate: Audio sample rate in Hz
            room_size: Size of the virtual room (affects decay time)
            damping: High frequency damping factor
            mix: Wet/dry mix (0.0 = dry only, 1.0 = wet only)
            early_reflections: Number of early reflections to simulate
        """
        self.sample_rate = sample_rate
        self.room_size = np.clip(room_size, 0.1, 0.99)
        self.damping = np.clip(damping, 0.0, 0.99)
        self.mix = np.clip(mix, 0.0, 1.0)
        self.early_reflections = early_reflections
        self.create_impulse_response()
        
    def create_impulse_response(self):
        """Create a realistic room impulse response"""
        # Calculate reverb time based on room size
        rt60 = self.room_size * 2.0  # 2 seconds at maximum room size
        length = int(self.sample_rate * rt60)
        
        # Create exponential decay
        time = np.linspace(0, rt60, length)
        decay = np.exp(-self.damping * time)
        
        # Add early reflections
        early_times = np.linspace(0.01, 0.1, self.early_reflections)
        for t in early_times:
            idx = int(t * self.sample_rate)
            if idx < length:
                decay[idx] += (1.0 - t/0.1) * 0.5
        
        # Add frequency-dependent decay
        noise = np.random.randn(length)
        # Low-pass filter the noise more as time increases
        for i in range(len(noise)):
            cutoff = np.exp(-self.damping * i / length)
            noise[i] *= cutoff
        
        self.impulse = decay * noise
        
        # Normalize impulse response
        self.impulse = self.impulse / np.max(np.abs(self.impulse))
        
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through reverb effect"""
        # Compute reverb signal
        wet = signal.convolve(audio, self.impulse, mode='same')
        
        # Mix dry and wet signals
        output = audio * (1 - self.mix) + wet * self.mix
        
        # Normalize output to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output = output / max_val
            
        return output