# instruments/__init__.py
from .base_instrument import BaseInstrument
from .piano import Piano
from .PluckedString import PluckedString
from .theremin import Theremin
from .drums import Drums
from .synth import Synthesizer
from .flute import Flute

__all__ = [
    'BaseInstrument',
    'Piano',
    'PluckedString',
    'Theremin',
    'Drums',
    'Synthesizer',
    'Flute'
]