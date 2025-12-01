"""Sound manager."""

# -- Imports --

import sounddevice as sd
import soundfile as sf
import os
import threading


def play_footstep():
    """Play footstep sound effect when player walks."""
    data, fs = sf.read(
        f'{os.path.curdir}/sound_effects/footstep.wav',
        dtype="float32",
    )
    sd.play(data, fs)
