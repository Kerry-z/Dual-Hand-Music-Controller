"""
Plucked String Instrument Simulator using Karplus-Strong Algorithm
========================================================================

This module implements a digital waveguide synthesis model for plucked string instruments
using an enhanced version of the Karplus-Strong algorithm. The implementation simulates
the physics of a vibrating string with additional parameters for realistic sound shaping. 
These parameters include string tension, decay rate, and low-pass filtering to create a more natural and dynamic sound.

Updates:
--------
- Unused parameters such as brightness, pluck position, body resonance, and noise amount
  are preserved but not actively utilized in the current implementation. These may be
  reintroduced or extended in future updates.

Mathematical Model:
-----------------
1. Basic Karplus-Strong Algorithm:
   y[n] = 0.5 * (y[n-P] + y[n-P-1]) * decay_factor
   where:
   - y[n] is the output signal at time n
   - P is the period (buffer_size = sample_rate/frequency)
   - decay_factor controls string energy dissipation

2. Enhanced Physics Model:
   The basic algorithm is extended with:
   a) String Tension Effect:
      tension_effect = tension * (new_sample - current_sample)
      - Simulates the restoring force of the string
      - Higher tension values create brighter, more metallic sounds
   
   b) Low-Pass Filter:
      H(z) = (b[0] + b[1]z^(-1)) / (1 + a[1]z^(-1))
      - Simulates frequency-dependent losses in the string
      - Creates warmer, more natural string tones

Key Parameters:
-------------
- string_decay (0.9-0.9999): Determines how quickly the string vibrations decay
- string_tension (0.1-0.5): Controls the stiffness and brightness of the string
- brightness, pluck_position, body_resonance, and noise_amount: Preserved for potential future enhancements but not actively used in the current implementation

Presets:
--------
Ready-to-use configurations for simulating plucked string instruments:
- Guitar: Emulates lower tension and longer decay *Not accurately implemented*
- Pipa: Balanced tension with medium decay *Not accurately implemented*
- Zither: Higher tension and shorter decay *Not accurately implemented*

Based on:
--------
1. Karplus, K. and Strong, A. (1983) - "Digital Synthesis of Plucked String and Drum Timbres"
2. Jaffe, D.A. and Smith, J.O. (1983) - "Extensions of the Karplus-Strong Plucked String Algorithm"
"""
import numpy as np
from .base_instrument import BaseInstrument
from typing import Optional

class PluckedString(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):
        super().__init__(sample_rate, chunk_size)
        # Basic string physics parameters
        self.string_decay = 0.999    # How quickly the string energy dissipates
        self.string_tension = 0.3    # String tension affecting wave propagation
        
        # Additional parameters for different instrument characteristics
        self.brightness = 0.5        # Controls high-frequency content
        self.pluck_position = 0.2    # Where along the string it's plucked (0-1)
        self.body_resonance = 0.3    # How much the body affects the sound
        self.noise_amount = 0.0001   # Amount of noise in string vibration
        
        # State variables
        self.buffer = None
        self.prev_frequency = None
        self.body_state = 0.0
        
    def set_params(self, 
                  decay: Optional[float] = None,
                  tension: Optional[float] = None,
                  brightness: Optional[float] = None,
                  pluck_pos: Optional[float] = None,
                  resonance: Optional[float] = None,
                  noise: Optional[float] = None):
        """Set instrument parameters to simulate different plucked string instruments"""
        if decay is not None:
            self.string_decay = np.clip(decay, 0.9, 0.9999)
        if tension is not None:
            self.string_tension = np.clip(tension, 0.1, 0.5)
        if brightness is not None:
            self.brightness = np.clip(brightness, 0.0, 1.0)
        if pluck_pos is not None:
            self.pluck_position = np.clip(pluck_pos, 0.1, 0.9)
        if resonance is not None:
            self.body_resonance = np.clip(resonance, 0.0, 0.5)
        if noise is not None:
            self.noise_amount = np.clip(noise, 0.0, 0.001)
        
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        # if frequency is None or volume is None:
        #     return np.zeros(self.chunk_size)
        # Determine buffer size based on frequency
        buffer_size = int(self.sample_rate/frequency)
        
        # Reset buffer if frequency changed significantly
        if (self.prev_frequency is None or 
            abs(frequency - self.prev_frequency) > 1.0 or 
            self.buffer is None or 
            len(self.buffer) != buffer_size):
            self.buffer = np.random.uniform(-1, 1, buffer_size)
            self.prev_frequency = frequency
            
        output = np.zeros(self.chunk_size)
        
        # Enhanced Karplus-Strong algorithm
        for i in range(self.chunk_size):
            # Get current sample
            output[i] = self.buffer[0]
            
            # Calculate new sample with string physics simulation
            new_sample = 0.5 * (self.buffer[0] + self.buffer[1])
            
            # Add string tension effect
            tension_effect = self.string_tension * (new_sample - self.buffer[0])
            new_sample += tension_effect
            
            # Apply string decay
            new_sample *= self.string_decay
            
            # Add subtle noise for more realistic string behavior
            new_sample += np.random.uniform(-0.0001, 0.0001)
            
            # Update buffer
            self.buffer = np.roll(self.buffer, -1)
            self.buffer[-1] = new_sample
            
        # Apply slight low-pass filter for warmth
        b, a = self._get_lowpass_coeffs()
        output = self._apply_filter(output, b, a)
        
        return output * volume
        
    def _get_lowpass_coeffs(self):
        """Generate coefficients for a simple low-pass filter"""
        cutoff = 0.1  # Normalized cutoff frequency
        b = [cutoff, cutoff]
        a = [1, cutoff - 1]
        return b, a
        
    def _apply_filter(self, signal: np.ndarray, b: list, a: list) -> np.ndarray:
        """Apply a simple IIR filter"""
        y = np.zeros_like(signal)
        x_prev = y_prev = 0
        
        for i in range(len(signal)):
            y[i] = b[0] * signal[i] + b[1] * x_prev - a[1] * y_prev
            x_prev = signal[i]
            y_prev = y[i]
            
        return y

    @classmethod
    def guitar_preset(cls, sample_rate: int, chunk_size: int) -> 'PluckedString':
        """Create a guitar-like instrument"""
        inst = cls(sample_rate, chunk_size)
        inst.set_params(decay=0.999, tension=0.1) # Example, may not correct
        return inst
    
    @classmethod
    def pipa_preset(cls, sample_rate: int, chunk_size: int) -> 'PluckedString':
        """Create a pipa-like instrument"""
        inst = cls(sample_rate, chunk_size)
        inst.set_params(decay=0.9985, tension=0.2)
        return inst

