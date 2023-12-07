import pandas as pd
import re


def get_data():
    # Read all files
    df_0 = pd.read_csv("cedear_0.txt", sep="\t", dtype=str)
    df_24 = pd.read_csv("cedear_24.txt", sep="\t", dtype=str)
    df_48 = pd.read_csv("cedear_48.txt", sep="\t", dtype=str)
    df_concat = pd.concat([df_0, df_24, df_48])

    return df_concat


def correct_str(input_str):
    # Correct the columns types
    input_str = input_str.replace(".", "")
    input_str = input_str.replace(",", ".")

    input_str = re.sub("[^0-9^.]", "", input_str)

    if input_str == '':
        input_str = 0.0
    return float(input_str)


def format_output_df(df_cedear):
    # Rename columns
    es_to_en_col_mapping = {'Especie': "symbol", 'Anterior': "open", 'Máx': "dayMax", 'Mín': "dayMin",
                            'Cierre': "close",
                            'Oper.': "volume", 'mercado': "exchange", 'moneda': "currency", 'CC': "bidSize",
                            'PC': "bid",
                            'PV': "ask", 'CV': "askSize", 'Plazo': "settlementPeriod"}
    df_cedear.rename(columns=es_to_en_col_mapping, inplace=True)

    df_cedear['exchange'] = "BUE"
    df_cedear['settlementPeriod'] = df_cedear['settlementPeriod'].replace({"C.I.": 0, "24hs.": 24, "48hs.": 48})

    for col_name in ["open", "dayMax", "dayMin", "close", "volume", "bidSize", "bid", "ask", "askSize"]:
        df_cedear[col_name] = df_cedear[col_name].apply(correct_str)

    for col_name in ["volume", "bidSize", "askSize"]:
        df_cedear[col_name] = df_cedear[col_name].astype(int)

    df_cedear = df_cedear[['symbol', 'open', 'dayMax', 'dayMin', 'close', 'volume', 'exchange',
                           'bidSize', 'bid', 'ask', 'askSize', 'settlementPeriod']]

    return df_cedear


if __name__ == '__main__':
    queried_data = get_data()
    data_formatted = format_output_df(queried_data)
    data_formatted.to_csv("../data/queried_data.csv", index=False)

