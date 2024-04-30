from Simulator.BaseInstrument import BaseInstrument


class InverseInstrument(BaseInstrument):
    def __init__(self, symbol: str, tick_size: float,
                 min_amount: float, maker_fee: float,
                 taker_fee: float):
        super().__init__(symbol, tick_size, min_amount, maker_fee, taker_fee)

    def quote_amount(self, amount: float, price: float):
        amt = round(amount * price / self.min_amount) * self.min_amount

        if amt == 0:
            amt = self.min_amount
        return amt

    def get_qty_from_notional(self, price: float, notional: float) -> float:
        return super().get_qty_from_notional(price, notional)

    def pnl(self, qty: float, entry_price: float, exit_price: float) -> float:
        return qty * (1.0 - entry_price / exit_price)

    def equity(self, mid: float, balance: float,
               position: float, avg_price: float,
               fee: float) -> float:
        return super().equity(mid, balance, position, avg_price, fee)

    def fees(self, qty: float, is_maker) -> float:
        return super().fees(qty, is_maker)
