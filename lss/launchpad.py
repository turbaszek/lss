import signal
import time
from contextlib import contextmanager
from functools import cached_property
from typing import Dict

import mido

from lss.drums import MiDIDrums
from lss.midi import HexMessage


class Color:
    GREEN = 87
    GREEN_DIMMED = 19
    PINK = 107


class FunctionPad:
    ARROW_UP = 91
    ARROW_DOWN = 92
    STOP = 19

    TEMPO_PADS = [ARROW_UP, ARROW_DOWN]


class Launchpad:
    ROW_TO_SOUND = {
        8: None,  # system functions
        7: MiDIDrums.KICK,
        6: MiDIDrums.SNARE,
        5: MiDIDrums.CLAP,
        4: MiDIDrums.HH_CLOSED,
        3: MiDIDrums.HH_OPEN,
        2: MiDIDrums.CRASH,
        1: MiDIDrums.TOM_MID,
        0: MiDIDrums.RIDE,
    }

    pads: Dict[int, "Pad"] = {}

    def __init__(self, name: str = "Launchpad Mini MK3 LPMiniMK3 MIDI"):
        self._outport = mido.open_output(name + " In", autoreset=True)
        self._inport = mido.open_input(name + " Out", autoreset=True)
        self.midi_outport = mido.open_output("Launchpad Step Sequencer", virtual=True, autoreset=True)

        # Set programmer mode
        self._outport.send(HexMessage("240 0 32 41 2 13 0 127 247"))
        self._outport.send(HexMessage("2400 32 41 2 13 14 1 247"))

        self._register_signal_handler()
        self._reset_all_pads()
        self._show_lss()

        self._is_stopped = True
        self._tempo = 120  # bpm

    def _register_signal_handler(self):
        def _sig_handler(signum, frame):
            self._reset_all_pads()
            self._inport.close()
            self._outport.close()

        signal.signal(signal.SIGINT, _sig_handler)
        signal.signal(signal.SIGTERM, _sig_handler)

    def _show_lss(self):
        pads = [61, 51, 41, 31, 32, 65, 54, 45, 34, 68, 57, 48, 37]
        for pad in pads:
            self.pads.get(pad).blink()
        time.sleep(1.5)
        self._reset_all_pads()

    def _sleep(self):
        time.sleep(60 / self._tempo)

    def on(self, note: int, color: int = 4):
        self._outport.send(mido.Message("note_on", note=note, velocity=color))

    def off(self, note: int):
        self._outport.send(mido.Message("note_off", note=note))

    def _reset_all_pads(self):
        self._all_pads = []
        for x in range(9):
            for y in range(9):
                pad = Pad(x, y, launchpad=self)
                pad.off()
                self.pads[pad.note] = pad

    def read_all_msgs(self):
        for msg in self._inport.iter_pending():
            self.process_msg(msg)

    def process_msg(self, msg: mido.Message):
        print(msg)

        # Handle control messages
        if hasattr(msg, "control"):
            if msg.value != 127:
                return

            if msg.control == FunctionPad.STOP:
                self._is_stopped = not self._is_stopped
                return

            if msg.control in FunctionPad.TEMPO_PADS:
                self.adjust_tempo(msg.control)

            # Last control column for muting
            if (msg.control - 9) % 10 == 0:
                self.mute(msg.control)
                return

        if self._is_stopped:
            # If sequencer is stopped then ignore none control messages
            return

        if hasattr(msg, "velocity") and hasattr(msg, "note"):
            if msg.velocity != 127:
                return

            pad = self.pads.get(msg.note)
            if pad:
                pad.click()
                return

    def send_message(self, note):
        self.midi_outport.send(mido.Message("note_on", note=note))
        self.midi_outport.send(mido.Message("note_off", note=note))

    def get_column(self, x: int):
        """Returns single column of pads, include functional buttons for better UX"""
        pads_ids = [Pad.get_note(x, y) for y in range(9)]
        return [self.pads.get(idx) for idx in pads_ids]

    def get_row(self, y: int):
        """Returns single row of pads, skips functional buttons"""
        pads_ids = [Pad.get_note(x, y) for x in range(8)]
        print(pads_ids)
        return [self.pads.get(idx) for idx in pads_ids]

    @contextmanager
    def column_on(self, x: int):
        pads = self.get_column(x)
        for p in pads:
            p.blink()
            if not self._is_stopped:
                p.play()

        yield

        for p in pads:
            p.unblink()

    def play(self):
        x = 0
        while True:
            with self.column_on(x):
                self.read_all_msgs()
                if self._is_stopped:
                    time.sleep(0.1)
                    continue
                self._sleep()

            x = (x + 1) % 8

    def mute(self, msg: int):
        y = int((msg - 9) / 10 - 1)
        for pad in self.get_row(y):
            pad.mute()

    def adjust_tempo(self, msg: int):
        if msg == FunctionPad.ARROW_DOWN:
            self._tempo -= 5
        if msg == FunctionPad.ARROW_UP:
            self._tempo += 5


class Pad:
    """
    Represents one of 81 pads.

    Pad is defined by (x, y) pair which strictly corresponds with note
    assigned to the pad.

    Note map:

    91 | 92 | 93 | 94 | 95 | 96 | 97 | 98 || 99
    ===========================================
    81 | 82 | 83 | 84 | 85 | 86 | 87 | 88 || 89
    71 | 72 | 73 | 74 | 75 | 76 | 77 | 78 || 79
    61 | 62 | 63 | 64 | 65 | 66 | 67 | 68 || 69
    51 | 52 | 53 | 54 | 55 | 56 | 57 | 58 || 59
    41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 || 49
    31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 || 39
    21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 || 29
    11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 || 19
    """

    def __init__(self, x: int, y: int, launchpad):
        assert 0 <= x < 9, f"x has to be between 0 and 9, got {x}"
        assert 0 <= y < 9, f"y has to be between 0 and 9, got {y}"

        self._launchpad = launchpad
        self.x = x
        self.y = y
        self._is_on = False
        self._muted = False
        self._sound = Launchpad.ROW_TO_SOUND[y]

    @staticmethod
    def get_note(x: int, y: int) -> int:
        return 10 * (y + 1) + x + 1

    @cached_property
    def note(self) -> int:
        return self.get_note(self.x, self.y)

    def on(self, color: int) -> None:
        self._launchpad.on(self.note, color)

    def off(self) -> None:
        self._launchpad.off(self.note)

    def _set_active_color(self) -> None:
        if self._is_on:
            if self._muted:
                self.on(Color.GREEN_DIMMED)
            else:
                self.on(Color.GREEN)
        else:
            self._launchpad.off(self.note)

    def blink(self) -> None:
        if not self._is_on:
            self.on(Color.PINK)

    def unblink(self) -> None:
        self._set_active_color()

    def mute(self) -> None:
        self._muted = not self._muted
        self._set_active_color()

    def play(self) -> None:
        if self._is_on and not self._muted:
            print(f"playing {self._sound}")
            self._launchpad.send_message(self._sound.value)

    def click(self) -> None:
        self._is_on = not self._is_on
        self._set_active_color()
