import yfinance as yf
import pandas as pd
from datetime import datetime
from utils.symbol_data_extractor import SymbolDataExtractor
from pathlib import Path


class YahooDataExtractor(SymbolDataExtractor):

    def __init__(self, symbols_to_query=None):
        super().__init__()
        self.col_mapping = {'symbol': 'symbol',
                            'Adj Close': 'close',
                            'High': 'dayMax',
                            'Low': 'dayMin',
                            'Open': 'open',
                            'Volume': 'volume'}
        self.symbols_to_query = symbols_to_query

    def get_cedear_symbols(self):
        ratios_data_path = Path(__file__).parent.parent.joinpath("data", "cedear_ratios_reloaded.xlsx")
        cedear_ratios = pd.read_excel(ratios_data_path, sheet_name="cedear")
        cedear_ratios = cedear_ratios[
            (cedear_ratios["type"].isin(["base", "dolar"]))
            & (cedear_ratios["can_use"] == 1)
            ]
        symbols_to_query = set(cedear_ratios["symbol"])
        symbols = {s + ".BA" for s in symbols_to_query}
        self.symbols_to_query = symbols

    def get_data(self):
        if self.symbols_to_query is None:
            self.get_cedear_symbols()
        today_date = datetime.now().date()
        queried_df = yf.download(self.symbols_to_query, period="1d", interval="1d")
        queried_df.index = pd.to_datetime(queried_df.index)
        filtered_df = queried_df[queried_df.index.date == today_date]
        stacked_df = filtered_df.stack(level=0).T.reset_index().droplevel(0, axis=1)
        stacked_df.rename(columns={'': 'symbol'}, inplace=True)

        self.clean_df = stacked_df

    def format_output(self):
        # Set the symbol name correctly
        self.clean_df['symbol'] = self.clean_df['symbol'].str.split('.').str[0]

        # The following data is not available
        self.clean_df['exchange'] = "BUE"
        self.clean_df['settlementPeriod'] = 48
        self.clean_df['ask'] = None
        self.clean_df['bid'] = None
        self.clean_df['askSize'] = None
        self.clean_df['bidSize'] = None


if __name__ == "__main__":
    data_extractor = YahooDataExtractor()
    data_extractor.run()
    data_df = data_extractor.clean_df
