# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/mixer_utils.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
import Live

def is_set_to_split_stereo(mixer):
    modes = Live.MixerDevice.MixerDevice.panning_modes
    return modes.stereo_split == getattr(mixer, 'panning_mode', modes.stereo)


def has_pan_mode(mixer):
    return hasattr(mixer, 'panning_mode')
