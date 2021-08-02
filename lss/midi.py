import mido


class HexMessage(mido.Message):
    """
    Example of documented message:

    Host => Launchpad Mini [MK3]:
    Hex: F0h 00h 20h 29h 02h 0Dh 00h 7Fh F7h
    Dec: 240 0 32 41 2 13 0 127 247

    Strips first and last control byte. Just copy paste the msg from
    Novation programming manual.
    """

    def __init__(self, msg: str):
        data = map(int, msg.split(" ")[1:-1])
        super().__init__("sysex", data=data)
