import os
import signal
import sys

import mido
from loguru import logger


def register_signal_handler(func) -> None:
    signals = {signal.SIGINT, signal.SIGTERM}
    for sig in signals:
        signal.signal(sig, func)


def open_output(port_name: str, **kwargs):
    try:
        return mido.open_output(port_name, **kwargs)
    except IOError:
        raise Exception(f"No output device/port named {port_name}")


def open_input(port_name: str, **kwargs):
    try:
        return mido.open_input(port_name, **kwargs)
    except IOError:
        raise Exception(f"No input device/port named {port_name}")


class Color:
    """
    Full color map is available in Novation guide

    https://www.djshop.gr/Attachment/DownloadFile?downloadId=10737
    """

    GREEN = 87
    GREEN_DIMMED = 19
    PINK = 107
    WHITE = 3


class FunctionPad:
    """
    Function pads, mostly top row and right column.
    """

    ARROW_UP = 91
    ARROW_DOWN = 92
    STOP = 19
    TEMPO_PADS = [ARROW_UP, ARROW_DOWN]


LSS_ASCII = r"""
.____       _________ _________
|    |     /   _____//   _____/
|    |     \_____  \ \_____  \
|    |___  /        \/        \
|_______ \/_______  /_______  /
        \/        \/        \/
"""
