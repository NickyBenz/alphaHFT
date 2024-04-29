import pandas as pd
import os
from os import listdir
from os.path import isfile, join


class Aligner:
    def __init__(self, temp_book_path, temp_trade_path):
        self.book_path = temp_book_path
        self.trade_path = temp_trade_path

    def align(self, output_path):
        modified_books = [join(self.book_path, f) for f in listdir(self.book_path) if
                          isfile(join(self.book_path, f))]

        for book_file in modified_books:
            tokens = os.path.basename(book_file).split("_")
            date_holder = tokens[5]
            symbol = tokens[6]
            trade_file = r"modified_deribit_trades_{0}_{1}".format(date_holder, symbol)
            trade_file = join(self.trade_path, trade_file)
            book_df = pd.read_csv(book_file, header=0, index_col='timestamp')
            trade_df = pd.read_csv(trade_file, header=0, index_col='timestamp')
            df = book_df.join(trade_df, how="outer")
            df.fillna(method='ffill', inplace=True)
            df.fillna(0, inplace=True)
            df.to_csv(join(output_path, "data_" + date_holder + "_" + symbol))
