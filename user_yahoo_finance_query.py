import yfinance as yf
import pandas as pd
from tqdm import tqdm
from utils.clean_cedear_data import split_into_countries, calculate_mep, adjust_prices


def query_symbol_data_yf(species_data):
    """Iterate over all the symbols and the combinations, and pull the data"""
    missing_symbols = []
    data = {}

    input_species_data = species_data[species_data["include"]].to_dict(orient="records")

    for symbol_info in tqdm(input_species_data):
        base_symbol = symbol_info["symbol"]
        for symbol_type in ['symbol', 'symbol_arg', 'symbol_arg_usd']:
            current_symbol = str(symbol_info[symbol_type])
            try:
                yf_ticker = yf.Ticker(current_symbol)
                retrieved_ticker_info = yf_ticker.info
                retrieved_ticker_info["base_symbol"] = base_symbol

                data[current_symbol] = yf_ticker.info
            except:
                missing_symbols.append(current_symbol)
    print("No data for: ", missing_symbols)
    return pd.DataFrame.from_dict(data, orient="index")


def update_yahoo_data():
    cedear_data = pd.read_csv("data/inputs/cedear_ratios.csv")
    queried_df = query_symbol_data_yf(cedear_data)

    df_merged_by_country = split_into_countries(df=queried_df, species_data=cedear_data)
    df_with_mep_values = calculate_mep(df=df_merged_by_country)
    df_with_adj_prices = adjust_prices(df=df_with_mep_values, species_data=cedear_data)

    cols = ["base_symbol", "shortName", "open_BA", "ask_BA", "bid_BA", "open_D_BA", "bid_D_BA", "ask_D_BA", "volume_BA",
            "volume_D_BA", "MEP", "USD/ARS ask", "USD/ARS bid", "ganDols", "ganPesos"]
    df_with_adj_prices[cols].to_csv("data/outputs/df_mep.csv", index=False)

