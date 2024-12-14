"""
Digital Piano Simulation Module 
========================================================================

This module implements a physical model of piano sound synthesis using digital waveguide techniques. The model simulates string vibration, hammer-string interaction, bridge coupling, and soundboard resonance to produce realistic piano tones.

Key Features:
-------------
1. Hammer-String Interaction:
   - Models the non-linear hammer force using displacement and velocity.
   - Hammer compression and hysteresis add realism.

2. Digital Waveguide for Strings:
   - Simulates left and right traveling waves with delay lines.
   - String damping models energy dissipation over time.

3. Bridge Coupling:
   - Applies a low-pass filter to simulate string-bridge impedance.

4. Soundboard Resonance:
   - Band-pass filtering models the resonance of the piano's soundboard.

5. Sympathetic Resonance:
   - Adds subtle randomness for realism.

Limitations:
------------
I didn't use this part of code in the final visulization and sound generation, but I still want to keep it for future reference.
The reason is that 

1. High computational complexity due to multiple filters and delay lines.
2. Not optimized for real-time response in interactive systems.
3. Lacks polyphonic capabilities for multi-key playing.
4. Unsuitable for video-based no-touch instruments due to the reliance on discrete frequency inputs.

Presets:
--------
1. Grand Piano: Brighter, more attack-heavy sound.
2. Upright Piano: Warmer, softer tone.

Based on:
--------
1. Physical modeling synthesis techniques.
2. Digital waveguide string simulation.
"""


import numpy as np
from .base_instrument import BaseInstrument
from typing import Optional
from scipy.signal import lfilter

class Piano(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):
        super().__init__(sample_rate, chunk_size)
        self.decay_time = 1.2
        self.current_states = np.zeros(2)
        self.harmonic_states = [np.zeros(2) for _ in range(3)]  # States for harmonics
        self.extended_size = int(self.decay_time * sample_rate)
        self._init_filters()
        
    def _init_filters(self):
        """Initialize resonant filter parameters with better stability"""
        # Use a more stable decay rate calculation
        self.r = np.exp(-1.0/(self.decay_time * self.sample_rate))

    def _create_filter_coeff(self, frequency: float):
        """Create filter coefficients for a given frequency"""
        omega = 2.0 * np.pi * frequency/self.sample_rate
        a = [1, -2 * self.r * np.cos(omega), self.r ** 2]
        b = [self.r * np.sin(omega)]
        return b, a
        
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        if frequency is None or volume is None:
            return np.zeros(self.extended_size)
            
        # Create shorter segments to process
        segment_size = min(self.chunk_size, self.extended_size)
        num_segments = (self.extended_size + segment_size - 1) // segment_size
        output = np.zeros(self.extended_size)
        
        # Process audio in segments
        for seg in range(num_segments):
            start_idx = seg * segment_size
            end_idx = min((seg + 1) * segment_size, self.extended_size)
            current_size = end_idx - start_idx
            
            # Create input for this segment
            x = np.zeros(current_size)
            if seg == 0:
                x[0] = 10000.0  # Initial impulse only in first segment
            
            # Get filter coefficients
            b, a = self._create_filter_coeff(frequency)
            
            # Process fundamental frequency
            y, self.current_states = lfilter(b, a, x, zi=self.current_states)
            segment_output = y
            
            # Add harmonics with better stability
            harmonic_weights = [0.5, 0.25, 0.125]  # Reduced weights
            
            for i, (weight, states) in enumerate(zip(harmonic_weights, self.harmonic_states)):
                b_harm, a_harm = self._create_filter_coeff(frequency * (i + 1))
                harmonic, new_states = lfilter(b_harm, a_harm, x, zi=states)
                segment_output += weight * harmonic
                self.harmonic_states[i] = new_states
            
            # Apply envelope to this segment
            t = np.linspace(start_idx/self.sample_rate, 
                          end_idx/self.sample_rate, 
                          current_size)
            decay_envelope = np.exp(-5 * t/self.decay_time)
            segment_output *= decay_envelope
            
            # Add minimal noise only to the beginning
            # if seg == 0:
            #     noise = np.random.randn(current_size) * 0.0005 * decay_envelope
            #     segment_output += noise
            
            # Add to output buffer
            output[start_idx:end_idx] = segment_output
        
        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val
            
        # Apply volume
        output *= volume
        
        # Ensure output is in float32 format and clipped
        return np.clip(output, -1.0, 1.0).astype(np.float32)
    
    @classmethod
    def create_bright_piano(cls, sample_rate: int, chunk_size: int) -> 'Piano':
        """Create a brighter sounding piano preset"""
        piano = cls(sample_rate, chunk_size)
        piano.decay_time = 1.0  # Slightly faster decay
        return piano
    
    @classmethod
    def create_soft_piano(cls, sample_rate: int, chunk_size: int) -> 'Piano':
        """Create a softer sounding piano preset"""
        piano = cls(sample_rate, chunk_size)
        piano.decay_time = 1.4  # Slightly longer decay
        return piano