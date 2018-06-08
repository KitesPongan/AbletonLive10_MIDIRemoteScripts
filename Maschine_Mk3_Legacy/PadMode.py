# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\PadMode.py
# Compiled at: 2017-08-10 18:34:01
import Live
from PadScale import *
from MaschineMode import MaschineMode
from MidiMap import *
from Constants import *
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from _Framework.SliderElement import SliderElement

class PadMode(MaschineMode):
    _focus_track = None
    _editmode = None
    _in_edit_mode = False

    def __init__(self, monochrome=False, *a, **k):
        super(PadMode, self).__init__(*a, **k)
        self._note_display_mode = ND_KEYBOARD1
        self.current_scale_index = 0
        self._scale = None
        self._base_note = 0
        self._octave = 0.55
        self.current_scale_index = 0
        self._is_monochrome = monochrome
        self._color_edit_assign = monochrome and self.assign_edit_mono or self.assign_edit_color
        self.assign_transpose(SCALES[self.current_scale_index])
        self._seg_display = None
        return

    def set_edit_mode(self, editmode):
        self._editmode = editmode

    def update_selected_track(self):
        self._focus_track = self.song().view.selected_track
        self.refresh()

    def set_segment_display(self, displayer):
        self._seg_display = displayer

    def get_color(self, value, column, row):
        button = self.canonical_parent._bmatrix.get_button(column, row)
        if button != None:
            midi_note = button.get_identifier()
            on = value != 0
            return self.get_color_by_note_mode(midi_note, on)
        return

    def _get_ref_color(self):
        if self._focus_track:
            return toHSB(self._focus_track.color)
        return (75, 70)

    def get_color_by_note_mode(self, midi_note, on):
        oncolor, offcolor = self._get_ref_color()
        return on and oncolor or offcolor

    def step_key_color_mode(self):
        if self._active:
            self.assign_transpose(SCALES[self.current_scale_index])

    def update_text_display(self):
        self.text_current_scale()

    def navigate(self, direction, modifier, alt_modifier=False):
        if modifier:
            self.inc_scale(direction)
        else:
            if alt_modifier:
                self.inc_base_note(direction)
            else:
                self.inc_octave(direction)

    @subject_slot('value')
    def _adjust_scale(self, value):
        self.inc_scale(value == REL_KNOB_DOWN and -1 or 1)

    @subject_slot('value')
    def _adjust_octav(self, value):
        self.inc_octave(value == REL_KNOB_DOWN and -1 or 1)

    @subject_slot('value')
    def _adjust_basem(self, value):
        self.inc_base_note(value == REL_KNOB_DOWN and -1 or 1)

    @subject_slot('value')
    def _do_oct_up(self, value):
        if value != 0:
            self.inc_octave(1)

    @subject_slot('value')
    def _do_oct_down(self, value):
        if value != 0:
            self.inc_octave(-1)

    @subject_slot('value')
    def _do_base_up(self, value):
        if value != 0:
            self.inc_base_note(1)

    @subject_slot('value')
    def _do_base_down(self, value):
        if value != 0:
            self.inc_base_note(-1)

    @subject_slot('value')
    def _do_scale_up(self, value):
        if value != 0:
            self.inc_scale(1)

    @subject_slot('value')
    def _do_scale_down(self, value):
        if value != 0:
            self.inc_scale(-1)

    def get_mode_id(self):
        return PAD_MODE

    def text_current_scale(self):
        scale = SCALES[self.current_scale_index]
        text = scale.name + ' ' + BASE_NOTE[self._base_note] + str(scale.to_octave(self._octave) - 2)
        self.canonical_parent.timed_display(text, 2)

    def inc_base_note(self, inc):
        prev_value = self._base_note
        self._base_note = min(11, max(0, self._base_note + inc))
        if prev_value != self._base_note:
            scale = SCALES[self.current_scale_index]
            self.canonical_parent.show_message(' Base Note ' + BASE_NOTE[self._base_note] + ' to ' + scale.name)
            self.text_current_scale()
            self.update_transpose()

    def inc_scale(self, inc):
        nr_of_scales = len(SCALES) - 1
        prev_value = self.current_scale_index
        self.current_scale_index = min(nr_of_scales, max(0, self.current_scale_index + inc))
        if prev_value != self.current_scale_index:
            newscale = SCALES[self.current_scale_index]
            self.canonical_parent.show_message(' PAD Scale ' + newscale.name + ' ' + BASE_NOTE[self._base_note] + str(newscale.to_octave(self._octave) - 2))
            self.text_current_scale()
            self.update_transpose()

    def inc_octave(self, inc):
        scale = SCALES[self.current_scale_index]
        octave = scale.to_octave(self._octave)
        newoctave = octave + inc
        if newoctave < 0:
            newoctave = 0
        else:
            if newoctave > scale.octave_range:
                newoctave = scale.octave_range
        self._octave = scale.to_relative(newoctave, self._octave)
        scale = SCALES[self.current_scale_index]
        self.canonical_parent.show_message(' OCTAVE ' + BASE_NOTE[self._base_note] + str(newoctave - 2) + ' to ' + scale.name)
        self.text_current_scale()
        self.update_transpose()
        if self._seg_display:
            val = newoctave - 2
            if val < 0:
                val = 100 + abs(val)
            self._seg_display.timed_segment(val)

    def get_octave(self):
        return SCALES[self.current_scale_index].to_octave(self._octave)

    def update_transpose(self):
        if self._active:
            self.assign_transpose(SCALES[self.current_scale_index])
            self.canonical_parent._set_suppress_rebuild_requests(True)
            self.canonical_parent.request_rebuild_midi_map()
            self.canonical_parent._set_suppress_rebuild_requests(False)

    def refresh(self):
        if self._active:
            scale_len = len(self._scale.notevalues)
            octave = self._scale.to_octave(self._octave)
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    note_index = (3 - row) * 4 + column
                    scale_index = note_index % scale_len
                    octave_offset = note_index / scale_len
                    note_value = self._scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                    button.reset()
                    button.send_color_direct(self.get_color_by_note_mode(note_value, note_value % 12 == self._base_note))

    def assign_edit_color(self, in_notes, button, note_value):
        if in_notes:
            if note_value in in_notes:
                button.send_color_direct(self.get_color_by_note_mode(note_value, True))
            else:
                button.send_color_direct(self.get_color_by_note_mode(note_value, False))
        else:
            button.send_color_direct(self.get_color_by_note_mode(note_value, False))

    def assign_edit_mono(self, in_notes, button, note_value):
        if in_notes:
            if note_value in in_notes:
                button.send_value(127, True)
            else:
                button.send_value(0, True)
        else:
            button.send_value(0, True)

    def get_in_notes(self):
        cs = self.song().view.highlighted_clip_slot
        if cs.has_clip and cs.clip.is_midi_clip:
            in_notes = set()
            notes = cs.clip.get_notes(0.0, 0, cs.clip.length, 127)
            for note in notes:
                in_notes.add(note[0])

            return in_notes
        return

    def assign_transpose(self, scale):
        assert isinstance(scale, PadScale)
        self._scale = scale
        scale_len = len(scale.notevalues)
        octave = scale.to_octave(self._octave)
        last_note_val = None
        if self._active:
            in_notes = self._in_edit_mode and self.get_in_notes() or None
            for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
                if button:
                    note_index = (3 - row) * 4 + column
                    scale_index = note_index % scale_len
                    octave_offset = note_index / scale_len
                    note_value = scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                    if note_value < 128:
                        last_note_val = note_value
                    else:
                        if last_note_val != None:
                            note_value = last_note_val
                    button.set_send_note(note_value)
                    if self._in_edit_mode:
                        self._color_edit_assign(in_notes, button, note_value)
                    else:
                        button.send_color_direct(self.get_color_by_note_mode(note_value, note_value % 12 == self._base_note))
                    self.canonical_parent._forwarding_registry[(MIDI_NOTE_ON_STATUS, button.get_identifier())] = button
                    self.canonical_parent._forwarding_registry[(MIDI_NOTE_OFF_STATUS, button.get_identifier())] = button

        return

    def handle_shift(self, shift_value):
        if shift_value:
            for button, (_, _) in self.canonical_parent.get_button_matrix().iterbuttons():
                if button:
                    button.set_to_notemode(False)
                    button.add_value_listener(self.handle_shift_button, True)

        else:
            for button, (_, _) in self.canonical_parent.get_button_matrix().iterbuttons():
                if button:
                    button.remove_value_listener(self.handle_shift_button)

            self.update_transpose()

    def handle_shift_button(self, value, button):
        if value != 0:
            col, row = button.get_position()
            self.canonical_parent.handle_edit_action((col, row))

    def auto_select(self):
        return True

    @subject_slot('notes')
    def _on_notes_changed(self):
        if self._in_edit_mode:
            in_notes = self.get_in_notes()
            if in_notes:
                for button, (_, _) in self.canonical_parent._bmatrix.iterbuttons():
                    if button:
                        if button._msg_identifier in in_notes:
                            button.send_value(127, True)
                        else:
                            button.send_value(0, True)

            else:
                for button, (_, _) in self.canonical_parent._bmatrix.iterbuttons():
                    button.send_value(0, True)

    def enter_clear_state(self):
        self._in_edit_mode = True
        cs = self.song().view.highlighted_clip_slot
        in_notes = set()
        if cs != None and cs.has_clip and cs.clip.is_midi_clip:
            clip = cs.clip
            notes = clip.get_notes(0.0, 0, clip.length, 127)
            self._on_notes_changed.subject = clip
            for note in notes:
                in_notes.add(note[0])

        else:
            self._on_notes_changed.subject = None
        for button, (_, _) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                if button._msg_identifier in in_notes:
                    button.send_value(127, True)
                else:
                    button.send_value(0, True)
                button.set_to_notemode(False)
                button.add_value_listener(self._action_clear, True)

        return

    def exit_clear_state(self):
        self._in_edit_mode = False
        self._on_notes_changed.subject = None
        scale_len = len(self._scale.notevalues)
        octave = self._scale.to_octave(self._octave)
        for button, (column, row) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                note_index = (3 - row) * 4 + column
                scale_index = note_index % scale_len
                octave_offset = note_index / scale_len
                button.send_value(0, True)
                note_value = self._scale.notevalues[scale_index] + self._base_note + octave * 12 + octave_offset * 12
                button.send_color_direct(self.get_color_by_note_mode(note_value, note_value % 12 == self._base_note))
                button.set_to_notemode(True)
                button.remove_value_listener(self._action_clear)

        return

    def _action_clear(self, value, button):
        if value != 0:
            self._editmode.edit_note(button._msg_identifier)

    def update_color(self):
        self.refresh()

    def enter(self):
        self._active = True
        self._focus_track = self.song().view.selected_track
        for button, (_, _) in self.canonical_parent._bmatrix.iterbuttons():
            if button:
                button.send_value(0, True)
                button.set_to_notemode(True)
                self.canonical_parent._forwarding_registry[(MIDI_NOTE_ON_STATUS, button.get_identifier())] = button
                self.canonical_parent._forwarding_registry[(MIDI_NOTE_OFF_STATUS, button.get_identifier())] = button

        self.update_transpose()

    def exit(self):
        self._active = False
