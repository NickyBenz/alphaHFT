from Simulator.OrderState import OrderState


class Order:
    def __init__(self, order_id, is_buy, price, amount, timestamp):
        self.order_id = order_id
        self.is_buy = is_buy
        self.price = price
        self.amount = amount
        self.state = OrderState.NEW
        self.timestamp = timestamp
