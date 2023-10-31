import pandas as pd


def calculate_mep(df):
    """Calculate ratio between outside price vs local"""
    df.loc[:, 'MEP'] = df['open_BA'] / df['open_D_BA']
    df.loc[:, "USD/ARS ask"] = df["ask_BA"] / df["bid_D_BA"]
    df.loc[:, "USD/ARS bid"] = df["bid_BA"] / df["ask_D_BA"]

    return df


def adjust_prices(df, species_data, metric="open"):
    """Adjust prices by the ratio and the CCL price"""
    # Load the ratios of the asset here vs usa
    ratios_df = species_data[["symbol", "ratio"]].copy()
    ratios_df.rename({"symbol": "base_symbol"}, inplace=True)

    # Merge df in dollars local vs usa, and make a ratio
    df_w_ratio = pd.merge(df, ratios_df, left_on="base_symbol", right_on="symbol", how="left", suffixes=('', '_y'))

    ccl = df_w_ratio["MEP"][df_w_ratio["base_symbol"] == "AAPL"]
    df_w_ratio[f"{metric}_D_BA_adj"] = df_w_ratio[f"{metric}_D_BA"] * df_w_ratio["ratio"]
    df_w_ratio[f"{metric}_BA_adj"] = df_w_ratio[f"{metric}_BA"] * df_w_ratio["ratio"] / ccl

    df_w_ratio["ganDols"] = (df_w_ratio[metric] - df_w_ratio[f"{metric}_D_BA_adj"]) / df_w_ratio[metric]
    df_w_ratio["ganPesos"] = (df_w_ratio[metric] - df_w_ratio[f"{metric}_BA_adj"]) / df_w_ratio[metric]

    return df_w_ratio


def split_into_countries_cedear(df, species_data):
    df = df[~df['symbol'].isna()]
    df_local_ars = df[df['symbol'].isin(species_data['symbol_arg'])]
    df_local_usd = df[df['symbol'].isin(species_data['symbol_arg_usd'])]
    df_ext_usd = df[df['symbol'].isin(species_data['symbol'])]

    # Merge df in pesos and dollars
    df_usd = pd.merge(df_ext_usd, df_local_usd, on="base_symbol", how='outer', suffixes=('', '_D_BA'))
    df_merged = pd.merge(df_usd, df_local_ars, on="base_symbol", how='outer', suffixes=('', '_BA'))

    return df_merged


def split_into_countries_on(df):
    df = df[~df['symbol'].isna()]
    df_local_ars = df[df['currency'] == "ARS"]
    df_local_usd = df[df['currency'] == "USD"]

    # Merge df in pesos and dollars
    df_merged = pd.merge(df_local_usd, df_local_ars, on="base_symbol", how='outer', suffixes=('_D_BA', '_BA'))

    df_merged.rename({"base_symbol_BA": "base_symbol}"}, inplace=True)

    return df_merged
