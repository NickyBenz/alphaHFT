from abc import abstractmethod


class BaseInstrument:
    def __init__(self, symbol: str, tick_size: float,
                 min_amount: float,
                 maker_fee: float, taker_fee: float):
        self.symbol = symbol
        self.tick_size = tick_size
        self.min_amount = min_amount
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee

    @property
    def name(self) -> str:
        return self.symbol

    @abstractmethod
    def quote_amount(self, amount: float, price: float):
        pass

    @abstractmethod
    def equity(self, mid: float, balance: float,
               position: float, avg_price: float,
               fee: float) -> float:
        return balance + self.pnl(position, avg_price, mid) - fee

    @abstractmethod
    def get_qty_from_notional(self, price: float, notional: float) -> float:
        return notional / price

    @abstractmethod
    def pnl(self, qty: float, entry_price: float, exit_price: float) -> float:
        pass

    @abstractmethod
    def fees(self, qty: float, price: float, is_maker) -> float:
        if is_maker:
            return abs(qty) * self.maker_fee
        else:
            return abs(qty) * self.taker_fee
