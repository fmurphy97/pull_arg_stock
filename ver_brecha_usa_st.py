import streamlit as st
import pandas as pd
from pathlib import Path
from yahoo.extract_data import YahooDataExtractor
import plotly.express as px

st.set_page_config(layout="wide")

source_data_path = Path(__file__).parent.joinpath("data", "df_mep.csv")
df_mep = pd.read_csv(source_data_path)

source_data_path = Path(__file__).parent.joinpath("data", "cedear_ratios_reloaded.xlsx")
df_ratios = pd.read_excel(source_data_path, sheet_name="cedear_names")

data_extractor = YahooDataExtractor(symbols_to_query=list(df_ratios["base_symbol"]))
data_extractor.run()
data_df = data_extractor.clean_df
data_df.rename(columns={'close': 'close_ext'}, inplace=True)
df_mep = df_mep.merge(data_df[["symbol", "close_ext"]], how="left", left_on="base_symbol_x", right_on="symbol")
df_mep["close_ext_adj"] = df_mep["close_ext"] / df_mep["ratio_x"]

for col_name in ["bid_y", "ask_y", "close_y"]:
    new_col_name = col_name + "_perc"
    df_mep[new_col_name] = df_mep[col_name] / df_mep["close_ext_adj"]
    t = 0.4
    df_mep = df_mep[(df_mep[new_col_name] < (1+t)) & (df_mep[new_col_name] > (1-t))]


final_df = df_mep.sort_values(by="vol_value_y", ascending=False)
final_df = final_df[["base_symbol_x", "bid_y_perc", "ask_y_perc", "close_y_perc", "vol_value_y",
                     "bid_y", "ask_y", "close_y", "close_ext_adj"]]


st.title("Boxplot for Symbols")
fig = px.box(final_df, x="base_symbol_x", y=["bid_y_perc", "ask_y_perc", "close_y_perc"], title="Boxplots for Symbols")

st.plotly_chart(fig)
st.dataframe(final_df)
