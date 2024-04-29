import sys

from pathlib import Path
from DeribitParser.FileFetcher import Fetcher
from DeribitParser.BookParser import BookParser
from DeribitParser.TradeParser import TradeParser
from DeribitParser.Aligner import Aligner

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

aligner = Aligner(temporary_books, temporary_trades)
aligner.align("./")