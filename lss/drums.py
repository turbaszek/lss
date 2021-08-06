from enum import Enum


class MiDIDrums(Enum):
    KICK = 36
    RIM = 37
    SNARE = 38
    CLAP = 39
    HH_CLOSED = 42
    TOM_MID = 43
    HH_OPEN = 44
    CRASH = 49
    RIDE = 51

    @classmethod
    def get_sound(cls, row: int):
        sound_map = {
            8: None,  # system functions
            7: cls.KICK,
            6: cls.SNARE,
            5: cls.CLAP,
            4: cls.HH_CLOSED,
            3: cls.HH_OPEN,
            2: cls.CRASH,
            1: cls.TOM_MID,
            0: cls.RIDE,
        }
        return sound_map[row]
