import unittest
import numpy as np
import pandas as pd


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.columns = ["local_timestamp"]

        for i in range(0, 5):
            self.columns.append("bids[{0}].price".format(i))
            self.columns.append("bids[{0}].amount".format(i))
            self.columns.append("asks[{0}].price".format(i))
            self.columns.append("asks[{0}].amount".format(i))

        self.book_df = pd.DataFrame(columns=self.columns)
        ts = pd.Timestamp.utcnow()
        ts -= pd.Timedelta(2, unit='D')
        timestep = pd.Timedelta(300, unit='ms')
        ts += timestep
        self.book_df.loc[ts, self.columns] = [1000.0, 200, 1001.0, 300,
                                              999.5, 300, 1001.5, 200,
                                              998.5, 500, 1002.0, 600,
                                              998.0, 100, 1003.0, 150,
                                              996.0, 600, 1005.0, 800]

        vol = 0.5 / np.sqrt(365 * 24 * 3600 * 3)

        for i in range(0, 20):
            change_in_price = np.random.normal(loc=0, scale=1) * vol
            bid_price = self.book_df.iloc[0, "bids[0].price"]
            bid_price -= change_in_price * bid_price
            ask_price = bid_price

            for j in range(0, 5):
                bid_amount = np.random.uniform(low=1, high=21) * 50
                ask_amount = np.random.uniform(low=1, high=21) * 50
                bid_price -= 0.5
                ask_price += 0.5
                self.book_df.loc[ts + timestep, "bids[{0}].price".format(j)] = bid_price
                self.book_df.loc[ts + timestep, "bids[{0}].amount".format(j)] = bid_amount
                self.book_df.loc[ts + timestep, "asks[{0}].price".format(j)] = ask_price
                self.book_df.loc[ts + timestep, "asks[{0}].amount".format(j)] = ask_amount
