import pandas as pd
from iolApi.token import Token
from iolApi.titlequery import TitleQuery
from utils.clean_cedear_data import split_into_countries_cedear, calculate_mep, split_into_countries_on


def query_data(instrument_type="cedears"):
    # Create token and title query instances
    token = Token()
    title_query = TitleQuery(token)

    # Query any instrument
    queried_data = title_query.get_instrument_data(instrument_type=instrument_type, country="argentina")

    # Get it into a df
    df = pd.DataFrame(queried_data['titulos'])

    return df


def format_output_df(df):
    # Expand the puntas column
    df = df[~df["puntas"].isna()]
    df[[key for key in df['puntas'].iloc[0].keys()]] = df['puntas'].apply(lambda x: pd.Series(x))

    # Re-Map english to spanish columns
    es_to_en_col_mapping = {'simbolo': "symbol", 'apertura': "open", 'maximo': "dayMax", 'minimo': "dayMin",
                            'ultimoCierre': "close", 'volumen': "volume", 'mercado': "exchange", 'moneda': "currency",
                            'descripcion': "shortName", 'cantidadCompra': "bidSize", 'precioCompra': "bid",
                            'precioVenta': "ask", 'cantidadVenta': "askSize"
                            }
    df.rename(columns=es_to_en_col_mapping, inplace=True)

    # Keep only relevant columns
    df = df[list(es_to_en_col_mapping.values())]

    # Update currencies
    df['currency'] = df['currency'].replace({"1": 'ARS', "2": 'USD'})
    df['exchange'] = df['exchange'].replace({"1": 'BUE'})
    df['symbol'] = df['symbol'] + '.BA'

    return df


def join_local_vs_foreign_asset(df, asset_data):
    my_dict = {}
    for _, row in asset_data.iterrows():
        my_dict[row['symbol_arg']] = row['symbol']
        my_dict[row['symbol_arg_usd']] = row['symbol']

    df['base_symbol'] = df['symbol'].map(my_dict)
    df2 = split_into_countries_cedear(df, asset_data)
    df3 = calculate_mep(df2)

    return df3


def join_local_vs_foreign_asset_ons(df):
    df['base_symbol'] = df['symbol'].str.split(".").str[0].str[:-1]
    df2 = split_into_countries_on(df)
    df3 = calculate_mep(df2)

    return df3


def update_iol_data_cedear(export_results=True):
    asset_ratios = pd.read_csv("data/cedear_ratios.csv")
    queried_df = query_data()
    queried_df_formatted = format_output_df(queried_df)
    final_queried_df = join_local_vs_foreign_asset(df=queried_df_formatted, asset_data=asset_ratios)

    cols = ["base_symbol", "shortName_D_BA", "open_BA", "bid_BA", "ask_BA", "open_D_BA", "bid_D_BA", "ask_D_BA",
            "volume_BA", "volume_D_BA", "MEP", "USD/ARS ask", "USD/ARS bid"]

    final_queried_df = final_queried_df[cols].rename(columns={"shortName_D_BA": "shortName"})
    if export_results:
        final_queried_df.to_csv("data/df_mep.csv", index=False)
    return final_queried_df


def update_iol_data_on(export_results=True):
    queried_df = query_data(instrument_type="obligacionesNegociables")
    queried_df_formatted = format_output_df(queried_df)
    final_queried_df = join_local_vs_foreign_asset_ons(df=queried_df_formatted)

    cols = ["base_symbol", "shortName", "open_BA", "bid_BA", "ask_BA", "open_D_BA", "bid_D_BA", "ask_D_BA",
            "volume_BA", "volume_D_BA", "MEP", "USD/ARS ask", "USD/ARS bid"]
    final_queried_df = final_queried_df[cols]

    if export_results:
        final_queried_df[cols].to_csv("data/df_mep.csv", index=False)
    return final_queried_df


def update_iol_data(export_results=True):
    cedear_df = update_iol_data_cedear(export_results=False)
    on_df = update_iol_data_on(export_results=False)

    combined_df = pd.concat([cedear_df, on_df])

    if export_results:
        combined_df.to_csv("data/df_mep.csv", index=False)
    return combined_df
