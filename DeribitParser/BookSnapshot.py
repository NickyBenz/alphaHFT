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
        self.ask_price_labels = []
        self.bid_price_labels = []
        self.ask_size_labels = []
        self.bid_size_labels = []

        for i in range(5):
            self.ask_price_labels.append("asks[{0}].price".format(i))
            self.ask_size_labels.append("asks[{0}].amount".format(i))
            self.bid_price_labels.append("bids[{0}].price".format(i))
            self.bid_size_labels.append("bids[{0}].amount".format(i))

    def fill(self, ds, idx):
        self.timestamp = idx

        for i in range(5):
            self.bid_prices[i] = ds.loc[self.bid_price_labels[i]]
            self.ask_prices[i] = ds.loc[self.ask_price_labels[i]]
            self.bid_sizes[i] = ds.loc[self.bid_size_labels[i]]
            self.ask_sizes[i] = ds.loc[self.ask_size_labels[i]]

        self.bid_cumsum = np.cumsum(self.bid_sizes, axis=0)
        self.ask_cumsum = np.cumsum(self.ask_sizes, axis=0)

    def bid_ask_imbalance(self):
        total_bid_volume = sum(self.bid_sizes)
        total_ask_volume = sum(self.ask_sizes)

        return (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)

    def weighted_imbalance(self):
        best_bid = self.bid_prices[0]
        best_ask = self.ask_prices[0]

        weighted_bid_volume = 0
        weighted_ask_volume = 0

        for i in range(0, self.bid_prices.shape[0]):
            weighted_bid_volume += (best_ask - self.bid_prices[i]) / (best_ask - best_bid) * self.bid_cumsum[i]
            weighted_ask_volume += (self.ask_prices[i] - best_bid) / (best_ask - best_bid) * self.ask_cumsum[i]

        return (weighted_bid_volume - weighted_ask_volume) / (weighted_bid_volume + weighted_ask_volume)

    def orderbook_slope(self):
        prices = np.concatenate((self.bid_prices, self.ask_prices))
        volumes = np.concatenate((self.bid_sizes, self.ask_sizes))

        a_matrix = np.vstack([prices, np.ones_like(prices)]).T
        slope, _ = np.linalg.lstsq(a_matrix, volumes, rcond=None)[0]
        return slope

    def bid_vwap(self):
        notional = np.sum(self.bid_prices * self.bid_sizes)
        bid_vwap_price = notional / np.sum(self.bid_sizes)
        return (self.bid_prices[0] - bid_vwap_price) / (self.bid_prices[0] - self.bid_prices[-1])

    def ask_vwap(self):
        notional = np.sum(self.ask_prices * self.ask_sizes)
        ask_vwap_price = notional / np.sum(self.ask_sizes)
        return (ask_vwap_price - self.ask_prices[0]) / (self.ask_prices[-1] - self.ask_prices[0])

    def depth_weighted_spread(self):
        weighted_spreads_sum = 0
        total_volume = 0

        for i in range(self.bid_prices.shape[0]):
            spread = self.ask_prices[i] - self.bid_prices[i]
            avg_volume = (self.bid_sizes[i] + self.ask_sizes[i]) / 2.0

            weighted_spreads_sum += spread * avg_volume
            total_volume += avg_volume

        return weighted_spreads_sum / total_volume

    def order_flow(self, prev_snap):
        orderflow = np.zeros(self.bid_prices.shape[0] - 1)

        for i in range(1, self.bid_prices.shape[0]):
            orderflow[i-1] = (self.bid_prices[i] >= prev_snap.bid_prices[i]) * self.bid_sizes[i] - \
                             (self.bid_prices[i] <= prev_snap.bid_prices[i]) * prev_snap.bid_sizes[i] - \
                             (self.ask_prices[i] <= prev_snap.ask_prices[i]) * self.ask_sizes[i] + \
                             (self.ask_prices[i] >= prev_snap.ask_prices[i]) * prev_snap.ask_sizes[i]

        return orderflow

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
        record.imbalance = self.bid_ask_imbalance()
        record.weighted_imbalance = self.weighted_imbalance()
        record.order_book_slope = self.orderbook_slope()
        record.depth_weighted_spread = self.depth_weighted_spread()
        record.bid_vwap = self.bid_vwap()
        record.ask_vwap = self.ask_vwap()
        record.order_flow = self.order_flow(prev_snap)
        notional_sum = self.bid_prices * self.bid_sizes + self.ask_prices * self.ask_sizes
        record.order_flow /= notional_sum[:-1] * 100.0
        return record
