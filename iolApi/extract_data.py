import pandas as pd
from iolApi.token import Token
from iolApi.titlequery import TitleQuery


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
                            'precioVenta': "ask", 'cantidadVenta': "askSize"}
    df.rename(columns=es_to_en_col_mapping, inplace=True)

    # Keep only relevant columns
    df = df[list(es_to_en_col_mapping.values())]

    # Update currencies
    df['currency'] = df['currency'].replace({"1": 'ARS', "2": 'USD'})
    df['exchange'] = df['exchange'].replace({"1": 'BUE'})

    df['settlementPeriod'] = 48

    return df

if __name__ == "__main__":
    df = query_data(instrument_type="cedears")
    df2 = format_output_df(df)
