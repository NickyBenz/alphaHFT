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
        trade_df = pd.read_csv(filename, header=0, index_col='local_timestamp', compression="gzip")
        trade_df.index = pd.to_datetime(trade_df.index, unit="us")
        modified_df = pd.DataFrame(columns=self.columns)

        prev_trade = TradeSnapshot()
        prev_trade.fill(trade_df.iloc[0], trade_df.index[0])

        print("number of trades: ", trade_df.shape[0])

        for row_count in range(1, trade_df.shape[0]):
            curr_trade = TradeSnapshot()
            curr_trade.fill(trade_df.iloc[row_count], trade_df.index[row_count])
            if curr_trade.timestamp < prev_trade.timestamp + pd.Timedelta(1, unit='s'):
                prev_trade.add(curr_trade, 1000000)
            else:
                trans = curr_trade.compute(prev_trade)
                modified_df.loc[curr_trade.timestamp, self.columns] = trans.flatten()
                prev_trade = curr_trade

        modified_df.index.name = 'timestamp'
        modified_df.to_csv(output_file, compression='gzip')
        return output_file
