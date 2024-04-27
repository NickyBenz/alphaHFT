from enum import Enum


class OrderState(Enum):
    NEW = 1
    AMEND = 2
    CANCELLED = 2
    FILLED = 3
