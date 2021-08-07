from functools import cached_property

from lss.drums import MiDIDrums
from lss.utils import Color


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
        self._sound = MiDIDrums.get_sound(self.y)

    def __repr__(self):
        return f"Pad({self.x}, {self.y}, note={self.note})"

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

    async def unblink(self) -> None:
        self._set_active_color()

    def mute(self) -> None:
        self._muted = not self._muted
        self._set_active_color()

    def click(self) -> None:
        self._is_on = not self._is_on
        self._set_active_color()

    async def process_pad(self, is_stopped: bool, callback) -> None:
        self.blink()
        if not is_stopped and self._is_on and not self._muted:
            callback(self._sound.value)
