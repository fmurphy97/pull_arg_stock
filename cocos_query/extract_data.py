import pandas as pd
from utils.symbol_data_extractor import SymbolDataExtractor
from utils.useful_functions import correct_str


class CocosDataExtractor(SymbolDataExtractor):

    def __init__(self):
        super().__init__()
        self.col_mapping = {'Especie': "symbol", 'Anterior': "open", 'Máx': "dayMax", 'Mín': "dayMin",
                            'Cierre': "close", 'Oper.': "volume", 'mercado': "exchange", 'moneda': "currency",
                            'CC': "bidSize", 'PC': "bid", 'PV': "ask", 'CV': "askSize", 'Plazo': "settlementPeriod"}

    def get_data(self):
        # Read all files
        df_0 = pd.read_csv("cedear_0.txt", sep="\t", dtype=str)
        df_24 = pd.read_csv("cedear_24.txt", sep="\t", dtype=str)
        df_48 = pd.read_csv("cedear_48.txt", sep="\t", dtype=str)
        df_concat = pd.concat([df_0, df_24, df_48])

        self.clean_df = df_concat

    def format_output(self):
        # Rename columns
        self.clean_df.rename(columns=self.col_mapping, inplace=True)

        self.clean_df['exchange'] = "BUE"
        self.clean_df['settlementPeriod'] = self.clean_df['settlementPeriod'].replace(
            {"C.I.": 0, "24hs.": 24, "48hs.": 48})
        self.clean_df['currency'] = None

        for col_name in ["open", "dayMax", "dayMin", "close", "volume", "bidSize", "bid", "ask", "askSize"]:
            self.clean_df[col_name] = self.clean_df[col_name].apply(correct_str)

        for col_name in ["volume", "bidSize", "askSize"]:
            self.clean_df[col_name] = self.clean_df[col_name].astype(int)

        df_cedear = self.clean_df[self.columns_to_output]

        return df_cedear


if __name__ == '__main__':
    data_extractor = CocosDataExtractor()
    data_extractor.run()
    data_extractor.clean_df.to_csv("../data/queried_data.csv", index=False)
