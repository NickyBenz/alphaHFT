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
        self.imbalance = None
        self.weighted_imbalance = None
        self.order_book_slope = None
        self.depth_weighted_spread = None
        self.bid_vwap = None
        self.ask_vwap = None
        self.order_flow = None

    def flatten(self):
        result = np.zeros(42)
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
        result[32] = self.imbalance
        result[33] = self.weighted_imbalance
        result[34] = self.order_book_slope
        result[35] = self.depth_weighted_spread
        result[36] = self.bid_vwap
        result[37] = self.ask_vwap
        result[38:] = self.order_flow
        return result.ravel()
