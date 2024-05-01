import unittest
import pandas as pd
from Simulator.InverseInstrument import InverseInstrument
from Simulator.Position import Position
from Simulator.Order import Order
from Simulator.OrderState import OrderState


class PositionTests(unittest.TestCase):

    def setUp(self):
        self.instrument = InverseInstrument("BTC-PERPETUAL", 0.5,
                                            10, 0, 0.0005)
        self.position = Position(1, self.instrument, 1000, 1000)

    def test_create(self):
        self.assertEqual(self.position.instrument, self.instrument)
        self.assertEqual(self.position.fees, 0)
        self.assertEqual(self.position.balance, 1)
        self.assertEqual(self.position.total_qty, 1000)
        self.assertEqual(self.position.avg_price, 1000)
        self.assertEqual(self.position.trade_qty, 0)
        self.assertEqual(self.position.trade_num, 0)
        self.assertEqual(self.position.initial_balance, 1)

    def test_on_fill(self):
        order = Order(0, True, 990, 200, pd.Timestamp.now())
        order.state = OrderState.FILLED
        self.position.on_fill(order, True)
        self.assertAlmostEqual(1.202020202020202, self.position.get_info(999, 1000)["leverage"])
        self.assertEqual(self.position.fees, 0)
        self.assertEqual(self.position.balance, 1)
        self.assertEqual(1200, self.position.total_qty)
        self.assertAlmostEqual(self.position.avg_price, 998.3193277310925)
        self.assertEqual(self.position.trade_qty, 200)
        self.assertEqual(self.position.trade_num, 1)
        self.assertEqual(self.position.initial_balance, 1)
        order = Order(1, False, 970, 200, pd.Timestamp.now())
        order.state = OrderState.FILLED
        self.position.on_fill(order, False)

        self.assertAlmostEqual(0.000103092783505154642, self.position.fees)
        self.assertAlmostEqual(self.position.balance, 0.9939803745921792)
        self.assertAlmostEqual(self.position.total_qty, 1000)
        self.assertAlmostEqual(self.position.avg_price, 998.3193277310925)
        self.assertEqual(self.position.trade_qty, 400)
        self.assertEqual(self.position.trade_num, 2)
        self.assertEqual(self.position.initial_balance, 1)
        info = self.position.get_info(1000, 1000.5)
        self.assertAlmostEqual(-0.3841132176767581, info["pnlPct"])
        self.assertAlmostEqual(1.0016835016835017, info["leverage"])
        self.assertEqual(2, info["numOfTrades"])
        self.assertAlmostEqual(0.9939803745921792, info["balance"])


if __name__ == '__main__':
    unittest.main()
