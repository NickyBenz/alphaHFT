from os import listdir
from os.path import isfile, join


class Fetcher:
    def __init__(self, root_path):
        self.book_path = root_path + r"/book_snapshot_5/"
        self.trade_path = root_path + r"/trades/"

    @staticmethod
    def get_files(mypath):
        files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
        return files

    def get_book_files(self):
        return Fetcher.get_files(self.book_path)

    def get_trade_files(self):
        return Fetcher.get_files(self.trade_path)