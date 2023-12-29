from tqdm import tqdm
import yfinance as yf
import pandas as pd


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


if __name__ == "__main__":
    cedear_ratios = pd.read_excel("../data/cedear_ratios_reloaded.xlsx", sheet_name="cedear")
    cedear_ratios = cedear_ratios[
        (cedear_ratios["type"].isin(["base", "dolar"]))
        & (cedear_ratios["can_use"] == 1)
        ]
    bla = yf.download(["SPY", "AAPL"], period="1d", interval="1d")
