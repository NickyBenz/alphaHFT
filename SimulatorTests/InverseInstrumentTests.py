import unittest
import pandas as pd
from Simulator.InverseInstrument import InverseInstrument


class InverseInstrumentTests(unittest.TestCase):

    def setUp(self):
        self.instrument = InverseInstrument("BTC-PERPETUAL", 0.5,
                                            10, 0, 0.0005)

    def test_create(self):
        self.assertEqual(self.instrument.tick_size, 0.5)
        self.assertEqual(self.instrument.min_amount, 10)
        self.assertEqual(self.instrument.symbol, "BTC-PERPETUAL")
        self.assertEqual(self.instrument.maker_fee, 0)
        self.assertEqual(self.instrument.taker_fee, 0.0005)

    def test_quote_amount(self):
        amount = self.instrument.quote_amount(0.001, 65234)
        self.assertEqual(70, amount)

        amount = self.instrument.quote_amount(0.01, 10)
        self.assertEqual(10, amount)

    def test_pnl(self):
        pnl = self.instrument.pnl(0.1, 1000, 2000)
        self.assertEqual(0.05, pnl)

        pnl = self.instrument.pnl(1, 2000, 1000)
        self.assertEqual(-1, pnl)

    def test_qty_from_notional(self):
        qty = self.instrument.get_qty_from_notional(62000, 31000)
        self.assertEqual(0.5, qty)
        qty = self.instrument.get_qty_from_notional(30000, 300)
        self.assertEqual(0.01, qty)

    def test_fees(self):
        fees = self.instrument.fees(1, True)
        self.assertEqual(0, fees)

        fees = self.instrument.fees(1, False)
        self.assertEqual(0.0005, fees)

    def test_equity(self):
        equity = self.instrument.equity(30000, 33000, -0.05, 32000, 0.001)
        self.assertAlmostEqual(33000.0023333333334, equity)


if __name__ == '__main__':
    unittest.main()
