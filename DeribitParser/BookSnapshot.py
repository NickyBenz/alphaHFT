import numpy as np
from DeribitParser.BookRecord import BookRecord


class Snapshot:
    def __init__(self):
        self.timestamp = 0
        self.bid_prices = np.zeros(5)
        self.ask_prices = np.zeros(5)
        self.bid_sizes = np.zeros(5)
        self.ask_sizes = np.zeros(5)
        self.bid_cumsum = None
        self.ask_cumsum = None

        self.timestamp = r"local_timestamp"
        self.ask_price_labels = []
        self.bid_price_labels = []
        self.ask_size_labels = []
        self.bid_size_labels = []

        for i in range(5):
            self.ask_price_labels.append("asks[{0}].price".format(i))
            self.ask_size_labels.append("asks[{0}].amount".format(i))
            self.bid_price_labels.append("bids[{0}].price".format(i))
            self.bid_size_labels.append("bids[{0}].amount".format(i))

    def fill(self, ds):
        self.timestamp = ds.loc[self.timestamp]

        for i in range(5):
            self.bid_prices[i] = ds.loc[self.bid_price_labels[i]]
            self.ask_prices[i] = ds.loc[self.ask_price_labels[i]]
            self.bid_sizes[i] = ds.loc[self.bid_size_labels[i]]
            self.ask_sizes[i] = ds.loc[self.ask_size_labels[i]]

        self.bid_cumsum = np.cumsum(self.bid_sizes, axis=0)
        self.ask_cumsum = np.cumsum(self.ask_sizes, axis=0)

    def compute(self, prev_snap):
        record = BookRecord()
        record.timestamp = self.timestamp
        record.bid_price = self.bid_prices[0]
        record.ask_price = self.ask_prices[0]
        record.bid_incr = (self.bid_prices[0] - prev_snap.bid_prices[0]) / self.bid_prices[0] * 1000
        record.ask_incr = (self.ask_prices[0] - prev_snap.ask_prices[0]) / self.ask_prices[0] * 1000
        record.bid_ticks = np.diff(self.bid_prices) / self.bid_prices[0] * 1000
        record.ask_ticks = np.diff(self.ask_prices) / self.ask_prices[0] * 1000
        record.bid_cumsum = self.bid_cumsum / (self.bid_cumsum[-1] + self.ask_cumsum[-1])
        record.ask_cumsum = self.ask_cumsum / (self.bid_cumsum[-1] + self.ask_cumsum[-1])
        record.bid_cumsum_diff = (self.bid_cumsum - prev_snap.bid_cumsum) / (self.bid_cumsum + prev_snap.bid_cumsum)
        record.ask_cumsum_diff = (self.ask_cumsum - prev_snap.ask_cumsum) / (self.ask_cumsum + prev_snap.ask_cumsum)
        return record
