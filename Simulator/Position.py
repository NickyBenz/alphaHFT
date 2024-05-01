import numpy as np
from Simulator.BaseInstrument import BaseInstrument
from Simulator.Order import Order
from Simulator.OrderState import OrderState


class Position:
    def __init__(self, balance: float, instrument: BaseInstrument,
                 init_qty: float, init_avg_price: float):
        self.initial_balance: float = balance
        self.balance: float = balance
        self.instrument: BaseInstrument = instrument
        self.total_qty: float = init_qty
        self.fees: float = 0
        self.trade_num: int = 0
        self.trade_qty: float = 0
        self.avg_price: float = init_avg_price

    def get_info(self, bid_price, ask_price):
        pnl = self.balance - self.initial_balance

        if self.total_qty < 0:
            pnl += self.instrument.pnl(self.total_qty, self.avg_price, bid_price)
        elif self.total_qty > 0:
            pnl += self.instrument.pnl(self.total_qty, self.avg_price, ask_price)

        info = {"balance": self.balance,
                "numOfTrades": self.trade_num,
                "pnlPct": pnl / self.initial_balance * 100.0}

        if self.total_qty == 0:
            info["leverage"] = 0
        else:
            info["leverage"] = abs(self.total_qty / self.avg_price) / self.initial_balance

        return info

    def on_fill(self, order: Order, is_maker) -> None:
        assert (order.state == OrderState.FILLED)
        notional_qty = self.instrument.get_qty_from_notional(order.price, order.amount)
        qty = order.amount

        total_notional_qty = 0

        if self.total_qty != 0:
            total_notional_qty = self.instrument.get_qty_from_notional(self.avg_price, self.total_qty)

        if not order.is_buy:
            qty = -qty
            notional_qty = -notional_qty

        pnl = 0

        if self.total_qty == 0:
            self.avg_price = order.price
        elif np.sign(self.total_qty) == np.sign(qty):
            assert (self.avg_price > 0)
            self.avg_price = (abs(notional_qty) * order.price +
                              abs(total_notional_qty) *
                              self.avg_price) / (abs(notional_qty) + abs(total_notional_qty))
        else:
            assert (self.avg_price > 0)
            if abs(self.total_qty) == abs(qty):
                pnl = self.instrument.pnl(order.amount, self.avg_price, order.price)
                self.avg_price = 0
            elif abs(self.total_qty) > abs(qty):
                pnl = self.instrument.pnl(order.amount, self.avg_price, order.price)
            else:
                pnl = self.instrument.pnl(self.total_qty, self.avg_price, order.price)
                self.avg_price = order.price

        self.fees += self.instrument.fees(order.amount, order.price, is_maker)
        self.trade_num += 1
        self.trade_qty += abs(qty)
        self.total_qty += qty
        self.balance += pnl
