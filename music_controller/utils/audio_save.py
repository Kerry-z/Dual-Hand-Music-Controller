import numpy as np
import wave
import os
from datetime import datetime
from typing import Optional

class AudioSaver:
    def __init__(self, sample_rate: int = 44100, channels: int = 1, sample_width: int = 2):
        """
        Initialize AudioSaver
        
        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            sample_width: Sample width in bytes (2 for 16-bit audio)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.buffer = []
        self.recording = False
        
        # Create recordings directory if it doesn't exist
        self.recordings_dir = os.path.join(os.getcwd(), 'recordings')
        os.makedirs(self.recordings_dir, exist_ok=True)
        
    def start_recording(self):
        """Start a new recording session"""
        self.buffer = []
        self.recording = True
        
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save the audio file
        
        Returns:
            str: Path to the saved audio file, or None if no audio was recorded
        """
        if not self.recording or not self.buffer:
            return None
            
        self.recording = False
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(self.recordings_dir, filename)
        
        # Combine all audio chunks
        audio_data = np.concatenate(self.buffer)
        
        # Save as WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"Audio saved to: {filepath}")
        self.clear()
        return filepath
        
    def add_audio(self, audio: np.ndarray):
        """
        Add audio chunk to the recording buffer
        
        Args:
            audio: Audio data as numpy array
        """
        if self.recording:
            # Convert to int16 if not already since the width is 2 
            if audio.dtype != np.int16:
                audio = (audio * 32767).astype(np.int16)
            self.buffer.append(audio)
    
    def clear(self):
        """Clear the recording buffer"""
        self.buffer = []
        self.recording = False
    
    def get_duration(self) -> float:
        """
        Get the current duration of recorded audio
        
        Returns:
            float: Duration in seconds
        """
        if not self.buffer:
            return 0.0
            
        total_samples = sum(len(chunk) for chunk in self.buffer)
        return total_samples / self.sample_rate
    
    def save_current(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Save current buffer to a specific file
        
        Args:
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file, or None if no audio was recorded
        """
        if not self.buffer:
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            
        filepath = os.path.join(self.recordings_dir, filename)
        
        # Combine and save audio
        audio_data = np.concatenate(self.buffer)
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
            
        return filepath