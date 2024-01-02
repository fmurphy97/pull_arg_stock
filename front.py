import streamlit as st
import pandas as pd
from utils.mep_calculator import MepCalculator
import datetime as dt
from pathlib import Path

st.set_page_config(layout="wide")

data_source = st.radio(label="Select Data Source", options=["IOL", "Yahoo Finance"], horizontal=True)

# Select Data source
instrument_type = None
if data_source == "IOL":
    instrument_type = st.radio(label="Select Instrument Type", options=["ALL", "ON", "CEDEAR"], horizontal=True)
if st.button("Refresh/Pull Data"):
    comb = MepCalculator(selected_data_extractor_name=data_source, asset_type="cedear")
    comb.run()

source_data_path = Path(__file__).parent.joinpath("data", "df_mep.csv")
df_mep = pd.read_csv(source_data_path)

min_vol_value_y_var = st.number_input("Min Volume USD", step=1250, value=5 * 10 ** 3)


def outlier_removal(df, min_vol_value_y, max_spread=0.5):
    # Outliers in terms of value
    df = df[(df["vol_value_y"] >= min_vol_value_y) & (df["max_spread"] < max_spread)]

    # Remove outliers in terms of x/y relationship
    for c_n in ["x/y bid", "x/y ask"]:
        reference_value = df[c_n].median()
        df = df[(df[c_n] - reference_value).abs() / reference_value < 0.5]
    return df


df_mep = outlier_removal(df_mep, min_vol_value_y=min_vol_value_y_var)

column_config = {"bid_y": st.column_config.NumberColumn("bid_y", format="%.2f"),
                 "ask_y": st.column_config.NumberColumn("ask_y", format="%.2f"),
                 "x/y ask": st.column_config.NumberColumn("x/y ask", format="$ %.0f"),
                 "x/y bid": st.column_config.NumberColumn("x/y bid", format="$ %.0f"),
                 "vol_value_x": st.column_config.NumberColumn("vol_value_x", format="%.0e"),
                 "vol_value_y": st.column_config.NumberColumn("vol_value_y", format="%.0e")
                 }


def calculate_ccl(df):
    # Calculate CCL
    x_y_values = {}
    for additional in ["bid", "mid", "ask"]:
        col_name = "x/y " + additional
        df_mep["aux"] = df_mep[col_name] * df_mep['vol_value_y']
        ccl = df_mep["aux"].sum() / df_mep['vol_value_y'].sum()
        x_y_values[additional] = ccl

    # Export to csv
    ccl_path = Path(__file__).parent.joinpath("data", "dolar_ccl_historic.csv")
    ccl_data = pd.read_csv(ccl_path, index_col="Fecha")
    today_date = dt.date.today().strftime("%m/%d/%Y")
    ccl_data.loc[today_date, :] = x_y_values["mid"]
    ccl_data.to_csv(ccl_path)

    return x_y_values


x_y_values = calculate_ccl(df_mep)

cols = st.columns(3)
cols[0].metric(label="CCL Avg Compra", value="$ {:.1f}".format(round(x_y_values["bid"], 1)))
cols[1].metric(label="CCL Avg", value="$ {:.1f}".format(round(x_y_values["mid"], 1)))
cols[2].metric(label="CCL Avg Venta", value="$ {:.1f}".format(round(x_y_values["ask"], 1)))

st.dataframe(df_mep[["base_symbol_x", "shortName_x", "bid_x", "ask_x", "bid_y", "ask_y",
                     "vol_value_x", "vol_value_y", "x/y bid", "x/y ask"]],
             hide_index=True, column_config=column_config, width=5000)

st.markdown("## WINNERS")

if not df_mep.empty:
    max_col1_row = df_mep[df_mep['x/y bid'] == df_mep['x/y bid'].max()]
    min_col2_row = df_mep[df_mep['x/y ask'] == df_mep['x/y ask'].min()]
    max_col1_row['Obj'] = 'Buy USD'
    min_col2_row['Obj'] = 'Buy ARS'

    best_assets = pd.concat([max_col1_row, min_col2_row])
    st.dataframe(best_assets[["base_symbol_x", "shortName_x", "bid_x", "ask_x", "bid_y", "ask_y",
                              "x/y bid", "x/y ask", 'Obj']],
                 hide_index=True, column_config=column_config, width=5000)

    usd_entry_point = max_col1_row['x/y bid'].iloc[0]
    ars_entry_point = min_col2_row['x/y ask'].iloc[0]

    expected_profit = usd_entry_point / ars_entry_point - 1

    cols = st.columns(2)
    with cols[0]:
        st.metric(label="usd_entry_point", value="$ {:.1f}".format(round(usd_entry_point, 1)))
        st.write(f"Buy {max_col1_row['base_symbol_x'].iloc[0]}D at {max_col1_row['ask_y'].iloc[0]} USD")
        st.write(f"Sell {max_col1_row['base_symbol_x'].iloc[0]} at {max_col1_row['bid_x'].iloc[0]} ARS")
    with cols[1]:
        st.metric(label="ars_entry_point", value="$ {:.1f}".format(round(ars_entry_point, 1)))
        st.write(f"Buy {min_col2_row['base_symbol_x'].iloc[0]} at {min_col2_row['ask_x'].iloc[0]} ARS")
        st.write(f"Sell {min_col2_row['base_symbol_x'].iloc[0]}D at {min_col2_row['bid_y'].iloc[0]} USD")

    st.metric(label="expected_profit", value="{:.1f} %".format(round(expected_profit * 100, 1)))
else:
    st.markdown("### Not enough data")