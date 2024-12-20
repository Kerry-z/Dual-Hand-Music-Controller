"""
Theremin Sound Module using Vibrato, Harmonics, and Inharmonic Components
========================================================================

This module implements a Theremin-like sound synthesizer. By simulating
frequency modulation (vibrato) and blending multiple harmonic and non-harmonic
partials, it creates a continuous, timbrally rich tone. An envelope function is
also applied to ensure smooth transitions at the start and end of each generated
audio chunk.

Mathematical Model:
-------------------
1. Vibrato (Frequency Modulation):
   - vibrato = sin(2 * pi * vibrato_rate * t) * vibrato_depth
   This periodically varies the pitch around the base frequency,
   enhancing expressiveness and adding a "humanized" feel.

2. Harmonics:
   - tone = sin(phase_1) 
        + 0.3 * sin(2 * phase_2) 
        + 0.15 * sin(3 * phase_3) 
        + 0.075 * sin(4 * phase_4)

    - phase_i = base_phases * (1 + vibrato * (1 - i * 0.2))
   
   Each harmonic is an integer multiple of the fundamental frequency.
   The decreasing amplitude of higher harmonics simulates natural spectral roll-off,
   resulting in a fuller, more realistic timbre.

3. Inharmonic Component:
   By introducing a partial at a non-integer multiple of the base frequency (e.g., 2.05 * f0),
   we break the pure harmonic structure. This adds complexity and can produce
   more unusual or bell-like tones. Here can also add the nosie to make it more realistic but 
   in my experiment, it didn't work well but create a lot of noise.

4. Envelope:
   A short fade-in/fade-out is applied to each chunk of audio:
   - Prevents clicks and pops at start/end points.
   - Smooths transitions, especially useful when concatenating multiple chunks.

5. Phase Smoothing:
   The phase continuity between successive chunks is maintained using a smoothing factor.
   This avoids sudden phase jumps that could introduce audible discontinuities.

6. Configurable Sound Duration:
    The parameter `sound_duration` determines the duration of each sound burst. 
    `extended_chunk_size` calculates the buffer size based on `sound_duration` and the sample rate. 
    This allows for balancing real-time responsiveness and computational efficiency.


Key Parameters:
---------------
- vibrato_rate (Hz): Frequency of the vibrato modulation.
- vibrato_depth: Amplitude of the vibrato in terms of frequency scaling.
- harmonics: The relative amplitudes of higher harmonics.
- non_harmonic_factor: A multiplier for adding an inharmonic partial.
- phase_smooth: A factor that controls how quickly the phase transitions to the new value.
- envelope_fade_time: Duration of the fade-in/out to smooth each audio segment's edges.
- sound_duration (seconds): Defines the duration of each sound burst.
- extended_chunk_size: The number of audio samples per generated chunk, based on sound_duration.


Presets:
-------
No preset configurations are provided, as all tones are dynamically generated based on input parameters.

Inspired by:
------------
Conceptually inspired by the characteristics of the Theremin instrument, known
for its continuously variable pitch and unique timbral qualities. While not a
physical model, this algorithmic approach captures some of the expressive
elements of a Theremin.
Some reference is here: 
[How The Theremin Works | Discover Instruments | Classic FM]{https://www.youtube.com/watch?v=9ONhwxx7Y6s}

Basic Logic reference is here:
[Theremin](https://github.com/Blue9/theremin/tree/master)
https://courses.ece.cornell.edu/ece5990/ECE5725_Spring2020_Projects/May_18_Demo/Theremin%202.0/gm484_rr655_monday/theremin.html

However, I add more function to the sound using the theorem in DSP.
"""

import numpy as np
from .base_instrument import BaseInstrument
from typing import Optional

class Theremin(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):# , times: int
        super().__init__(sample_rate, chunk_size)
        self.vibrato_rate = 5.0  # Hz, sets how fast the pitch oscillates
        self.vibrato_depth = 0.015  # Frequency multiplier for vibrato depth
        self.phase = 0             # Current phase accumulator
        self.prev_phase = 0        # Previous phase to assist in smoothing
        self.phase_smooth = 0.1    # Factor for smoothing phase transitions
        self.envelope_fade_time = 0.015  # Duration of fade-in/out in seconds
        self.sound_duration = 0.1  # Generate a short burst of sound
        self.extended_chunk_size = int(self.sound_duration * sample_rate)
        
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        if frequency is None or volume is None:
            return np.zeros(self.chunk_size)
        
        # Generate time array for extended duration
        t = np.linspace(0, self.sound_duration, self.extended_chunk_size)
        
        # Generate vibrato
        vibrato = np.sin(2 * np.pi * self.vibrato_rate * t) * self.vibrato_depth
        
        # Calculate phase increment for the main tone
        phase_inc = 2 * np.pi * frequency / self.sample_rate
        
        # Generate continuous phase
        phases = self.phase + np.cumsum(np.ones(self.extended_chunk_size)) * phase_inc
        
        # Smooth phase transition
        self.phase = phases[-1] % (2 * np.pi)
        
        # Generate main tone with harmonics
        tone = np.zeros(self.extended_chunk_size)

        # Sum of all harmonics and non-harmonic amplitude
        total_amplitude = 1.0 + 0.3 + 0.15 + 0.075 + 0.025 + 0.015

        # Fundamental frequency with vibrato
        tone += 1.0 / total_amplitude * np.sin(phases * (1 + vibrato))

        # Harmonics with decreasing amplitude and vibrato depth
        harmonics = [
            (0.3/total_amplitude, 2, 0.8),   # Second harmonic
            (0.15/total_amplitude, 3, 0.6),  # Third harmonic
            (0.075/total_amplitude, 4, 0.4), # Fourth harmonic
        ]
        
        for amplitude, harmonic, vib_scale in harmonics:
            tone += amplitude * np.sin(harmonic * phases * (1 + vibrato * vib_scale))
        
        # Non-harmonic components for texture
        non_harmonic_factors = [(0.025/total_amplitude, 2.05, 0.4), (0.015/total_amplitude, 3.07, 0.3)]
        for amplitude, factor, vib_scale in non_harmonic_factors:
            tone += amplitude * np.sin(factor * phases * (1 + vibrato * vib_scale))
        
        # Normalize the signal to ensure it does not exceed the valid amplitude range
        max_val = np.max(np.abs(tone))
        if max_val > 0:
            tone /= max_val
        
        # Apply volume envelope for smooth transitions
        envelope = np.ones_like(tone)
        fade_samples = int(self.envelope_fade_time * self.sample_rate) 
        if len(tone) > 2 * fade_samples:
            # Smooth fade in
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            # Smooth fade out
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        # Apply volume and envelope
        final_sound = tone * envelope * volume
        
        # Return the extended sound buffer
        return final_sound

