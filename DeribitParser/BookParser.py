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
                        'ask_sum_diff_4', 'bid_price', 'ask_price']

    def parse(self, filename):
        output_file = self.temp_folder + "modified_" + os.path.basename(filename)
        header = True
        write_mode = 'w'

        for chunk in pd.read_csv(filename,
                                 compression="gzip", chunksize=1024):
            df = pd.DataFrame(columns=self.columns)

            if header:
                prev_snap = Snapshot()
                prev_snap.fill(chunk.iloc[0])
                last_snap = prev_snap

            for rowcount in range(1, chunk.shape[0]):
                curr_snap = Snapshot()
                curr_snap.fill(chunk.iloc[rowcount])

                if curr_snap.timestamp > last_snap.timestamp + 500000:
                    record = prev_snap.compute(last_snap)
                    ts = pd.to_datetime(last_snap.timestamp + 500000, unit='us', utc=True)
                    df.loc[ts, self.columns] = record.flatten()
                    last_snap = prev_snap
                prev_snap = curr_snap

            df.index.name = 'timestamp'
            df.to_csv(output_file, compression='gzip',
                      header=header, mode=write_mode)
            header = False
            write_mode = 'a'
        return output_file
