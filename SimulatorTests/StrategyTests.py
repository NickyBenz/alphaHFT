import unittest
import pandas as pd
from Simulator.Exchange import Exchange
from Simulator.Strategy import Strategy
from Simulator.InverseInstrument import InverseInstrument


class StrategyTests(unittest.TestCase):

    def setUp(self):
        self.instrument = InverseInstrument("BTC", 0.5, 10, 0, 0.0005)
        self.df = pd.DataFrame(columns=["bid_price", "ask_price"])
        ts = pd.Timestamp.utcnow()
        ts -= pd.Timedelta(2, unit='D')

        base_price = 1000.0
        delta = 0.5
        timestep = pd.Timedelta(500, unit='ms')

        for i in range(20):
            if i % 2 == 0:
                bid_price = base_price + (i % 10) * delta
            else:
                bid_price = base_price - (i % 10) * delta
            ts += timestep
            self.df.loc[ts, "ask_price"] = bid_price + delta
            self.df.loc[ts, "bid_price"] = bid_price

        self.exchange = Exchange(self.df)
        self.strategy = Strategy(self.instrument, self.exchange, 0.01, 0.001)

    def test_create(self):
        self.strategy.reset(1)
        ds = self.strategy.get_observation()
        self.assertEqual(999.5, ds["bid_price"])
        self.assertEqual(1000, ds["ask_price"])
        self.strategy.quote(True, True,
                            0, 1, 1, 1)

        for i in range(15):
            self.strategy.quote(False, False,
                                0,0,0,0)

        ds = self.strategy.get_observation()
        info = self.strategy.get_info(ds["bid_price"], ds["ask_price"])
        self.assertEqual(996.5, ds["bid_price"])
        self.assertEqual(997, ds["ask_price"])
        self.assertAlmostEqual(0.09990007495002534, info["trading_pnl_pct"])
        self.assertAlmostEqual(0, info["leverage"])
        self.assertEqual(2, info["trade_count"])
        self.assertAlmostEqual(0.010009990007495003, info["balance"])

