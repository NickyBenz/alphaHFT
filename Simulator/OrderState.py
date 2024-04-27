from enum import Enum


class OrderState(Enum):
    NEW = 1
    AMEND = 2
    CANCELLED = 3
    FILLED = 4
