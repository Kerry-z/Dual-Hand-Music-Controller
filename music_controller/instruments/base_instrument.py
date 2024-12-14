from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

class BaseInstrument(ABC):
    def __init__(self, sample_rate: int, chunk_size: int):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
    @abstractmethod
    def generate_sound(self, frequency: Optional[float], volume: Optional[float]) -> np.ndarray:
        """Generate audio samples for the instrument.
        
        Args:
            frequency (float): The fundamental frequency of the note
            volume (float): The volume level (0.0 to 1.0)
            
        Returns:
            np.ndarray: Audio samples
        """
        pass