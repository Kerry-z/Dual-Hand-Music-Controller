'''
Attempt to use Wavelet Transforms to eliminate the low freq noise but the result is not good.

Not used, the noise reduction is done in the audio_processing module
'''

import numpy as np

class AudioNoiseReduction:
    def __init__(self, noise_floor: float, silence_threshold: float):
        self.noise_floor = noise_floor
        self.silence_threshold = silence_threshold

    def process_audio_chunk(self, audio: np.ndarray) -> np.ndarray:
        """Process audio chunk with noise reduction"""
        # Ensure audio is in float32 format
        audio = audio.astype(np.float32)

        # Calculate RMS level
        rms = np.sqrt(np.mean(np.square(audio)))

        # Apply noise gate
        if rms < self.noise_floor:
            return np.zeros_like(audio)

        # Simple noise reduction
        mask = np.abs(audio) < self.silence_threshold
        audio[mask] = 0

        # Smooth transitions using a Hanning window
        window = np.hanning(32)
        smoothed_audio = np.convolve(audio, window / window.sum(), mode='same')

        return smoothed_audio
