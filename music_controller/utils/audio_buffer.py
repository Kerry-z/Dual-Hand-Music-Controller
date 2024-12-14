import numpy as np

class AudioBuffer:
    """A circular buffer for audio processing with overlapping capability."""
    def __init__(self, sample_rate: int, chunk_size: int, duration: float = 2.0):
        self.chunk_size = chunk_size
        self.duration = duration
        self.buffer = np.zeros(duration * sample_rate, dtype=np.float32)
        self.remaining = np.zeros(duration * sample_rate, dtype=np.float32)
        self.write_position = 0
        self.read_position = 0
        self.smooth_factor = 0.1    # Factor for smoothing pitch transitions

    def add_audio(self, audio: np.ndarray):
        """Add new audio to buffer with overlapping."""
        length = min(len(audio), len(self.buffer) - self.write_position)

        sound = self.smooth_factor * self.buffer[self.write_position:self.write_position + length] + (1 - self.smooth_factor) *audio[:length]

        # Normalize the sound to have a consistent amplitude
        # max_amplitude = max(abs(sound.max()), abs(sound.min()))
        # if max_amplitude > 0:
        #     sound = sound / max_amplitude  # Normalize to a range of [-1, 1]

        self.buffer[self.write_position:self.write_position + length] = sound

        if length < len(audio):
            remaining = min(len(audio) - length, len(self.remaining))
            self.remaining[:remaining] += audio[length:length + remaining]
            self.read_position = remaining

    def get_chunk(self, chunk_size: int ) -> np.ndarray:
        """Get the next chunk of audio from buffer."""
        chunk = self.buffer[:chunk_size].copy()

        # Shift buffer and clear old data
        # Overlap helps average noise and ensures continuity between chunks
        chunk_size_with_overlap = int(chunk_size / 2)

        self.buffer[:-chunk_size_with_overlap] = self.buffer[chunk_size_with_overlap:]
        self.buffer[-chunk_size_with_overlap:] = self.remaining[:chunk_size_with_overlap]
        self.read_position -= chunk_size_with_overlap

        if self.read_position < 0:
            self.read_position = 0
            self.remaining = np.zeros(len(self.remaining), dtype=np.float32)

        return (chunk * 32767).astype(np.int16)

    def is_empty(self) -> bool:
        """Check if the buffer is empty."""
        return np.all(self.buffer == 0)