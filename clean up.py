import yfinance as yf
import pandas as pd
from tqdm import tqdm
from requests.exceptions import HTTPError


def query_symbol_data_yf(species_data):
    """Iterate over all the symbols and the combinations, and pull the data"""
    missing_symbols = []
    data = {}

    input_species_data = species_data[species_data["include"]].to_dict(orient="records")

    for symbol_info in tqdm(input_species_data):
        base_symbol = symbol_info["symbol"]
        for symbol_type, symbol_suffix in {'symbol': "", 'symbol_arg': ".BA", 'symbol_arg_usd': ".BA"}.items():
            current_symbol = symbol_info[symbol_type] + symbol_suffix
            yf_ticker = yf.Ticker(current_symbol)
            try:
                retrieved_ticker_info = yf_ticker.info
                retrieved_ticker_info["base_symbol"] = base_symbol
                retrieved_ticker_info[symbol_type] = symbol_info[symbol_type]

                data[current_symbol] = yf_ticker.info
            except HTTPError:
                missing_symbols.append(current_symbol)
    print("No data for: ", missing_symbols)
    return pd.DataFrame.from_dict(data, orient="index")


def calculate_mep(df):
    """Calculate ratio between outside price vs local"""
    df.loc[:, 'MEP'] = df['open_BA'] / df['open_D_BA']
    df.loc[:, "MEP_compra_ARS"] = df["ask_BA"] / df["bid_D_BA"]
    df.loc[:, "MEP_compra_USD"] = df["bid_BA"] / df["ask_D_BA"]

    return df


def adjust_prices(df, species_data, metric="open"):
    """Adjust prices by the ratio and the CCL price"""
    # Load the ratios of the asset here vs usa
    ratios_df = species_data[["symbol", "ratio"]]
    ratios_df.rename({"symbol": "base_symbol"}, inplace=True)

    # Merge df in dollars local vs usa, and make a ratio
    df_w_ratio = pd.merge(df, ratios_df, left_on="base_symbol", right_on="symbol", how="left", suffixes=('', '_y'))

    ccl = df_w_ratio["MEP"][df_w_ratio["base_symbol"] == "AAPL"]
    df_w_ratio["price_D_BA_adj"] = df_w_ratio[f"{metric}_D_BA"] * df_w_ratio["ratio"]
    df_w_ratio["price_BA_adj"] = df_w_ratio[f"{metric}_BA"] * df_w_ratio["ratio"] / ccl

    df_w_ratio["ganDols"] = (df_w_ratio[metric] - df_w_ratio["price_D_BA_adj"]) / df_w_ratio[metric]
    df_w_ratio["ganPesos"] = (df_w_ratio[metric] - df_w_ratio["price_BA_adj"]) / df_w_ratio[metric]

    return df_w_ratio


def split_into_countries(df, species_data):
    df_local_ars = df[
        (~df['symbol_arg'].isna())
        & df['symbol_arg'].isin(species_data['symbol_arg'])]
    df_local_usd = df[
        (~df['symbol_arg_usd'].isna())
        & (df['symbol_arg_usd'].isin(species_data['symbol_arg_usd']))
        ]
    df_ext_usd = df[
        (~df['symbol'].isna())
        & (df['symbol'].isin(species_data['symbol']))
    ]

    # Merge df in pesos and dollars
    df_usd = pd.merge(df_ext_usd, df_local_usd, on="base_symbol", how='outer', suffixes=('', '_D_BA'))
    df_merged = pd.merge(df_usd, df_local_ars, on="base_symbol", how='outer', suffixes=('', '_BA'))

    return df_merged


if __name__ == "__main__":
    # Get the data in a df
    filepath = "data/outputs/species_data.csv"

    cedear_data = pd.read_csv("data/inputs/cedear_ratios.csv")
    queried_df = query_symbol_data_yf(cedear_data)
    queried_df.to_csv(filepath)

    df_full = split_into_countries(df=queried_df, species_data=cedear_data)
    df_full = calculate_mep(df=df_full)
    df_full = adjust_prices(df=df_full, species_data=cedear_data)

    df_full.to_csv("data/outputs/df_full.csv")

    # Display the df with the selected columns
    cols = ["base_symbol", "shortName", "open_BA", "bid_BA", "ask_BA", "open_D_BA", "bid_D_BA", "ask_D_BA", "volume_BA",
            "volume_D_BA", "MEP", "MEP_compra_ARS", "MEP_compra_USD", "ganDols", "ganPesos"]
    df_full[cols].to_csv("data/outputs/df_mep.csv", index=False)

    #
    cols = ["base_symbol", "shortName", "open", "price_D_BA_adj", "price_BA_adj", "volume_BA", "volume_D_BA", "ganDols",
            "ganPesos"]
    df_full[cols].to_csv("data/outputs/asset_here_vs_local_with_ratio.csv", index=False)