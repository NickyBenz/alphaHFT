import unittest
import pandas as pd
from Simulator.Order import Order
from Simulator.Exchange import Exchange


class ExchangeTests(unittest.TestCase):

    def setUp(self):
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

    def test_create(self):
        exchange = Exchange(self.df)
        self.assertEqual(len(exchange.timed_buffer), 0)
        self.assertEqual(len(exchange.quotes), 0)
        self.assertIsNotNone(exchange.df)
        self.assertEqual(exchange.counter, 0)
        self.assertIsNone(exchange.ds)

    def test_reset(self):
        exchange = Exchange(self.df)
        exchange.reset(3)
        self.assertEqual(len(exchange.timed_buffer), 0)
        self.assertEqual(len(exchange.quotes), 0)
        self.assertIsNotNone(exchange.df)
        self.assertEqual(exchange.counter, 3)
        self.assertIsNone(exchange.ds)

    def test_data_iterations(self):
        exchange = Exchange(self.df)
        exchange.reset(5)
        self.assertEqual(True, exchange.next_data())
        self.assertEqual(6, exchange.counter)
        self.assertEqual(0, len(exchange.timed_buffer))
        ds = exchange.get_current_observation()
        self.assertIsNotNone(ds)
        self.assertEqual(997.5, ds["bid_price"])
        self.assertEqual(998.0, ds["ask_price"])
        exchange.quote(1, True, 1020, 1)
        exchange.quote(2, False, 1800, 1)
        self.assertEqual(True, exchange.next_data())
        self.assertEqual(7, exchange.counter)
        ds = exchange.get_current_observation()
        self.assertIsNotNone(ds)
        self.assertEqual(0, len(exchange.quotes))
        self.assertEqual(1003.0, ds["bid_price"])
        self.assertEqual(1003.5, ds["ask_price"])
        self.assertEqual(1, len(exchange.timed_buffer))
        self.assertEqual(True, exchange.next_data())
        self.assertEqual(8, exchange.counter)
        ds = exchange.get_current_observation()
        self.assertEqual(996.5, ds["bid_price"])
        self.assertEqual(997.0, ds["ask_price"])
        self.assertEqual(1, len(exchange.quotes))
        fills = exchange.get_fills()
        self.assertEqual(0, len(fills))
        self.assertEqual(True, exchange.next_data())
        exchange.cancel_sells()
        self.assertEqual(9, exchange.counter)
        fills = exchange.get_fills()
        self.assertEqual(0, len(fills))
        self.assertEqual(996.5, ds["bid_price"])
        self.assertEqual(997.0, ds["ask_price"])
        self.assertEqual(1, len(exchange.quotes))
        self.assertEqual(True, exchange.next_data())
        fills = exchange.get_fills()
        self.assertEqual(1, len(fills))
        self.assertEqual(10, exchange.counter)
        self.assertEqual(True, exchange.next_data())
        self.assertEqual(11, exchange.counter)
        fills = exchange.get_fills()
        self.assertEqual(0, len(fills))
        self.assertEqual(0, len(exchange.quotes))

        for i in range(12, 20):
            self.assertEqual(True, exchange.next_data())
            self.assertEqual(i, exchange.counter)
            fills = exchange.get_fills()
            self.assertEqual(0, len(fills))
            self.assertEqual(0, len(exchange.quotes))
        self.assertEqual(False, exchange.next_data())
        fills = exchange.get_fills()
        self.assertEqual(0, len(fills))
        self.assertEqual(0, len(exchange.quotes))


if __name__ == '__main__':
    unittest.main()
