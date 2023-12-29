import pandas as pd


class SymbolDataExtractor:
    def __init__(self):
        self.clean_df = pd.DataFrame()
        self.columns_to_output = ['symbol', 'open', 'dayMax', 'dayMin', 'close', 'volume', 'exchange',
                                  'bidSize', 'bid', 'ask', 'askSize', 'settlementPeriod']
        self.col_mapping = {}  # the mapping to translate the original column names to the required ones

    def run(self):
        self.get_data()
        self.format_output()
        # Rename columns
        self.clean_df.rename(columns=self.col_mapping, inplace=True)
        # Keep only relevant columns
        self.clean_df = self.clean_df[self.columns_to_output]

    def get_data(self):
        pass

    def format_output(self):
        pass
