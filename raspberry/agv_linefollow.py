from enum import Enum


class LineMode(Enum):
    OVERRIDE = -1
    DISABLE = 0
    KEEP_RIGHT = 1
    KEEP_LEFT = 2
    KEEP_STRAIGHT = 3
