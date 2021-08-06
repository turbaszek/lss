import asyncio
import time
from typing import Iterable

import mido

from lss.midi import ControlMessage, NoteMessage
from lss.utils import FunctionPad, open_output, register_signal_handler


class Sequencer:
    def __init__(self, launchpad):
        # Create virtual MiDI device where sequencer sends signals
        self.midi_outport = open_output("Launchpad Step Sequencer", virtual=True, autoreset=True)
        register_signal_handler(self._sig_handler)

        # Setup launchpad
        self.launchpad = launchpad
        self.launchpad.hand_shake()
        self._show_lss()

        # Sequencer state and control
        self._is_stopped = True
        self._tempo = 120  # bpm

    def _sig_handler(self, signum, frame):
        self.midi_outport.close()

    def _show_lss(self) -> None:
        """Show LSS when starting sequencer"""
        pads = [61, 51, 41, 31, 32, 65, 54, 45, 34, 68, 57, 48, 37]
        for pad in pads:
            self.launchpad.get_pad(pad).blink()
        time.sleep(1.5)
        self.launchpad.reset_all_pads()

    async def _sleep(self) -> None:
        await asyncio.sleep(60 / self._tempo)

    def on(self, note: int, color: int = 4) -> None:
        self.launchpad.on(note, color)

    def off(self, note: int) -> None:
        self.launchpad.off(note)

    async def _process_msg(self, msg) -> None:
        print(msg)
        if ControlMessage.is_control(msg):
            self._process_control_message(msg)
            return

        if NoteMessage.is_note(msg):
            self._process_pad_message(msg)
            return

    def _process_control_message(self, msg: ControlMessage) -> None:
        if msg.value != 127:
            return

        if msg.control == FunctionPad.STOP:
            self._is_stopped = not self._is_stopped
            return

        if msg.control in FunctionPad.TEMPO_PADS:
            self.adjust_tempo(msg.control)
            return

            # Last control column for muting
        if (msg.control - 9) % 10 == 0:
            self._mute(msg.control)
            return

    def _process_pad_message(self, msg: NoteMessage) -> None:
        if msg.velocity != 127:
            return

        pad = self.launchpad.get_pad(msg.note)
        if pad:
            pad.click()
            return

    def _mute(self, msg: int) -> None:
        """All pads in last right column are used to mute corresponding row"""
        y = int((msg - 9) / 10 - 1)
        for pad in self.launchpad.get_pads_in_row(y):
            pad.mute()

    def adjust_tempo(self, msg: int) -> None:
        if msg == FunctionPad.ARROW_DOWN:
            self._tempo -= 5
        elif msg == FunctionPad.ARROW_UP:
            self._tempo += 5

    def send_message(self, note) -> None:
        """Send note to virtual MiDI device"""
        self.midi_outport.send(mido.Message("note_on", note=note))
        self.midi_outport.send(mido.Message("note_off", note=note))

    async def _process_column(self, column: int):
        pads = self.launchpad.get_pads_in_column(column)
        await asyncio.gather(*[p.process_pad(self._is_stopped, self.send_message) for p in pads])
        await self._sleep()
        await asyncio.gather(*[p.unblink() for p in pads])

    async def _process_signals(self) -> None:
        while True:
            await asyncio.gather(*[self._process_msg(m) for m in self.launchpad.get_pending_messages()])
            await asyncio.sleep(0.001)

    def column_iterator(self) -> Iterable[int]:
        column = 0
        while True:
            yield column
            column = (column + 1) % 8 if not self._is_stopped else column
            time.sleep(0.001)

    async def run(self) -> None:
        asyncio.get_event_loop().create_task(self._process_signals())
        for column in self.column_iterator():
            await self._process_column(column)
