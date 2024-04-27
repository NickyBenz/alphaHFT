import os.path

import pandas as pd
from DeribitParser.TradeSnapshot import TradeSnapshot


class TradeParser:
    def __init__(self, temp_folder):
        self.temp_folder = temp_folder
        self.columns = ['long_size_diff', 'short_size_diff',
                        'long_price_diff', 'short_price_diff']

    def parse(self, filename):
        output_file = self.temp_folder + "modified_" + os.path.basename(filename)
        header = True
        write_mode = 'w'

        for chunk in pd.read_csv(filename, compression="gzip", chunksize=1024):
            df = pd.DataFrame(columns=self.columns)

            if header:
                prev_trade = TradeSnapshot()
                prev_trade.fill(chunk.iloc[0])
                last_trade = prev_trade

            for row_count in range(1, chunk.shape[0]):
                curr_trade = TradeSnapshot()
                curr_trade.fill(chunk.iloc[row_count])
                if curr_trade.timestamp < prev_trade.timestamp + 500000:
                    prev_trade.add(curr_trade, 500000)
                else:
                    trans = prev_trade.compute(last_trade)
                    ts = pd.to_datetime(last_trade.timestamp + 500000,
                                        unit='us', utc=True)
                    df.loc[ts, self.columns] = trans.flatten()
                    last_trade = prev_trade
                    prev_trade = curr_trade

            df.index.name = 'timestamp'
            df.to_csv(output_file, compression='gzip',
                      header=header, mode=write_mode)
            header = False
            write_mode = 'a'
        return output_file

