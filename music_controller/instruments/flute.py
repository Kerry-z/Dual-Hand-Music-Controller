"""
Flute Sound Synthesis Module (Under development)
========================================================================

This module simulates flute sounds by combining harmonic content, vibrato effects, ADSR (Attack, Decay, Sustain, Release) envelopes, and breath noise. The synthesis is designed to mimic the natural characteristics of a flute.

Key Features:
-------------
1. **Harmonic Synthesis**:
   - Simulates flute harmonics with normalized amplitudes for realism.
   - Fundamental frequency and harmonics (up to the 5th) are generated.

2. **Vibrato**:
   - Applies low-frequency oscillations (LFO) to modulate pitch dynamically.
   - Adjustable rate and depth for vibrato customization.

3. **ADSR Envelope**:
   - Smooth transitions between attack, decay, sustain, and release phases.
   - Models the dynamic shaping of notes during play.

4. **Breath Noise**:
   - Adds subtle noise to emulate air turbulence in a real flute.

Presets:
--------
1. **Concert Flute**: Standard flute configuration with mild breath noise and vibrato.
2. **Alto Flute**: Darker tone with adjusted harmonic structure and stronger breath noise.

Limitations:
------------
1. **Sound Quality**:
   - The synthesized sound does not closely resemble a real flute, failing to capture its natural warmth and dynamics.

2. **Computational Complexity**:
   - The harmonic generation and vibrato calculations introduce latency unsuitable for real-time interactive systems.

3. **Interaction Model**:
   - Lacks gesture-based interaction and sensitivity, which are critical for no-touch instrument projects.

4. **Static Behavior**:
   - Does not adapt well to nuanced changes in input, making it less expressive.

Based on:
--------
1. Harmonic synthesis with vibrato modulation.
2. Standard ADSR envelope modeling for dynamic sound shaping.
"""

import numpy as np
from .base_instrument import BaseInstrument
from typing import Optional, Tuple

class Flute(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):
        super().__init__(sample_rate, chunk_size)
        # Basic flute parameters
        self.air_decay = 0.997
        self.breath_intensity = 0.02
        
        # Vibrato parameters
        self.vibrato_rate = 5.0    # Hz
        self.vibrato_depth = 0.01  # Fraction of frequency
        self.vibrato_phase = 0.0   # Current phase of vibrato LFO
        
        # Harmonic structure (normalized amplitudes)
        total_amplitude = 1.0 + 0.5 + 0.3 + 0.1 + 0.05  # Sum of all harmonics
        self.harmonic_amplitudes = {
            1: 1.0 / total_amplitude,    # Fundamental
            2: 0.5 / total_amplitude,    # 2nd harmonic
            3: 0.3 / total_amplitude,    # 3rd harmonic
            4: 0.1 / total_amplitude,    # 4th harmonic
            5: 0.05 / total_amplitude    # 5th harmonic
        }
        
        # ADSR envelope parameters (in seconds)
        self.attack_time = 0.1
        self.decay_time = 0.1
        self.sustain_level = 0.8
        self.release_time = 0.2
        
        # State variables
        self.oscillators = []
        self.prev_frequency = None
        self.envelope_state = 0.0
        self.time_in_note = 0.0
        self.note_on = False
        
    def _initialize_oscillators(self, frequency: float):
        """Initialize oscillators for fundamental and harmonics"""
        self.oscillators = []
        for harmonic, amplitude in self.harmonic_amplitudes.items():
            self.oscillators.append({
                'frequency': frequency * harmonic,
                'amplitude': amplitude,
                'phase': 0.0
            })
    
    def _generate_vibrato(self, chunk_size: int) -> np.ndarray:
        """Generate vibrato modulation"""
        t = np.arange(chunk_size) / self.sample_rate
        vibrato = self.vibrato_depth * np.sin(
            2 * np.pi * self.vibrato_rate * t + self.vibrato_phase
        )
        self.vibrato_phase += 2 * np.pi * self.vibrato_rate * (chunk_size / self.sample_rate)
        self.vibrato_phase %= 2 * np.pi
        return vibrato
    
    def _generate_harmonic_content(self, frequency: float, 
                                 vibrato: np.ndarray, 
                                 chunk_size: int) -> np.ndarray:
        """Generate harmonics with vibrato"""
        output = np.zeros(chunk_size, dtype=np.float32)
        dt = 1.0 / self.sample_rate
        
        for osc in self.oscillators:
            # Apply vibrato to frequency
            freq_mod = osc['frequency'] * (1 + vibrato)
            
            # Generate samples for this harmonic
            t = np.arange(chunk_size) * dt
            phase_increment = 2 * np.pi * freq_mod * dt
            phases = osc['phase'] + np.cumsum(phase_increment)
            
            # Add harmonic to output
            output += osc['amplitude'] * np.sin(phases).astype(np.float32)
            
            # Update oscillator phase
            osc['phase'] = phases[-1] % (2 * np.pi)
            
        return output
    
    def _update_envelope(self, chunk_size: int) -> np.ndarray:
        """Generate ADSR envelope"""
        envelope = np.zeros(chunk_size, dtype=np.float32)
        dt = 1.0 / self.sample_rate
        
        for i in range(chunk_size):
            if not self.note_on:
                # Release phase
                self.envelope_state = max(0, self.envelope_state - 
                                       dt / self.release_time)
            else:
                if self.time_in_note < self.attack_time:
                    # Attack phase
                    self.envelope_state = self.time_in_note / self.attack_time
                elif self.time_in_note < (self.attack_time + self.decay_time):
                    # Decay phase
                    decay_progress = (self.time_in_note - self.attack_time) / self.decay_time
                    self.envelope_state = 1.0 + (self.sustain_level - 1.0) * decay_progress
                else:
                    # Sustain phase
                    self.envelope_state = self.sustain_level
                    
            envelope[i] = self.envelope_state
            self.time_in_note += dt
            
        return envelope
    
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        """Generate flute sound with all effects, returning float32 values in [-1, 1]"""
        if frequency != self.prev_frequency:
            self._initialize_oscillators(frequency)
            self.prev_frequency = frequency
            
        # Generate basic components
        vibrato = self._generate_vibrato(self.chunk_size)
        harmonic_content = self._generate_harmonic_content(
            frequency, vibrato, self.chunk_size
        )
        
        # Generate breath noise (scaled down to prevent overflow)
        breath_noise = np.random.normal(
            0, self.breath_intensity, self.chunk_size
        ).astype(np.float32) * 0.1
        
        # Combine components
        output = harmonic_content + breath_noise
        
        # Apply envelope
        envelope = self._update_envelope(self.chunk_size)
        output *= envelope
        
        # Apply volume
        output *= volume
        
        # Ensure output is in [-1, 1] range
        output = np.clip(output, -1.0, 1.0)
        
        return output.astype(np.float32)
    
    def set_vibrato(self, rate: float, depth: float):
        """Adjust vibrato parameters"""
        self.vibrato_rate = np.clip(rate, 0.1, 10.0)
        self.vibrato_depth = np.clip(depth, 0.0, 0.1)
    
    def set_envelope(self, attack: float, decay: float, 
                    sustain: float, release: float):
        """Set ADSR envelope parameters"""
        self.attack_time = np.clip(attack, 0.01, 1.0)
        self.decay_time = np.clip(decay, 0.01, 1.0)
        self.sustain_level = np.clip(sustain, 0.0, 1.0)
        self.release_time = np.clip(release, 0.01, 2.0)

    @classmethod
    def concert_flute(cls, sample_rate: int, chunk_size: int) -> 'Flute':
        """Create a concert flute preset"""
        flute = cls(sample_rate, chunk_size)
        flute.set_vibrato(5.0, 0.01)
        flute.breath_intensity = 0.02
        flute.set_envelope(0.1, 0.1, 0.8, 0.2)
        return flute

    @classmethod
    def alto_flute(cls, sample_rate: int, chunk_size: int) -> 'Flute':
        """Create an alto flute preset"""
        flute = cls(sample_rate, chunk_size)
        flute.set_vibrato(4.5, 0.015)
        flute.breath_intensity = 0.025
        # Normalize harmonic amplitudes
        total_amplitude = 1.0 + 0.6 + 0.4 + 0.15 + 0.08
        flute.harmonic_amplitudes = {
            1: 1.0 / total_amplitude,
            2: 0.6 / total_amplitude,
            3: 0.4 / total_amplitude,
            4: 0.15 / total_amplitude,
            5: 0.08 / total_amplitude
        }
        flute.set_envelope(0.15, 0.12, 0.75, 0.25)
        return flute