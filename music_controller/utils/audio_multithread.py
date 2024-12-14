'''
Still in process ! This helps eliminate noise when playing piano sounds during real-time interaction.
'''
import threading
import queue
import numpy as np
import pyaudio
import time
import logging
from typing import Optional
from music_controller.instruments import Piano, PluckedString, Theremin, Drums

class AudioMultithread:
    def __init__(self, rate=44100, chunk_size=1024, buffer_size=10):
        self.rate = rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue(maxsize=buffer_size)
        self.is_running = False
        self.current_pitch = None
        self.current_volume = None
        
        # Current instrument and parameters
        self.current_instrument = None
        self.last_pitch = None
        self.buffer = np.zeros(rate * 2)  # 2 seconds buffer
        self.write_position = 0
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Lock for thread safety
        self.buffer_lock = threading.Lock()
        
        # Start worker threads
        self.audio_generator_thread = threading.Thread(target=self._audio_generator_loop)
        self.audio_player_thread = threading.Thread(target=self._audio_player_loop)

    def start_playback_thread(self):
        """Start the audio playback thread"""
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self._audio_playback_loop)
        self.playback_thread.daemon = True  # Thread will stop when main program stops
        self.playback_thread.start()

    def _audio_playback_loop(self):
        """Audio playback thread loop"""
        while self.is_playing:
            try:
                # Get audio chunk from queue with timeout
                audio_chunk = self.audio_queue.get(timeout=0.1)
                self.stream.write(audio_chunk.tobytes())
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio playback error: {e}")
                continue