import numpy as np
from scipy import signal

class AudioProcessor:
    @staticmethod
    def apply_envelope(audio: np.ndarray, attack: float, decay: float) -> np.ndarray:
        """Apply ADSR envelope to audio signal"""
        samples = len(audio)
        attack_samples = int(attack * samples)
        decay_samples = int(decay * samples)
        
        envelope = np.ones(samples)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
        
        return audio * envelope
    
    @staticmethod
    def apply_lowpass_filter(audio: np.ndarray, cutoff_freq: float, sample_rate: int, order: int = 4) -> np.ndarray:
        """
        Apply a low-pass filter to reduce high-frequency noise
        
        Parameters:
            audio (np.ndarray): Input audio signal
            cutoff_freq (float): Cutoff frequency in Hz
            sample_rate (int): Sample rate of the audio in Hz
            order (int): Filter order (higher = sharper cutoff but more processing)
            
        Returns:
            np.ndarray: Filtered audio signal
        """
        # Normalize cutoff frequency
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff_freq / nyquist

        # Design Butterworth filter
        b, a = signal.butter(order, normalized_cutoff, btype='low', analog=False)
        
        # Apply filter (use filtfilt for zero-phase filtering)
        filtered_audio = signal.filtfilt(b, a, audio)
        
        return filtered_audio

    @staticmethod
    def process_audio(audio: np.ndarray, sample_rate: int, 
                     attack: float = 0.1, decay: float = 0.1, 
                     cutoff_freq: float = 5000) -> np.ndarray:
        """
        Process audio with both envelope and low-pass filter
        
        Parameters:
            audio (np.ndarray): Input audio signal
            sample_rate (int): Sample rate of the audio in Hz
            attack (float): Attack time in ratio of total length
            decay (float): Decay time in ratio of total length
            cutoff_freq (float): Cutoff frequency for low-pass filter in Hz
            
        Returns:
            np.ndarray: Processed audio signal
        """
        # Apply low-pass filter first
        filtered_audio = AudioProcessor.apply_lowpass_filter(audio, cutoff_freq, sample_rate)
        
        # Then apply envelope
        processed_audio = AudioProcessor.apply_envelope(filtered_audio, attack, decay)
        
        return processed_audio