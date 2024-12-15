import cv2
import mediapipe as mp
import numpy as np
import pyaudio
from typing import Tuple, Optional
import logging
import threading
import queue
from music_controller.instruments import Piano, PluckedString, Theremin, Drums
from music_controller.effects import Delay, Reverb
from music_controller.utils import NotePitchMapper, AudioBuffer, AudioSaver, AudioNoiseReduction, AudioProcessor
from music_controller.visual import DisplayManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualHandMusicController:
    def __init__(self):
        """Initialize the music controller with all components"""

        self.duration = 2 # duration of the sound stored in the buffer, n = self.duration * self.RATE
        self.noise_floor = 0.02  # Adjustable noise threshold
        self.silence_threshold = 0.01  # Threshold for silence detection

         # Initialize other components
        self.setup_audio()
        self.setup_hand_tracking()
        self.setup_instruments()
        self.setup_effects()
        self.setup_utils()
        
        # self.note_mapper = NotePitchMapper()

        self.display_manager = DisplayManager(self)
        
        # Control state
        self.current_freq = 440.0  # A4 default
        self.current_volume = 0.0
        self.pitch_smooth_factor = 0.3
        self.last_pitch = None
        
        # Start recording when controller starts
        self.audio_saver.start_recording()

        # Start audio playback thread
        # self.start_playback_thread()
         
    def setup_audio(self):
        """Initialize audio output"""
        try:
            self.RATE = 44100
            self.CHUNK = 1024
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.RATE,
                input = False,
                output=True,
                frames_per_buffer=self.CHUNK
            )
            logger.info("Audio setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise

    def setup_hand_tracking(self):
        """Initialize MediaPipe hand tracking"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        logger.info("Hand tracking setup completed")

    def setup_instruments(self):
        """Initialize all instruments"""
        self.instruments = {
            'Plucked String': PluckedString.guitar_preset(self.RATE, self.CHUNK),# .guitar_preset
            'theremin': Theremin(self.RATE, self.CHUNK),
            'drums': Drums(self.RATE, self.CHUNK),
            'piano': Piano(self.RATE, self.CHUNK)
        }
        self.current_instrument = self.instruments['piano']
        self.current_mode = 'piano'
        

    def setup_effects(self):
        """Initialize audio effects"""
        self.delay = Delay(self.RATE, delay_time=0.3, feedback=0.3)
        self.reverb = Reverb(self.RATE, room_size=0.8, damping=0.5)

    def setup_utils(self):
        """Initialize audio utils, expecially the buffer"""
        self.buffer = AudioBuffer(self.RATE, self.CHUNK, self.duration)
        self.audio_saver = AudioSaver(sample_rate=self.RATE)
        self.noise_reduction = AudioNoiseReduction(self.noise_floor, self.silence_threshold)

    def process_hands(self, 
                     results,
                     frame_shape: Tuple[int, int]) -> Tuple[Optional[float], Optional[float]]:
        """Process detected hands and return pitch and volume controls"""
        if not results.multi_hand_landmarks:
            return None, None

        height, width = frame_shape[:2]
        left_hand = right_hand = None

        # Identify hands
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[hand_idx].classification[0].label
            if handedness == 'Left':
                left_hand = hand_landmarks
            else:
                right_hand = hand_landmarks

        pitch = volume = octave = None

        if self.current_mode != 'drums':
            # Get octave from left hand (3, 4, or 5)
            if left_hand:
                palm_y = left_hand.landmark[8].y
                # Map y position to octaves (3, 4, 5)
                if palm_y > 0.66:  # Bottom third
                    octave = 3
                elif palm_y > 0.33:  # Middle third
                    octave = 4
                else:  # Top third
                    octave = 5

        else:
            # Original drums mode processing
            if left_hand:
                palm_y = left_hand.landmark[8].y
                if palm_y < 0.25:
                    self.instruments['drums'].current_drum = 'hihat'
                elif palm_y < 0.5:
                    self.instruments['drums'].current_drum = 'snare'
                elif palm_y < 0.75:
                    self.instruments['drums'].current_drum = 'tom'
                else:
                    self.instruments['drums'].current_drum = 'kick'

        if octave == None:
            octave = 4

        # Get note from right hand
        if right_hand:
            palm_x = right_hand.landmark[8].x
            palm_y = right_hand.landmark[8].y
            if palm_x > 0.75:
                notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                note_idx = int(palm_y * len(notes))
                note_idx = max(0, min(note_idx, len(notes) - 1))
                note = notes[note_idx]
            else:
                note = None

        # Calculate frequency if both hands are detected
        if left_hand and right_hand:
            if note is not None:
                # Calculate MIDI note number
                base_c0 = 12  # MIDI note number for C0
                note_idx = notes.index(note)
                midi_note = base_c0 + note_idx + (octave * 12)
                
                # Convert MIDI note to frequency: f = 440 * 2^((n-69)/12)
                pitch = 440.0 * (2 ** ((midi_note - 69) / 12))
            else:
                pitch = None

        # Use left hand x position for volume
        if left_hand:
            palm_x = left_hand.landmark[8].x
            volume = min(1.0, max(0.0, palm_x))

        return pitch, volume

    def change_instrument(self, instrument_name):
        """Change the current instrument"""
        # Clear audio buffer when changing instruments
        if hasattr(self, 'buffer'):
            self.buffer.buffer.fill(0)
            self.buffer.write_position = 0
        if instrument_name in self.instruments:
            self.current_instrument = self.instruments[instrument_name]
            self.current_mode = instrument_name
            logger.info(f"Changed instrument to {instrument_name}")

    def cleanup(self):
        """Clean up resources and save audio"""
        logger.info("Saving the whole process...")
        if hasattr(self, 'audio_saver'):
            filepath = self.audio_saver.stop_recording()
            if filepath:
                logger.info("Session recording saved to: %s", filepath)
        logger.info("Cleaning up resources...")
        # if self.playback_thread and self.playback_thread.is_alive():
        #     self.playback_thread.join(timeout=1.0)

        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'p'):
            self.p.terminate()
        try:
            self.display_manager.root.destroy()
        except:
            pass

    def generate_audio(self, pitch, volume):
        """Generate audio based on pitch and volume"""
        audio = self.current_instrument.generate_sound(pitch, volume)

        if not (isinstance(self.current_instrument, PluckedString)):
            audio = AudioProcessor.process_audio(audio, self.RATE, attack=0.1, decay=0.1, cutoff_freq=5000)

        # Apply effects and comment it out if not works well
        # audio = self.delay.process(audio)
        # audio = self.reverb.process(audio)
        
        # Add to main buffer and get current chunk
        self.buffer.add_audio(audio)
        output_chunk = self.buffer.get_chunk(self.CHUNK)

        # Save audio chunk
        self.audio_saver.add_audio(output_chunk)
        
        # Play processed audio
        self.stream.write(output_chunk.tobytes(), self.CHUNK)

    def read_audio_buffer(self):
        """Read audio from buffer and play"""
        # Get next chunk from buffer
        output_chunk = self.buffer.get_chunk(self.CHUNK)
        
        # # If pitch is the same, just play the buffer
        self.stream.write(self.buffer.get_chunk(self.CHUNK).tobytes(), self.CHUNK)

        # Save audio chunk
        self.audio_saver.add_audio(output_chunk)

    def run(self):
        """Main application loop"""
        try:
            # Try to open secondary camera first
            cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                # If secondary camera fails, try primary camera
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    raise ValueError("No webcam available")
            
            logger.info("Camera initialized successfully")

            while self.display_manager.running:
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to get frame from camera")
                    break

                # Mirror frame for more intuitive control
                frame = cv2.flip(frame, 1)
                
                # Process frame for hand detection
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                # Process hand positions
                pitch, volume = self.process_hands(results, frame.shape)
                
                
                # Generate and play audio if hands are detected
                if pitch is not None and volume is not None:
                    # Key and discrete for Piano and Drums
                    if (pitch != self.last_pitch) and (self.last_pitch == None) and (isinstance(self.current_instrument, Piano) or isinstance(self.current_instrument, Drums)): 
                        # Generate sound
                        self.generate_audio(pitch, volume)

                    elif (pitch != self.last_pitch) and (isinstance(self.current_instrument, Theremin)):
                        self.generate_audio(pitch, volume)
                    
                    # Since for Plucked String, we use Karplus-Strong with buffer inside and pass to self.buffer
                    elif (isinstance(self.current_instrument, PluckedString)):
                        self.generate_audio(pitch, volume)

                    else:
                        self.read_audio_buffer()

                # Update display
                self.display_manager.update_frame(
                    frame, 
                    results, 
                    self.current_instrument,
                    self.current_mode,
                    pitch, 
                    volume,
                    self.last_pitch
                )

                self.last_pitch = pitch

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

        finally:
            cap.release()
            self.cleanup()
            cv2.destroyAllWindows()
            logger.info("End up!!!")