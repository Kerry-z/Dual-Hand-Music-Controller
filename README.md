# Dual-Hand Music Controller

A computer vision-based virtual instrument controller that lets you create music through hand gestures. This project uses hand tracking to transform your movements into musical expressions, providing an intuitive and interactive way to make music.

It is a final project about No-touch Video-based Musical Instrument for the course "Real-Time Digital Signal Processing Lab: ECE-GY 6183" at New York University, Tandon School of Engineering.

## Features

### 🎹 Multiple Synthesized Instruments

- **Piano**: Physical modeling synthesis with resonant filters
- **PluckedString**: Karplus-Strong algorithm for string simulation
- **Theremin**: Classic electronic instrument with vibrato
- **Drums**: Fully synthesized drum kit
- **Flute**: Wind instrument simulation (In development )
- **Synth**: Basic synthesizer with waveform options  (for the user to design their own instruments)

### 🎯 Gesture Control

- **Right Hand**: Controls pitch (note) selection (y-axis) and simulate the feeling of keys for piano and drums combined x-axis
- **Left Hand**: Controls volume (x-axis) and octave (y-axis)
- **Discrete Note Mapping**: Musical note quantization
- **Real-time Visual Feedback**: Hand tracking visualization
- **Clear visual guidance**: Hand position and note mapping indicators, volume visulization, instrument switch button and pitch regions

### 🎛️ Audio Effects

- **Delay**: Adjustable delay time and feedback
- **Reverb**: Room simulation with customizable parameters

## Project Structure

```tree
music_controller/
├── effects/                  # Audio effects
│   ├── __init__.py
│   ├── base_effect.py       # Base effect class
│   ├── delay.py             # Delay implementation
│   └── reverb.py            # Reverb implementation
├── instruments/             # Musical instruments
│   ├── __init__.py
│   ├── base_instrument.py   # Base instrument class
│   ├── drums.py            # Drum synthesis
│   ├── flute.py            # Flute synthesis
│   ├── piano.py            # Piano synthesis
│   ├── PluckedString.py    # String instrument
│   ├── synth.py            # Basic synthesizer
│   └── theremin.py         # Theremin implementation
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── test_effects.py
│   ├── test_instruments.py
│   └── test_utils.py
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── audio_buffer.py     # Audio buffering
│   ├── audio_multithread.py # Audio threading
│   ├── audio_noise_reduction.py  # Noise reduction
│   ├── audio_processing.py # Audio processing tools
│   ├── audio_save.py       # Recording functionality
│   └── note_utils.py       # Musical note mapping (not used)
├── visual/                  # Visual interface
│   ├── __init__.py
│   └── display_manager.py  # GUI and visualization
├── __init__.py
├── controller.py            # Main controller
││recordings/               # Recorded audio files
││main.py                 # START !!!
││requirements.txt        # Dependencies
││README.md            # Project description
││setup.py            # Setup script
```

## Requirements

### System Requirements

- Python 3.10+
- Webcam
- Audio output device

### Main Dependencies

```python
numpy
scipy
opencv-python
mediapipe
pyaudio
pillow
unittest
tk
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd music_controller
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Or I recommand to use `conda` to install dependencies:

```bash
conda create -n music_env python=3.10 -y
```

```bash
conda activate music_env
```

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Controls:
- Number keys to switch instruments:
  - 1: Piano
  - 2: PluckedString
  - 3: Theremin
  - 4: Drums
- Use right hand for note control
- Use left hand for volume and octave control
- 'q' to quit or directly close the window

3. Instrument controls:

- Piano:
  - Play notes by moving your right hand to specific note position. 
  - If you want to switch to another note, you need to move your hand to left three-quarters of the screen (Silent region) just like raising of the hand on the piano. 
  - And, use your left hand to control volume and octave.
- PluckedString:
  - Play notes by moving your right hand from top to bottom along the right quarter of the screen, similar to picking a string.
  - Also, use your left hand to control volume and octave.
- Theremin:
  - Play notes by moving your right hand from top to bottom along the right quarter of the screen.
  - Use your left hand to control volume just like playing the Theremin and choose specific octave using your left hand.
- Drums:
  - Play drums by moving your right hand to specific drum position.
  - Mimicking the tapping sensation, the movement is the same as the piano part above.
  - Use your left hand to control volume by moving left and right on the X-axis.
  - And moving your left hand up and down to select the type of drum.

## Audio Features

### Sound Synthesis
- Advanced physical modeling for piano and string instruments
- Real-time audio processing with buffer management
- Noise reduction capabilities (In development and testing)
- Audio recording and playback

### Effects Processing
- Customizable delay and reverb effects
- Real-time effect parameter control
- Audio buffer management for smooth playback

### Features and defects

prons:
- Real-time audio processing
- Various sound synthesis
- Customizable instrument settings
- **Gesture simulation is based on real instrument playing**
- Real-time effect parameter control
- **Modularization**
- **High scalability** and supports various personalization Settings.
- **Audio saving and playback**

cons:
- Some noises in the background
- The generated sound lacks authenticity and sounds unrealistic, and the sound is not as good as the real instrument.
- Better multithread method is still in process and the existing multithread is not very efficient and works poorly.
- The buffer is not that effective to update and track the current sound.
- ....

## Future Improvements

- [ ] **Eliminating the noises in the background during the real-time interaction**
- [ ] Additional instruments like flute
- [ ] More audio effects
- [ ] Enhanced visual feedback

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe team for hand tracking
- Scientific computing community
- Open source audio synthesis community
- DSP Lab course at New York University
