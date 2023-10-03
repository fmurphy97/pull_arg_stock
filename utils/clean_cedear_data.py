import yfinance as yf
import pandas as pd
from tqdm import tqdm


def query_symbol_data_yf(species_data):
    """Iterate over all the symbols and the combinations, and pull the data"""
    missing_symbols = []
    data = {}

    input_species_data = species_data[species_data["include"]].to_dict(orient="records")

    for symbol_info in tqdm(input_species_data):
        base_symbol = symbol_info["symbol"]
        for symbol_type in ['symbol', 'symbol_arg', 'symbol_arg_usd']:
            current_symbol = symbol_info[symbol_type]
            yf_ticker = yf.Ticker(current_symbol)
            try:
                retrieved_ticker_info = yf_ticker.info
                retrieved_ticker_info["base_symbol"] = base_symbol

                data[current_symbol] = yf_ticker.info
            except:
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
    ratios_df = species_data[["symbol", "ratio"]].copy()
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
    df = df[~df['symbol'].isna()]
    df_local_ars = df[df['symbol'].isin(species_data['symbol_arg'])]
    df_local_usd = df[df['symbol'].isin(species_data['symbol_arg_usd'])]
    df_ext_usd = df[df['symbol'].isin(species_data['symbol'])]

    # Merge df in pesos and dollars
    df_usd = pd.merge(df_ext_usd, df_local_usd, on="base_symbol", how='outer', suffixes=('', '_D_BA'))
    df_merged = pd.merge(df_usd, df_local_ars, on="base_symbol", how='outer', suffixes=('', '_BA'))

    return df_merged


if __name__ == "__main__":
    cedear_data = pd.read_csv("../data/inputs/cedear_ratios.csv")
    queried_df = query_symbol_data_yf(cedear_data)

    df_merged_by_country = split_into_countries(df=queried_df, species_data=cedear_data)
    df_with_mep_values = calculate_mep(df=df_merged_by_country)
    df_with_adj_prices = adjust_prices(df=df_with_mep_values, species_data=cedear_data)

    # Display the df with the selected columns
    cols = ["base_symbol", "shortName", "open_BA", "bid_BA", "ask_BA", "open_D_BA", "bid_D_BA", "ask_D_BA", "volume_BA",
            "volume_D_BA", "MEP", "MEP_compra_ARS", "MEP_compra_USD", "ganDols", "ganPesos"]
    df_with_adj_prices[cols].to_csv("../data/outputs/df_mep.csv", index=False)

    # cols = ["base_symbol", "shortName", "open", "price_D_BA_adj", "price_BA_adj", "volume_BA", "volume_D_BA",
    # "ganDols", "ganPesos"]
    # df_full[cols].to_csv("data/outputs/asset_here_vs_local_with_ratio.csv", index=False)
