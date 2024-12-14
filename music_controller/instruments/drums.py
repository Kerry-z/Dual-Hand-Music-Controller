"""
Drum Sounds Module
========================================================================

This module simulates a drum machine capable of generating sounds for different percussion instruments, including kick, snare, hi-hat, and toms. It employs frequency envelopes, noise generation, filtering, and amplitude envelopes to create realistic drum sounds.

Mathematical Model:
-----------------
1. Kick Drum:
   freq_env = exp(-t * 30) * 150 + 20
   - A decaying frequency envelope creates the "thump" characteristic of a kick drum.

2. Snare Drum:
   noise_filtered = butter_lowpass_filter(noise, cutoff=2000 Hz)
   - Combines a tonal component with filtered noise for a characteristic snare sound.

3. Hi-Hat:
   bandpass_filtered_noise = butter_bandpass_filter(noise, 4000 Hz - 8000 Hz)
   - High-frequency filtered noise creates the metallic tone of a hi-hat, enhanced with a resonance.

4. Tom Drum:
   freq_env = exp(-t * 15) * 100 + 50
   - Decaying frequency envelope simulates the deep resonance of a tom drum.

Key Parameters:
-------------
- Frequency Envelopes: Time-based decay for pitch modulation (e.g., `freq_env`).
- Noise: Random noise filtered for snare and hi-hat timbres.
- Envelopes: Amplitude envelopes for smooth decay.
- Filters: Low-pass and band-pass filters shape noise components.

Presets:
-------
1. Kick Drum: Low-frequency thump with punch.
2. Snare Drum: Tonal body with a noise component.
3. Hi-Hat: High-frequency noise with metallic resonance.
4. Tom Drum: Deep, resonant body with harmonics.

Based on:
--------
No specific prior work but inspired by the typical characteristics of acoustic drum sounds.
"""

import numpy as np
from .base_instrument import BaseInstrument
from scipy.signal import butter, filtfilt

class Drums(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):
        super().__init__(sample_rate, chunk_size)
        self.current_drum = 'kick'  # Default drum
        
    def generate_kick(self, volume: float) -> np.ndarray:
        t = np.linspace(0, self.chunk_size/self.sample_rate, self.chunk_size)
        
        # Frequency envelope for punch
        freq_env = np.exp(-t * 30) * 150 + 20
        
        # Generate sine wave with frequency envelope
        tone = np.sin(2 * np.pi * freq_env * t)
        
        # Add body punch with a second oscillator
        punch_freq = np.exp(-t * 50) * 80 + 40
        punch = 0.7 * np.sin(2 * np.pi * punch_freq * t)
        
        # Mix signals
        signal = tone + punch
        
        # Apply amplitude envelope
        envelope = np.exp(-t * 20)
        return signal * envelope * volume
        
    def generate_snare(self, volume: float) -> np.ndarray:
        t = np.linspace(0, self.chunk_size/self.sample_rate, self.chunk_size)
        
        # Generate body tone
        tone_freq = 180
        tone = np.sin(2 * np.pi * tone_freq * t)
        
        # Generate noise
        noise = np.random.uniform(-1, 1, len(t))
        
        # Filter noise for snare character
        b, a = butter(4, 2000/(self.sample_rate/2), btype='lowpass')
        filtered_noise = filtfilt(b, a, noise)
        
        # Apply different envelopes
        tone_env = np.exp(-t * 40)
        noise_env = np.exp(-t * 30)
        
        # Mix components
        mixed = tone * tone_env * 0.5 + filtered_noise * noise_env * 0.5
        return mixed * volume
        
    def generate_hihat(self, volume: float) -> np.ndarray:
        t = np.linspace(0, self.chunk_size/self.sample_rate, self.chunk_size)
        
        # Generate filtered noise
        noise = np.random.uniform(-1, 1, len(t))
        
        # Apply bandpass filter
        b, a = butter(4, [4000/(self.sample_rate/2), 
                               8000/(self.sample_rate/2)], btype='band')
        filtered_noise = filtfilt(b, a, noise)
        
        # Add high frequency resonance
        resonance_freq = 6000
        resonance = 0.3 * np.sin(2 * np.pi * resonance_freq * t)
        
        # Mix and apply envelope
        signal = filtered_noise + resonance
        envelope = np.exp(-t * 200)
        return signal * envelope * volume
        
    def generate_tom(self, volume: float) -> np.ndarray:
        t = np.linspace(0, self.chunk_size/self.sample_rate, self.chunk_size)
        
        # Frequency envelope for realistic tom sound
        freq_env = np.exp(-t * 15) * 100 + 50
        
        # Generate main tone
        tone = np.sin(2 * np.pi * freq_env * t)
        
        # Add subtle harmonics
        tone += 0.5 * np.sin(4 * np.pi * freq_env * t)
        tone += 0.25 * np.sin(6 * np.pi * freq_env * t)
        
        # Apply amplitude envelope
        envelope = np.exp(-t * 15)
        return tone * envelope * volume
        
    def generate_sound(self, trigger: float, volume: float) -> np.ndarray:
        if trigger is None or volume is None:
            return np.zeros(self.chunk_size)
        if self.current_drum == 'kick':
            return self.generate_kick(volume)
        elif self.current_drum == 'snare':
            return self.generate_snare(volume)
        elif self.current_drum == 'hihat':
            return self.generate_hihat(volume)
        else:  # tom
            return self.generate_tom(volume)