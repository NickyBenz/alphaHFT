import pandas as pd
from Simulator.Order import Order
from Simulator.OrderState import OrderState


class Exchange:
    def __init__(self, df):
        self.ds = None
        self.timestamp = None
        self.counter = 0
        self.df = df
        self.quotes = {}
        self.executions = []
        self.timed_buffer = {}
        self.reset(0)

    def reset(self, start_pos):
        self.counter = start_pos
        self.ds = None
        self.timestamp = None
        self.quotes.clear()
        self.executions.clear()
        self.timed_buffer.clear()
        self.next_data()

    def next_data(self):
        if self.counter < self.df.shape[0]:
            self.ds = self.df.iloc[self.counter, :]
            self.timestamp = self.df.index[self.counter]
            self.execute()
            self.counter += 1
        else:
            self.ds = None

        return self.counter < self.df.shape[0]

    def get_current_observation(self):
        return self.ds

    def get_fills(self):
        executions = self.executions[:]
        self.executions.clear()
        return executions

    def cancel_sells(self):
        cancels = []
        for order in self.quotes.values():
            if not order.is_buy:
                cancels.append(order)
        self.process_cancels(cancels)

    def quote(self, order_id, is_buy, price, amount):
        order = Order(order_id, is_buy, price, amount, self.timestamp)
        order.state = OrderState.NEW
        self.add_to_buffer(order)

    def cancel_buys(self):
        cancels = []
        for order in self.quotes.values():
            if order.is_buy:
                cancels.append(order)

        self.process_cancels(cancels)

    def process_cancels(self, cancels):
        for order in cancels:
            order.state = OrderState.CANCELLED
            order.timestamp = self.timestamp
            self.add_to_buffer(order)

    def execute(self):
        self.process_pending()
        processed = []
        for order in self.quotes.values():
            if order.is_buy and order.price > self.ds.loc['ask_price']:
                processed.append(order)
            if not order.is_buy and order.price < self.ds.loc['bid_price']:
                processed.append(order)

        for order in processed:
            order.state = OrderState.FILLED
            order.timestamp = self.timestamp
            del self.quotes[order.order_id]
            self.add_to_buffer(order)

    def add_to_buffer(self, order):
        if order.timestamp not in self.timed_buffer:
            self.timed_buffer[order.timestamp] = []

        self.timed_buffer[order.timestamp].append(order)

    def process_pending(self):
        deletions = {}
        for timestamp in self.timed_buffer:
            if self.timestamp >= timestamp + pd.Timedelta(1000, unit='ms'):
                for order in self.timed_buffer[timestamp]:
                    if order.state == OrderState.NEW:
                        if order.is_buy:
                            if order.price <= self.ds.loc["bid_price"]:
                                self.quotes[order.order_id] = order
                        else:
                            if order.price >= self.ds.loc["ask_price"]:
                                self.quotes[order.order_id] = order
                    elif order.state == OrderState.AMEND:
                        if order.order_id in self.quotes:
                            self.quotes[order.order_id] = order
                    elif order.state == OrderState.CANCELLED:
                        if order.order_id in self.quotes:
                            del self.quotes[order.order_id]
                    else:
                        assert order.state == OrderState.FILLED
                        self.executions.append(order)

                    if timestamp not in deletions:
                        deletions[timestamp] = []
                    deletions[timestamp].append(order)

        for timestamp in deletions:
            for order in deletions[timestamp]:
                self.timed_buffer[timestamp].remove(order)
            if len(self.timed_buffer[timestamp]) == 0:
                del self.timed_buffer[timestamp]
