import pandas as pd

df_cedear = pd.DataFrame()

# Local in USD
df_local = df_cedear[
    (df_cedear["exchange"] == "BUE")
    & (df_cedear["type"] != "base")
    ]

# Local in ARS
df_ext = df_cedear[
    (df_cedear["exchange"] == "BUE")
    & (df_cedear["currency"] == "ARS")
    ]

cedear_cross_joined = pd.merge(df_local, df_ext, how="cross")
cedear_cross_joined = cedear_cross_joined[cedear_cross_joined["base_symbol_x"] == cedear_cross_joined["base_symbol_y"]]
