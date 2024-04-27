import sys
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd
from DeribitParser.FileFetcher import Fetcher
from DeribitParser.BookParser import BookParser
from DeribitParser.TradeParser import TradeParser

if len(sys.argv) < 2:
    print("Supply root directory for book and trade folders for matching dates")
    exit(1)

root_folder = sys.argv[1]

fetcher = Fetcher(root_folder)
book_files = fetcher.get_book_files()
trade_files = fetcher.get_trade_files()

temp_book_folder = "./temp_books/"
Path(temp_book_folder).mkdir(parents=True, exist_ok=True)

book_parser = BookParser(temp_book_folder)

temporary_books = []
for filename in book_files:
    modified_file = book_parser.parse(filename)
    temporary_books.append(modified_file)

temp_trade_folder = "./temp_trades/"
Path(temp_trade_folder).mkdir(parents=True, exist_ok=True)

trade_parser = TradeParser(temp_trade_folder)

temporary_trades = []
for filename in trade_files:
    modified_file = trade_parser.parse(filename)
    temporary_trades.append(modified_file)

align_mapper = {}

modified_books = [join(temp_book_folder, f)  for f in listdir(temp_book_folder) if isfile(join(temp_book_folder, f))]

for book_file in modified_books:
    tokens = os.path.basename(book_file).split("_")
    date_holder = tokens[5]
    symbol = tokens[6]
    trade_file = r"modified_deribit_trades_{0}_{1}".format(date_holder, symbol)
    trade_file = join(temp_trade_folder, trade_file)
    book_df = pd.read_csv(book_file, header=0, index_col='timestamp')
    trade_df = pd.read_csv(trade_file, header=0, index_col='timestamp')
    df = book_df.join(trade_df, how="outer")
    df.fillna(method='ffill', inplace=True)
    df.fillna(0, inplace=True)
    df.to_csv("data_" + date_holder + "_" + symbol)
