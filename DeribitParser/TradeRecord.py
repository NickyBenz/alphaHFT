import numpy as np


class TradeRecord:
    def __init__(self):
        self.buy_vol_incr = 0
        self.sell_vol_incr = 0
        self.buy_price_incr = 0
        self.sell_price_incr = 0

    def flatten(self):
        ret = np.zeros(4)
        ret[0] = self.buy_vol_incr
        ret[1] = self.sell_vol_incr
        ret[2] = self.buy_price_incr
        ret[3] = self.sell_price_incr
        return ret
