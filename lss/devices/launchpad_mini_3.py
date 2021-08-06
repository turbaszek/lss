from lss.devices.launchpad_base import BaseLaunchpad
from lss.midi import HexMessage


class LaunchpadMiniMk3(BaseLaunchpad):
    row_count = 9
    column_count = 9

    name = "Launchpad Mini MK3 LPMiniMK3 MIDI"

    def hand_shake(self):
        self._outport.send(HexMessage("240 0 32 41 2 13 0 127 247"))
        self._outport.send(HexMessage("2400 32 41 2 13 14 1 247"))
