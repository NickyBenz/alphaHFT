from Simulator.BaseInstrument import BaseInstrument
from Simulator.OrderState import OrderState
from Simulator.Position import Position
from Simulator.Exchange import Exchange


class Strategy:
    def __init__(self, instr: BaseInstrument, exchange: Exchange,
                 amount: float, base_amount: float):
        self.amount = amount
        self.base_amount = base_amount
        self.instr = instr
        self.exchange = exchange
        self.position = Position(amount, instr, 0, 0)
        self.order_id = 0

    def reset(self, start_pos: int):
        self.order_id = 0
        self.exchange.reset(start_pos)
        self.position = Position(self.amount, self.instr, 0, 0)

    def quote(self,
              buy_spread: int, sell_spread: int,
              buy_multiple: int, sell_multiple: int):

        ds = self.exchange.get_current_observation()

        if buy_multiple == 1 or buy_multiple == 3:
            self.exchange.cancel_buys()
            bid_price = ds.loc["bid_price"] - buy_spread * self.instr.tick_size

            if buy_multiple == 1 or self.position.total_qty // self.base_amount <= 0:
                bid_amount = self.instr.quote_amount(buy_multiple * self.base_amount,
                                                     bid_price)
            else:
                bid_amount = self.instr.quote_amount(self.position.total_qty / bid_price, bid_price)

            self.order_id += 1
            self.exchange.quote(self.order_id, True, bid_price, bid_amount)
        elif buy_multiple == 2:
            self.exchange.cancel_buys()

        if sell_multiple == 1 or sell_multiple == 3:
            self.exchange.cancel_sells()
            ask_price = ds.loc["ask_price"] + sell_spread * self.instr.tick_size

            if sell_multiple == 1 or self.position.total_qty // self.base_amount >= 0:
                ask_amount = self.instr.quote_amount(sell_multiple * self.base_amount,
                                                     ask_price)
            else:
                ask_amount = self.instr.quote_amount(self.position.total_qty / ask_price, ask_price)

            self.order_id += 1
            self.exchange.quote(self.order_id, False, ask_price, ask_amount)
        elif sell_multiple == 2:
            self.exchange.cancel_sells()

        done = self.exchange.next_data()

        for fill in self.exchange.get_fills():
            assert fill.state == OrderState.FILLED
            self.position.on_fill(fill, True)

        return done

    def get_info(self, bid_price, ask_price):
        return self.position.get_info(bid_price, ask_price)

    def get_observation(self):
        return self.exchange.get_current_observation()
