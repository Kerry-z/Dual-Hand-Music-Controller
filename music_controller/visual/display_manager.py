# music_controller/visual/display_manager.py
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from typing import Callable, Optional, Tuple

from music_controller import controller

class DisplayManager:
    def __init__(self, controller):
        # Initialize Tkinter root window first
        self.root = tk.Tk()
        self.root.title("Enhanced Music Controller")
        self.controller = controller  # Store reference to controller
        
        # Initialize other components after root window
        self.setup_note_mapping()
        self.setup_gui()
        
        # Ensure window is ready
        self.root.update()
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.running = True
        
        # Bind 'q' key to quit
        self.root.bind('<q>', self.on_quit)
        
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.quit()
        
    def on_quit(self, event):
        """Handle 'q' key press"""
        self.running = False
        self.root.quit()
        
    def setup_gui(self):
        """Setup GUI components"""

        # Create instrument buttons
        self.create_instrument_buttons()
        # Information display
        self.create_info_frame()

        # Main display area
        self.video_frame = tk.Frame(self.root)
        self.video_frame.pack(expand=True, fill='both')
        
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(expand=True)
        
        # Instructions
        instruction_text = ("Press 1:Piano 2:Plucked String 3:Theremin 4:Drums\n" + 
                          "| Right hand: Pitch (Note) control |\n" + 
                           "| Left hand: x-axis for Volume control and y-axis for Pitch (Octave) control |")
        self.instruction_label = tk.Label(
            self.root,
            text=instruction_text,
            font=("Arial", 12),
            fg='gray'
        )
        self.instruction_label.pack(pady=5)
        
        # Initial update to ensure all widgets are ready
        self.root.update_idletasks()
        
    def setup_note_mapping(self):
        """Setup note frequency mapping"""
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.base_freq = 440.0  # A4
        
    def create_info_frame(self):
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill='x', pady=10)
        
        # Current instrument label
        self.instrument_label = tk.Label(
            self.info_frame,
            text="Piano",
            font=("Arial", 24),
            fg='purple'
        )
        self.instrument_label.pack(side='left', padx=20)
        
        # Note label
        self.note_label = tk.Label(
            self.info_frame,
            text="♪ --",
            font=("Arial", 24),
            fg='blue'
        )
        self.note_label.pack(side='left', padx=20)
        
        # Volume meter
        self.volume_meter = tk.Canvas(
            self.info_frame,
            width=200,
            height=30,
            bg='black'
        )
        self.volume_meter.pack(side='right', padx=20)

    def update_frame(self, frame: np.ndarray, hand_results, current_instrument, current_mode, pitch: Optional[float], volume: Optional[float], last_pitch: Optional[float] = None):
        """Update the display with the current frame and control information"""
        # Draw hand landmarks if available
        if hand_results and hand_results.multi_hand_landmarks:
            for landmarks in hand_results.multi_hand_landmarks:
                self.draw_hand_landmarks(frame, landmarks)
                
        # Draw control guides
        self.draw_control_guides(frame, current_instrument, current_mode)
        
       # Only update display and play sound if pitch has changed
        if pitch != last_pitch:
            self.update_gui_elements(frame, pitch, volume, current_instrument, current_mode)
        else:
            # Update frame without changing audio
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.root.update()
        
    def draw_hand_landmarks(self, frame: np.ndarray, landmarks):
        """Draw hand landmarks with enhanced visualization"""
        height, width = frame.shape[:2]
        # for landmark in landmarks.landmark:
        #     # Convert normalized coordinates to pixel coordinates
        #     x = int(landmark.x * width)
        #     y = int(landmark.y * height)
        #     cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        # Index finger landmarks (MediaPipe hand landmarks 5-8)
        index_finger_indices = [5, 6, 7, 8]  # Index finger landmarks
        
        # Draw connections for index finger
        for i in range(len(index_finger_indices) - 1):
            current_landmark = landmarks.landmark[index_finger_indices[i]]
            next_landmark = landmarks.landmark[index_finger_indices[i + 1]]
            
            # Convert normalized coordinates to pixel coordinates
            current_x = int(current_landmark.x * width)
            current_y = int(current_landmark.y * height)
            next_x = int(next_landmark.x * width)
            next_y = int(next_landmark.y * height)
            
            # Draw line connecting landmarks
            cv2.line(frame, (current_x, current_y), (next_x, next_y), 
                    (0, 255, 0), 2)
            
            # Draw points at landmark positions
            cv2.circle(frame, (current_x, current_y), 5, (0, 0, 255), -1)
        
        # Draw the tip of index finger with a different color
        tip_landmark = landmarks.landmark[8]  # Index fingertip
        tip_x = int(tip_landmark.x * width)
        tip_y = int(tip_landmark.y * height)
        cv2.circle(frame, (tip_x, tip_y), 8, (255, 0, 0), -1)

    def draw_control_guides(self, frame: np.ndarray, current_instrument, current_mode):
        """Draw instrument-specific control guides"""
        height, width = frame.shape[:2]

        # Draw volume guide
        for i in range(5):
            x = int(width * i / 4)
            cv2.line(frame, (x, 0), (x, height), (0, 255, 0), 1)
            cv2.putText(frame, f"{i*25}%", (x+5, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw note positions on the right
            note_height = height / len(self.notes)

        for i, note in enumerate(self.notes):
                y = int(i * note_height)
                # Draw horizontal separator lines
                cv2.line(frame, (width - width//6, y), (width, y), (0, 255, 0), 1)
                # Draw note names
                cv2.putText(frame, note, (width - 50, int(y + note_height/2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        cv2.putText(frame, "Right hand: Note", (width - 150, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if current_mode != 'drums':
            # Draw octave zones on the left
            octaves = ['5', '4', '3']
            section_height = height / 3
            for i, octave in enumerate(octaves):
                y = int(i * section_height)
                # Draw horizontal separator lines
                cv2.line(frame, (0, y), (width//4, y), (0, 255, 0), 1)
                # Draw octave number
                cv2.putText(frame, f"Octave {octave}", (10, int(y + section_height/2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw instructions
            cv2.putText(frame, "Left hand: Octave", (10, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        else:
            # Original drums visualization
            self.draw_drum_regions(frame, current_instrument, current_mode)

    def draw_drum_regions(self, frame: np.ndarray, current_instrument, current_mode):
        """Draw drum type regions on the left side"""
        height, width = frame.shape[:2]
        
        # Define drum regions
        drum_regions = ['hihat', 'snare', 'tom', 'kick']
        region_height = height / len(drum_regions)
        
        # Draw region separators and labels
        for i, drum in enumerate(drum_regions):
            # Calculate y position for this drum region
            y = int((i + 0.5) * region_height)
            
            # Draw horizontal separator lines
            y_line = int(i * region_height)
            cv2.line(frame, (0, y_line), (width//3, y_line), (0, 255, 0), 1)
            
            # Determine if this is the current drum
            is_current = drum == getattr(current_instrument, 'current_drum', None)
            
            # Set text color and thickness based on selection
            color = (255, 0, 0) if is_current else (0, 255, 0)  # Red if selected, green otherwise
            thickness = 2 if is_current else 1
            
            # Draw drum name
            cv2.putText(frame, drum.upper(), (10, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    color, thickness)
            
            # Draw selection indicator
            if is_current:
                # Draw an arrow or marker
                arrow_start = (width//4, y)
                arrow_end = (width//4 - 20, y)
                cv2.arrowedLine(frame, arrow_start, arrow_end, color, thickness)
                
            # Add hit zone indicator
            zone_text = f"Hit Zone {i+1}"
            cv2.putText(frame, zone_text, (width//4 + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw final separator line
        cv2.line(frame, (0, height-1), (width//3, height-1), (0, 255, 0), 1)
        
        # Add instructions
        instructions = "Use left hand Y position to select drum"
        cv2.putText(frame, instructions, (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    def update_gui_elements(self, frame: np.ndarray, pitch: Optional[float], volume: Optional[float], current_instrument, current_mode):
        """Update all GUI elements with current state"""
        # Convert frame for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        # Update volume meter
        if volume is not None:
            self.update_volume_meter(volume)
            
        # Update note display
        if pitch is not None:
            self.update_note_display(pitch, current_instrument, current_mode)
            
        self.root.update()

    def update_volume_meter(self, volume: float):
        """Update volume meter with smooth gradient"""
        self.volume_meter.delete('all')
        width = int(volume * 200)
        for i in range(width):
            intensity = i / 200
            r = int(255 * intensity)
            b = int(255 * (1 - intensity))
            color = f'#{r:02x}00{b:02x}'
            self.volume_meter.create_line(i, 0, i, 30, fill=color)

    def update_note_display(self, pitch: float, current_instrument, current_mode):
        """Update the note display with current pitch information"""
        if current_mode != "drums":
            if pitch <= 0: 
                note = "--"
            else:
                 # Convert frequency to MIDI note number relative to A4 (69)
                midi_note = 12 * np.log2(pitch/440.0) + 69
                
                # Calculate octave and note
                octave = (int(midi_note) - 12) // 12
                note_idx = int(midi_note) % 12
                
                # Adjust note index to match our note list
                note_idx = (note_idx) % 12
                # note = self.notes[note_idx] + str(octave)
                # Only update if the note has changed
                current_note = self.note_label.cget("text").split()[-1]
                new_note = f"{self.notes[note_idx]}{octave}"
                
                if current_note != new_note:
                    self.note_label.config(text=f"♪ {new_note}")
        else:
            # self.note_label.config(text=f"🥁 {getattr(current_instrument, 'current_drum', None)}")
            current_drum = getattr(current_instrument, 'current_drum', None)
            if self.note_label.cget("text") != f"🥁 {current_drum}":
                self.note_label.config(text=f"🥁 {current_drum}")

    def create_instrument_buttons(self):
        """Create buttons for instrument selection"""
        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill='x', padx=10, pady=5)
        
        # Define instruments with their display names and keyboard shortcuts
        instruments = [
            ('Piano (1)', 'piano', '1'),
            ('Plucked String (2)', 'Plucked String', '2'),
            ('Theremin (3)', 'theremin', '3'),
            ('Drums (4)', 'drums', '4')
        ]
        
        # Create button for each instrument
        style = {
            'width': 15,
            'bg': '#2C3E50',
            'fg': 'white',
            'relief': tk.RAISED,
            'font': ('Arial', 10, 'bold'),
            'pady': 5
        }
        
        for display_name, instrument_name, key in instruments:
            btn = tk.Button(
                self.button_frame,
                text=display_name,
                command=lambda name=instrument_name: self.on_instrument_change(name),
                **style
            )
            btn.pack(side='left', padx=5)
            
            # Bind keyboard shortcuts
            self.root.bind(key, lambda event, name=instrument_name: self.on_instrument_change(name))

    def on_instrument_change(self, instrument_name: str):
        """Handle instrument change events"""
        # Update current instrument
        self.controller.change_instrument(instrument_name)
        
        # Update instrument label
        self.instrument_label.config(text=instrument_name.title())
        
        # Clear note display when switching to drums
        if instrument_name == 'drums':
            self.note_label.config(text="🥁")
        else:
            self.note_label.config(text="♪ --")