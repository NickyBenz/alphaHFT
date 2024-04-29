import unittest
import numpy as np
import pandas as pd
from datetime import date
from pathlib import Path
from DeribitParser.FileFetcher import Fetcher
from DeribitParser.BookParser import BookParser
from DeribitParser.TradeParser import TradeParser
from DeribitParser.Aligner import Aligner


class ParserTests(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.columns = []

        for i in range(0, 5):
            self.columns.append("bids[{0}].price".format(i))
            self.columns.append("bids[{0}].amount".format(i))
            self.columns.append("asks[{0}].price".format(i))
            self.columns.append("asks[{0}].amount".format(i))

        self.book_df = pd.DataFrame(columns=self.columns)
        ts = date(year=2020, month=1, day=1)
        ts = (ts-date(1970,1,1)).total_seconds() * 1000000
        timestep = 50000
        ts += timestep
        self.book_df.loc[ts, self.columns] = [1000.0, 200, 1001.0, 300,
                                              999.5, 300, 1001.5, 200,
                                              998.5, 500, 1002.0, 600,
                                              998.0, 100, 1003.0, 150,
                                              996.0, 600, 1005.0, 800]

        vol = 0.5 / np.sqrt(365 * 24 * 3600 * 3)

        rowcount = np.random.randint(low=1048, high=5000)
        bid_price = 1000.0

        for i in range(0, rowcount):
            change_in_price = np.random.normal(loc=0, scale=1) * vol
            bid_price -= change_in_price * bid_price
            ask_price = bid_price
            ts += timestep

            for j in range(0, 5):
                bid_amount = np.random.randint(low=1, high=21) * 50
                ask_amount = np.random.randint(low=1, high=21) * 50
                bid_price -= 0.5
                ask_price += 0.5
                self.book_df.loc[ts, "bids[{0}].price".format(j)] = bid_price
                self.book_df.loc[ts, "bids[{0}].amount".format(j)] = bid_amount
                self.book_df.loc[ts, "asks[{0}].price".format(j)] = ask_price
                self.book_df.loc[ts, "asks[{0}].amount".format(j)] = ask_amount

        trade_columns = ["price", "amount", "side"]
        self.trade_df = pd.DataFrame(columns=trade_columns)
        trade_count = rowcount // 10

        for i in range(1, trade_count):
            trade_count = np.random.randint(low=1, high=30)
            timestamp = int(np.random.uniform(low=10*(trade_count-1), high=10*trade_count))
            timestamp = self.book_df.index[timestamp]

            if trade_count % 2 == 0:
                self.trade_df.loc[timestamp, "side"] = "sell"
                self.trade_df.loc[timestamp, "price"] = self.book_df.loc[timestamp, "bids[0].price"]
            else:
                self.trade_df.loc[timestamp, "side"] = "buy"
                self.trade_df.loc[timestamp, "price"] = self.book_df.loc[timestamp, "asks[0].price"]

            self.trade_df.loc[timestamp, "amount"] = np.random.uniform(low=10, high=1001)

        self.book_df.index.name = "local_timestamp"
        self.trade_df.index.name = "local_timestamp"

        self.book_df.to_csv("./test_data/book_snapshot_5/deribit_book_snapshot_5_2020-01-01_BTC-PERPETUAL.csv.gz", compression='gzip')
        self.trade_df.to_csv("./test_data/trades/deribit_trades_2020-01-01_BTC-PERPETUAL.csv.gz", compression="gzip")

    def test_run(self):
        root_folder = "./test_data/"

        fetcher = Fetcher(root_folder)
        book_files = fetcher.get_book_files()
        trade_files = fetcher.get_trade_files()

        temp_book_folder = "./test_data/temp_book/"
        Path(temp_book_folder).mkdir(parents=True, exist_ok=True)

        book_parser = BookParser(temp_book_folder)

        temporary_books = []
        for filename in book_files:
            modified_file = book_parser.parse(filename)
            temporary_books.append(modified_file)

        temp_trade_folder = "./test_data/temp_trade/"
        Path(temp_trade_folder).mkdir(parents=True, exist_ok=True)

        trade_parser = TradeParser(temp_trade_folder)

        temporary_trades = []
        for filename in trade_files:
            modified_file = trade_parser.parse(filename)
            temporary_trades.append(modified_file)

        aligner = Aligner("./test_data/temp_book/",
                          "./test_data/temp_trade/")
        aligner.align("./test_data/")
