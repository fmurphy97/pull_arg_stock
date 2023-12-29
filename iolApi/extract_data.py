import pandas as pd

from iolApi.token import Token
from iolApi.titlequery import TitleQuery
from utils.symbol_data_extractor import SymbolDataExtractor


class IolDataExtractor(SymbolDataExtractor):

    def __init__(self, instrument_type="cedears"):
        super().__init__()

        self.col_mapping = {'simbolo': "symbol", 'apertura': "open", 'maximo': "dayMax", 'minimo': "dayMin",
                            'ultimoCierre': "close", 'volumen': "volume", 'mercado': "exchange",
                            'moneda': "currency", 'descripcion': "shortName", 'cantidadCompra': "bidSize",
                            'precioCompra': "bid", 'precioVenta': "ask", 'cantidadVenta': "askSize"}

        self.instrument_type = instrument_type

    def get_data(self):
        # Create token and title query instances
        token = Token()
        title_query = TitleQuery(token)

        # Query any instrument
        queried_data = title_query.get_instrument_data(instrument_type=self.instrument_type, country="argentina")

        # Get it into a df
        self.clean_df = pd.DataFrame(queried_data['titulos'])

    def format_output(self):
        # Expand the puntas column
        self.clean_df = self.clean_df[~self.clean_df["puntas"].isna()]
        self.clean_df[[key for key in self.clean_df['puntas'].iloc[0].keys()]] = \
            self.clean_df['puntas'].apply(lambda x: pd.Series(x))

        # Re-Map english to spanish columns
        self.clean_df.rename(columns=self.col_mapping, inplace=True)

        # Update currencies
        self.clean_df['currency'] = self.clean_df['currency'].replace({"1": 'ARS', "2": 'USD'})
        self.clean_df['exchange'] = self.clean_df['exchange'].replace({"1": 'BUE'})

        self.clean_df['settlementPeriod'] = 48

        # Keep only relevant columns
        self.clean_df = self.clean_df[self.columns_to_output]


if __name__ == "__main__":
    data_extractor = IolDataExtractor()
    data_extractor.run()
    data_df = data_extractor.clean_df
