from DeribitParser.TradeRecord import TradeRecord


class TradeSnapshot:
    def __init__(self):
        self.timestamp = 0
        self.buy_vol = 0
        self.sell_vol = 0
        self.buy_price = 0
        self.sell_price = 0

    def fill(self, df):
        if self.timestamp > 0:
            raise ValueError("Cannot fill a non empty trade")

        self.timestamp = df.loc['local_timestamp']

        consideration = df.loc['amount'] * df.loc['price']
        if df.loc['side'] == 'sell':
            consideration += self.sell_vol * self.sell_price
            self.sell_vol += df.loc['amount']
            self.sell_price = consideration / self.sell_vol
        else:
            consideration += self.buy_vol * self.buy_price
            self.buy_vol += df.loc['amount']
            self.buy_price = consideration / self.buy_vol

    def add(self, curr_trade, time_difference):
        if self.timestamp == 0 or curr_trade.timestamp > self.timestamp + time_difference:
            raise ValueError("Timestamp mismatch in trade aggregation")

        consideration = curr_trade.buy_vol * curr_trade.buy_price + self.buy_vol * self.buy_price
        self.buy_vol += curr_trade.buy_vol

        if self.buy_vol > 0:
            self.buy_price = consideration / self.buy_vol

        consideration = curr_trade.sell_vol * curr_trade.sell_price + self.sell_vol * self.sell_price
        self.sell_vol += curr_trade.sell_vol

        if self.sell_vol > 0:
            self.sell_price = consideration / self.sell_vol

    def compute(self, last_trade):
        ts = TradeRecord()
        ts.buy_vol_incr = (self.buy_vol - last_trade.buy_vol) / (1. + self.buy_vol + last_trade.buy_vol)
        ts.sell_vol_incr = (self.sell_vol - last_trade.sell_vol) / (1. + self.sell_vol + last_trade.sell_vol)
        ts.buy_price_incr = (self.buy_price - last_trade.buy_price) / (1. + self.buy_price + last_trade.buy_price)
        ts.sell_price_incr = (self.sell_price - last_trade.sell_price) / (1. + self.sell_price + last_trade.sell_price)
        return ts
