import pandas as pd
import os
from DeribitParser.BookSnapshot import Snapshot


class BookParser:
    def __init__(self, temp_folder):
        self.temp_folder = temp_folder
        self.columns = ['bid_incr', 'ask_incr', 'bid_ticks_1', 'bid_ticks_2',
                        'bid_ticks_3', 'bid_ticks_4', 'ask_ticks_1', 'ask_ticks_2',
                        'ask_ticks_3', 'ask_ticks_4', 'bid_sum_0', 'bid_sum_1',
                        'bid_sum_2', 'bid_sum_3', 'bid_sum_4', 'ask_sum_0',
                        'ask_sum_1', 'ask_sum_2', 'ask_sum_3', 'ask_sum_4',
                        'bid_sum_diff_0', 'bid_sum_diff_1', 'bid_sum_diff_2',
                        'bid_sum_diff_3', 'bid_sum_diff_4', 'ask_sum_diff_0',
                        'ask_sum_diff_1', 'ask_sum_diff_2', 'ask_sum_diff_3',
                        'ask_sum_diff_4', 'bid_price', 'ask_price',
                        'imbalance', 'weighted_imbalance', 'order_book_slope',
                        'depth_weighted_spread', 'bid_vwap', 'ask_vwap',
                        'of1', 'of2', 'of3', 'of4']

    def parse(self, filename):
        output_file = self.temp_folder + "modified_" + os.path.basename(filename)
        book_df = pd.read_csv(filename, header=0, index_col='local_timestamp', compression="gzip")
        book_df.index = pd.to_datetime(book_df.index, unit='us')
        book_df = book_df.resample("1s").last().ffill()
        modified_df = pd.DataFrame(columns=self.columns)
        prev_snap = Snapshot()
        prev_snap.fill(book_df.iloc[0], book_df.index[0])
        print("number of book records: ", book_df.shape[0])
        write_header = True
        write_mode = "w"

        for rowcount in range(1, book_df.shape[0]):
            curr_snap = Snapshot()
            curr_snap.fill(book_df.iloc[rowcount], book_df.index[rowcount])
            record = curr_snap.compute(prev_snap)
            modified_df.loc[curr_snap.timestamp, self.columns] = record.flatten()
            prev_snap = curr_snap

            if rowcount % 500 == 0 or rowcount == book_df.shape[0] - 1:
                print("rowcount: ", rowcount)
                modified_df.index.name = 'timestamp'
                modified_df.to_csv(output_file, compression='gzip', header=write_header, mode=write_mode)
                modified_df = pd.DataFrame(columns=self.columns)
                write_mode = 'a'
                write_header = False
        return output_file
