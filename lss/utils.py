import signal


def register_signal_handler(func) -> None:
    signal.signal(signal.SIGINT, func)
    signal.signal(signal.SIGTERM, func)


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
