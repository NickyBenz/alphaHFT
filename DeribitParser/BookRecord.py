import pandas as pd
import numpy as np


class BookRecord:
    def __init__(self):
        self.timestamp = 0
        self.bid_price = 0
        self.ask_price = 0
        self.bid_incr = 0
        self.ask_incr = 0
        self.bid_ticks = None
        self.ask_ticks = None
        self.bid_cumsum = None
        self.ask_cumsum = None
        self.bid_cumsum_diff = None
        self.ask_cumsum_diff = None

    def flatten(self):
        result = np.zeros(32)
        result[0] = self.bid_incr
        result[1] = self.ask_incr
        result[2:6] = self.bid_ticks
        result[6:10] = self.ask_ticks
        result[10:15] = self.bid_cumsum
        result[15:20] = self.ask_cumsum
        result[20:25] = self.bid_cumsum_diff
        result[25:30] = self.ask_cumsum_diff
        result[30] = self.bid_price
        result[31] = self.ask_price
        return result.ravel()
