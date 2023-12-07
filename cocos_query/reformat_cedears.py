import pandas as pd
import re

# Read all files
df_0 = pd.read_csv("cedear_0.txt", sep="\t", dtype=str)
df_24 = pd.read_csv("cedear_24.txt", sep="\t", dtype=str)
df_48 = pd.read_csv("cedear_48.txt", sep="\t", dtype=str)
df_cedear = pd.concat([df_0, df_24, df_48])

# Rename columns
es_to_en_col_mapping = {'Especie': "symbol", 'Anterior': "open", 'Máx': "dayMax", 'Mín': "dayMin", 'Cierre': "close",
                        'Oper.': "volume", 'mercado': "exchange", 'moneda': "currency", 'CC': "bidSize", 'PC': "bid",
                        'PV': "ask", 'CV': "askSize", 'Plazo': "settlementPeriod"}
df_cedear.rename(columns=es_to_en_col_mapping, inplace=True)

# Join with cedear data to get the ratio, the currency and the base symbol
cedear_ratios = pd.read_excel("cedear ratios reloaded.xlsx", sheet_name='cedear')
df_cedear = pd.merge(df_cedear, cedear_ratios, on="symbol", how="left")

df_cedear['exchange'] = "BUE"
df_cedear['settlementPeriod'] = df_cedear['settlementPeriod'].replace({"C.I.": 0, "24hs.": 24, "48hs.": 48})


# Correct the columns types
def correct_str(input_str):
    input_str = input_str.replace(".", "")
    input_str = input_str.replace(",", ".")

    input_str = re.sub("[^0-9^.]", "", input_str)

    if input_str == '':
        input_str = 0.0
    return float(input_str)


for col_name in ["open", "dayMax", "dayMin", "close", "volume", "bidSize", "bid", "ask", "askSize"]:
    df_cedear[col_name] = df_cedear[col_name].apply(correct_str)

for col_name in ["volume", "bidSize", "askSize"]:
    df_cedear[col_name] = df_cedear[col_name].astype(int)

df_cedear = df_cedear[['symbol', 'base_symbol', 'open', 'dayMax', 'dayMin', 'close', 'volume', 'exchange', 'currency',
                       'bidSize', 'bid', 'ask', 'askSize', 'settlementPeriod', 'type']]