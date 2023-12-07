import pandas as pd


def join_with_asset_data(df, asset_type):
    # Join with cedear data to get the ratio, the currency and the base symbol
    cedear_ratios = pd.read_excel("../data/cedear_ratios_reloaded.xlsx", sheet_name=asset_type)
    df_merged = pd.merge(df, cedear_ratios, on="symbol", how="left")
    return df_merged


def cross_join_df(df):
    # Split into ARS vs other currency
    df_local_ars = df[(df["exchange"] == "BUE") & (df["currency"] == "ARS")]
    df_local_other = df[(df["exchange"] == "BUE") & (df["type"] == "dolar")]

    # Cross join the ARS vs other currency
    cedear_cross_joined = pd.merge(df_local_ars, df_local_other, how="cross")
    cedear_cross_joined = cedear_cross_joined[
        cedear_cross_joined["base_symbol_x"] == cedear_cross_joined["base_symbol_y"]]
    cedear_cross_joined["conversion"] = (
        cedear_cross_joined["symbol_x"] + " " + cedear_cross_joined["settlementPeriod_x"].astype(str) + "h - "
        + cedear_cross_joined["symbol_y"] + " " + cedear_cross_joined["settlementPeriod_y"].astype(str) + "h")

    return cedear_cross_joined


def calculate_mep(df):
    """Calculate ratio between outside price vs local"""
    df.loc[:, 'x/y mid'] = df['open_x'] / df['open_y']
    df.loc[:, "x/y ask"] = df["ask_x"] / df["bid_y"]
    df.loc[:, "x/y bid"] = df["bid_x"] / df["ask_y"]

    return df


if __name__ == "__main__":
    queried_df = pd.read_csv("queried_data.csv", sep=",")
    df_with_asset_data = join_with_asset_data(df=queried_df, asset_type='cedear')
    df_cross = cross_join_df(df=df_with_asset_data)
    df_mep = calculate_mep(df=df_cross)
