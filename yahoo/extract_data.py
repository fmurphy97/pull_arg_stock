from tqdm import tqdm
import yfinance as yf
import pandas as pd
from datetime import datetime
from utils.symbol_data_extractor import SymbolDataExtractor


class YahooDataExtractor(SymbolDataExtractor):

    def __init__(self):
        super().__init__()
        self.col_mapping = {
            "symbol": 'symbol',
            "close": 'Adj Close',
            "dayMax": 'High',
            "dayMin": 'Low',
            "open": 'Open',
            "volume": 'Volume'}

        self.queried_df = None

    def get_data(self):
        cedear_ratios = pd.read_excel("../data/cedear_ratios_reloaded.xlsx", sheet_name="cedear")
        cedear_ratios = cedear_ratios[
            (cedear_ratios["type"].isin(["base", "dolar"]))
            & (cedear_ratios["can_use"] == 1)
            ]

        today_date = datetime.now().date()
        symbols = [s + ".BA" for s in set(cedear_ratios["symbol"])]
        queried_df = yf.download(symbols, period="1d", interval="1d")
        queried_df.index = pd.to_datetime(queried_df.index)
        filtered_df = queried_df[queried_df.index.date == today_date]
        stacked_df = filtered_df.stack(level=0).T.reset_index().droplevel(0, axis=1)
        stacked_df.rename(columns={'': 'symbol'}, inplace=True)

        self.queried_df = stacked_df

    def format_output(self):
        self.queried_df['symbol'] = self.queried_df['symbol'].str.split('.').str[0]
        self.queried_df['exchange'] = "BUE"
        self.queried_df['settlementPeriod'] = 48

        # Add currency
        cedear_ratios = pd.read_excel("../data/cedear_ratios_reloaded.xlsx", sheet_name="cedear")
        self.queried_df = self.queried_df.merge(cedear_ratios[["symbol", "currency"]], on="symbol", how="left")

        # The following data is not available
        self.queried_df['ask'] = None
        self.queried_df['bid'] = None
        self.queried_df['askSize'] = None
        self.queried_df['bidSize'] = None

        # Keep only relevant columns
        self.clean_df = self.queried_df
