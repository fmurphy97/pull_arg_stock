from iolApi.token import Token
from iolApi.titlequery import TitleQuery
import pandas as pd

from utils.clean_cedear_data import *

# Create token and title query instances
token = Token()
title_query = TitleQuery(token)

# Query any instrument
queried_data = title_query.get_instrument_data(instrument_type="cedears", country="argentina")

# Get it into a df
queried_df = pd.DataFrame(queried_data['titulos'])
# Expand the puntas column
queried_df = queried_df[~queried_df["puntas"].isna()]
queried_df[[key for key in queried_df['puntas'].iloc[0].keys()]] = queried_df['puntas'].apply(lambda x: pd.Series(x))


es_to_en_col_mapping = {
 'simbolo': "symbol",
 'apertura': "open",
 'maximo': "dayMax",
 'minimo': "dayMin",
 'ultimoCierre': "close",
 'volumen': "volume",
 'mercado': "exchange",
 'moneda': "currency",
 'descripcion': "shortName",
 'cantidadCompra': "askSize",
 'precioCompra': "ask",
 'precioVenta': "bid",
 'cantidadVenta': "bidSize"
}

queried_df.rename(columns=es_to_en_col_mapping, inplace=True)
queried_df = queried_df[list(es_to_en_col_mapping.values())]

queried_df['currency'] = queried_df['currency'].replace({"1": 'ARS', "2": 'USD'})
queried_df['exchange'] = queried_df['exchange'].replace({"1": 'BUE'})
queried_df['symbol'] = queried_df['symbol'] + '.BA'


cedear_data = pd.read_csv("data/inputs/cedear_ratios.csv")


# df_full = all_calculations(df=queried_df, species_data=cedear_data)
my_dict = {}
for _, row in cedear_data.iterrows():
 my_dict[row['symbol_arg']] = row['symbol']
 my_dict[row['symbol_arg_usd']] = row['symbol']

queried_df['base_symbol'] = queried_df['symbol'].map(my_dict)
df2 = split_into_countries(queried_df, cedear_data)
df3 = calculate_mep(df2)

cols = ["base_symbol", "shortName_D_BA", "open_BA", "bid_BA", "ask_BA", "open_D_BA", "bid_D_BA", "ask_D_BA", "volume_BA",
        "volume_D_BA", "MEP", "MEP_compra_ARS", "MEP_compra_USD"]
df3[cols].rename(columns={"shortName_D_BA": "shortName"}).to_csv("data/outputs/df_mep.csv", index=False)

