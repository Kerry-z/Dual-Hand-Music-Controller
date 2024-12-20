"""
Synthesizer Module with Multi-Oscillator, ADSR Envelope, and Filtering
========================================================================

This module implements a simple synthesizer or a demo capable of generating a wide range of sounds using four basic waveforms, 
dual oscillators, an ADSR (Attack, Decay, Sustain, Release) envelope, and a low-pass filter. 
The design is trying to create basslines, leads, and other synthesized sounds.

Mathematical Model:
-----------------
1. Oscillator:
   waveform(phase) generates the basic waveform (sine, square, sawtooth, triangle) with detuning for richer sound.
   - phase = 2pi * frequency * t
   - detune modifies frequency slightly to create harmonic interactions.

2. ADSR Envelope:
   Attack-Decay-Sustain-Release shape modifies volume over time:
   - Attack: Linear ramp-up over `attack` seconds.
   - Decay: Linear reduction to `sustain` level over `decay` seconds.
   - Sustain: Constant level during note duration.
   - Release: Exponential fade-out over `release` seconds.

3. Low-Pass Filter:
   Filter coefficients are calculated using Butterworth filter design:
   - \( H(z) = \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}} \)
   - Used to smooth high frequencies and shape timbre.

Key Features:
-------------
- Oscillator Parameters:
  - `waveform`: Type of waveform (e.g., sine, square).
  - `volume`: Relative amplitude of each oscillator.
  - `detune`: Slight frequency offsets to create richer sounds.
- ADSR Envelope Parameters:
  - `attack`: Time to reach peak volume.
  - `decay`: Time to settle to sustain level.
  - `sustain`: Constant volume level after decay.
  - `release`: Time to fade out after note release.
- Filter Parameters:
  - `filter_cutoff`: Determines the frequency above which harmonics are attenuated.

Presets:
-------
1. Bass: Uses sawtooth and square waveforms with a low cutoff for a deep sound.
2. Lead: Combines sine and triangle waveforms with a higher cutoff for clarity.

Based on:
--------
It is just a simple demo here, which is flexible for user to add their code to generate sounds, and 
it doesn't work well at this time.
No specific prior work but draws inspiration from classic subtractive synthesizers.
"""
from .base_instrument import BaseInstrument
import numpy as np
from scipy import signal
from typing import List, Dict, Optional
from scipy.signal import butter, lfilter

class Synthesizer(BaseInstrument):
    def __init__(self, sample_rate: int, chunk_size: int):
        super().__init__(sample_rate, chunk_size)
        
        # Basic waveforms
        self.waveforms = {
            'sine': np.sin,
            'square': signal.square,
            'sawtooth': signal.sawtooth,
            'triangle': lambda x: signal.sawtooth(x, 0.5)
        }
        
        # Two simple oscillators
        self.oscillators = [
            {'waveform': 'sine', 'volume': 1.0, 'detune': 0.0},
            {'waveform': 'sawtooth', 'volume': 0.5, 'detune': 0.01}
        ]
        
        # Simple ADSR envelope
        self.attack = 0.1    # seconds
        self.decay = 0.2     # seconds
        self.sustain = 0.7   # level (0-1)
        self.release = 0.3   # seconds
        
        # Simple lowpass filter
        self.filter_cutoff = 1000.0  # Hz
        
        # Initialize filter coefficients and state
        nyquist = self.sample_rate / 2
        cutoff = self.filter_cutoff / nyquist
        self.b, self.a = butter(2, cutoff, btype='low')
        self.filter_state = np.zeros(len(self.b) - 1)
        
        # Previous volume for envelope tracking
        self.prev_volume = 0.0
    
    def set_oscillator(self, osc_num: int, waveform: str, volume: float, detune: float):
        """Configure an oscillator"""
        if osc_num < len(self.oscillators):
            self.oscillators[osc_num].update({
                'waveform': waveform,
                'volume': np.clip(volume, 0.0, 1.0),
                'detune': np.clip(detune, -0.1, 0.1)
            })
    
    def set_envelope(self, attack: float, decay: float, sustain: float, release: float):
        """Set ADSR envelope parameters"""
        self.attack = np.clip(attack, 0.01, 2.0)
        self.decay = np.clip(decay, 0.01, 2.0)
        self.sustain = np.clip(sustain, 0.0, 1.0)
        self.release = np.clip(release, 0.01, 2.0)
    
    def set_filter_cutoff(self, cutoff: float):
        """Set filter cutoff frequency"""
        self.filter_cutoff = np.clip(cutoff, 20.0, self.sample_rate/2)
        nyquist = self.sample_rate / 2
        normalized_cutoff = self.filter_cutoff / nyquist
        self.b, self.a = butter(2, normalized_cutoff, btype='low')
        self.filter_state = np.zeros(len(self.b) - 1)
    
    def _apply_envelope(self, volume: float) -> float:
        """Simple envelope following current volume"""
        if volume > self.prev_volume:
            # Attack phase
            envelope = self.prev_volume + (volume - self.prev_volume) * 0.1
        else:
            # Release phase
            envelope = self.prev_volume + (volume - self.prev_volume) * 0.2
            
        self.prev_volume = envelope
        return envelope
    
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        """Generate synthesizer sound"""
        if frequency is None or volume is None:
            return np.zeros(self.chunk_size, dtype=np.float32)
        
        # Generate time array
        t = np.linspace(0, self.chunk_size/self.sample_rate, self.chunk_size)
        
        # Initialize output
        output = np.zeros(self.chunk_size, dtype=np.float32)
        
        # Generate each oscillator
        for osc in self.oscillators:
            # Calculate frequency with detune
            osc_freq = frequency * (1 + osc['detune'])
            
            # Generate waveform
            phase = 2 * np.pi * osc_freq * t
            wave = self.waveforms[osc['waveform']](phase)
            
            # Add to output with oscillator volume
            output += wave * osc['volume']
        
        # Normalize output
        output = output / len(self.oscillators)
        
        # Apply envelope
        envelope = self._apply_envelope(volume)
        output *= envelope
        
        # Apply lowpass filter
        output, self.filter_state = lfilter(self.b, self.a, output, zi=self.filter_state)
        
        # Ensure float32 output in [-1, 1] range
        return np.clip(output, -1.0, 1.0).astype(np.float32)

    @classmethod
    def create_bass_preset(cls, sample_rate: int, chunk_size: int) -> 'Synthesizer':
        """Create a simple bass synth preset as a less rigorous example"""
        synth = cls(sample_rate, chunk_size)
        synth.set_oscillator(0, 'sine', 0.5, 0.02)
        synth.set_oscillator(1, 'square', 0.5, 0.01)
        synth.set_envelope(0.01, 0.2, 0.7, 0.1)
        synth.set_filter_cutoff(1000)
        return synth
