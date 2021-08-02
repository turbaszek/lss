import atexit
import time
from contextlib import contextmanager
from typing import List

import mido

from lss.drums import MiDIDrums
from lss.midi import HexMessage


class Launchpad:
    ROW_TO_SOUND = {
        8: None,
        7: MiDIDrums.KICK,
        6: MiDIDrums.SNARE,
        5: MiDIDrums.CLAP,
        4: MiDIDrums.HH_CLOSED,
        3: MiDIDrums.HH_OPEN,
        2: MiDIDrums.CRASH,
        1: MiDIDrums.TOM_MID,
        0: MiDIDrums.RIM,
    }

    def __init__(self, name: str = "Launchpad Mini MK3 LPMiniMK3 MIDI"):
        self._outport = mido.open_output(name + " In", autoreset=True)
        self._inport = mido.open_input(name + " Out", autoreset=True)
        self.midi_outport = mido.open_output("PadSequencer", virtual=True, autoreset=True)
        # Set programmer mode
        self._outport.send(HexMessage("240 0 32 41 2 13 0 127 247"))
        self._outport.send(HexMessage("2400 32 41 2 13 14 1 247"))

        self._register_signal_handler()
        self._reset_all_pads()

        self._is_stopped = False

    def _register_signal_handler(self):
        def _sig_handler():
            self._reset_all_pads()
            self._inport.close()
            self._outport.close()

        atexit.register(_sig_handler)

    def new_pad(self, x: int, y: int):
        return Pad(x, y, launchpad=self)

    def on(self, note: int, color: int = 4):
        self._outport.send(mido.Message("note_on", note=note, velocity=color))

    def off(self, note: int):
        self._outport.send(mido.Message("note_off", note=note))

    def _reset_all_pads(self):
        self._all_pads = []
        for x in range(9):
            for y in range(9):
                pad = self.new_pad(x, y)
                pad.off(final=True)
                self._all_pads.append(pad)

    @property
    def pads(self) -> List["Pad"]:
        return self._all_pads

    def read_all_msgs(self):
        for msg in self._inport.iter_pending():
            self.process_msg(msg)

    def process_msg(self, msg: mido.Message):
        print(msg)

        # Handle control messages
        if hasattr(msg, "control"):
            if msg.value != 127:
                return

            if msg.control == 19:
                self._is_stopped = not self._is_stopped
                return
            if (msg.control - 9) % 10 == 0:
                # Last control column
                self.mute(msg.control)
                return

        if self._is_stopped:
            # If sequencer is stopped then ignore none control messages
            return

        if hasattr(msg, "velocity") and hasattr(msg, "note"):
            if msg.velocity != 127:
                return

            for pad in self.pads:
                if pad.note == msg.note:
                    pad.click()
                    return

    def send_message(self, note):
        self.midi_outport.send(mido.Message("note_on", note=note))
        self.midi_outport.send(mido.Message("note_off", note=note))

    @contextmanager
    def column_on(self, x: int):
        pads = [p for p in self.pads if p.x == x and p.y < 8]
        for p in pads:
            p.on()
            if not self._is_stopped:
                p.play()

        yield

        for p in pads:
            p.off()

    def play(self):
        x = 0
        tempo = 0.5
        while True:
            with self.column_on(x):
                self.read_all_msgs()
                if self._is_stopped:
                    time.sleep(0.1)
                    continue
                time.sleep(tempo)

            x = (x + 1) % 8

    def mute(self, msg: int):
        y = (msg - 9) / 10 - 1
        for pad in self._all_pads:
            if pad.y == y:
                pad.mute()


class Pad:
    COLOR_ON = 107
    COLOR_CLICKED = 87
    COLOR_MUTED = 19

    def __init__(self, x: int, y: int, launchpad: Launchpad = None):
        assert 0 <= x < 9, f"x has to be between 0 and 9, got {x}"
        assert 0 <= y < 9, f"y has to be between 0 and 9, got {y}"

        self._launchpad = launchpad
        self.note = 10 * (y + 1) + x + 1
        self.x = x
        self.y = y
        self._is_on = False
        self._muted = False
        self._sound = Launchpad.ROW_TO_SOUND[y]

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def get_color(self):
        if self._is_on:
            if self._muted:
                return self.COLOR_MUTED
            return self.COLOR_CLICKED
        return self.COLOR_ON

    def on(self):
        color = self.get_color()
        self._launchpad.on(self.note, color)

    def off(self, final: bool = False):
        """
        Turn the pad off

        :param final: does not fallbacks to previous color
        """
        self._launchpad.off(self.note)
        if not final and self._is_on:
            self.on()

    def mute(self):
        self._muted = not self._muted
        if self._is_on:
            self.on()

    def play(self):
        if self._is_on and not self._muted:
            print(f"Playing {self._sound}")
            self._launchpad.send_message(self._sound.value)

    def click(self):
        self._is_on = not self._is_on
        if not self._is_on:
            self.off(final=True)
        else:
            self.on()
