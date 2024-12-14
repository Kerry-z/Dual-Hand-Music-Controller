# effects/base_effect.py
from abc import ABC, abstractmethod
import numpy as np

class AudioEffect(ABC):
    @abstractmethod
    def process(self, audio: np.ndarray) -> np.ndarray:
        pass