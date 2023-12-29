import streamlit as st
import pandas as pd
import datetime as dt
from utils.mep_calculator import MepCalculator

st.set_page_config(layout="wide")

data_source = st.radio(label="Select Data Source", options=MepCalculator.switch_dict.keys(), horizontal=True)
min_vol_y = st.number_input("Min Volume USD", step=1250, value=5 * 10 ** 3)

df_mep = pd.DataFrame()

instrument_type = None
if data_source == "IOL":
    instrument_type = st.radio(label="Select Instrument Type", options=["ALL", "ON", "CEDEAR"], horizontal=True)
if st.button("Refresh/Pull Data"):
    comb = MepCalculator(selected_data_extractor_name=data_source, asset_type="cedear")
    comb.run()
    df_mep = comb.merged_df

for name in ['x', 'y']:
    df_mep[f'vol_{name}'] = df_mep[f'volume_{name}'] * df_mep[f'open_{name}']

cols_to_show = ['symbol_x', 'bid_x', 'ask_x', 'bid_y', 'ask_y', 'vol_x', 'vol_y', 'x/y ask', 'x/y bid']

st.dataframe(df_mep[cols_to_show])

# ==================

df_mep["spread_x"] = ((df_mep["ask_x"] - df_mep["bid_x"]).abs() * 2 /
                      (df_mep["ask_x"] + df_mep["bid_x"]))
df_mep["spread_y"] = ((df_mep["ask_y"] - df_mep["bid_y"]).abs() * 2 /
                      (df_mep["ask_y"] + df_mep["bid_y"]))
df_mep["max_spread"] = df_mep[['spread_x', 'spread_y']].max(axis=1)

df_mep = df_mep[
    (df_mep["vol_y"] >= min_vol_y)
    & (df_mep["max_spread"] < 0.5)
    ]

# Remove outliers in terms of USD/ARS relationship
for col_name in ["x/y bid", "x/y ask"]:
    reference_value = df_mep[col_name].median()
    df_mep = df_mep[
        (df_mep["x/y ask"] - reference_value).abs() / reference_value < 0.5]

column_config = {"bid_y": st.column_config.NumberColumn("bid_y", format="%.2f"),
                 "ask_y": st.column_config.NumberColumn("ask_y", format="%.2f"),
                 "x/y ask": st.column_config.NumberColumn("x/y ask", format="$ %.0f"),
                 "x/y bid": st.column_config.NumberColumn("x/y bid", format="$ %.0f"),
                 "vol_x": st.column_config.NumberColumn("vol_x", format="%.0e"),
                 "vol_y": st.column_config.NumberColumn("vol_y", format="%.0e")

                 }

# CALCULATE CCL
ccl_puntas = []
for col_name in ["x/y bid", "x/y ask"]:
    df_mep["aux"] = df_mep[col_name] * df_mep['vol_y']
    ccl = df_mep["aux"].sum() / df_mep['vol_y'].sum()
    ccl_puntas.append(ccl)

new_ccl = sum(ccl_puntas) / 2
ccl_path = "data/dolar_ccl_historic.csv"
ccl_data = pd.read_csv(ccl_path, index_col="Fecha")
today_date = dt.date.today().strftime("%m/%d/%Y")
ccl_data.loc[today_date, :] = new_ccl
ccl_data.to_csv(ccl_path)

cols = st.columns(3)
cols[0].metric(label="CCL Avg Compra", value="$ {:.1f}".format(round(ccl_puntas[0], 1)))
cols[1].metric(label="CCL Avg", value="$ {:.1f}".format(round(new_ccl, 1)))
cols[2].metric(label="CCL Avg Venta", value="$ {:.1f}".format(round(ccl_puntas[1], 1)))

st.dataframe(df_mep[cols_to_show]
             , hide_index=True, column_config=column_config, width=5000)

st.markdown("## WINNERS")
max_col1_row = df_mep[df_mep['x/y bid'] == df_mep['x/y bid'].max()]
min_col2_row = df_mep[df_mep['x/y ask'] == df_mep['x/y ask'].min()]
max_col1_row['Obj'] = 'Buy USD'
min_col2_row['Obj'] = 'Buy ARS'

best_assets = pd.concat([max_col1_row, min_col2_row])
st.dataframe(best_assets[cols_to_show]
             , hide_index=True, column_config=column_config, width=5000)

usd_entry_point = max_col1_row['x/y bid'].iloc[0]
ars_entry_point = min_col2_row['x/y ask'].iloc[0]

expected_profit = usd_entry_point / ars_entry_point - 1

cols = st.columns(2)
with cols[0]:
    st.metric(label="usd_entry_point", value="$ {:.1f}".format(round(usd_entry_point, 1)))
    st.write(f"Buy {max_col1_row['symbol_y'].iloc[0]} at {max_col1_row['ask_y'].iloc[0]} USD")
    st.write(f"Sell {max_col1_row['symbol_x'].iloc[0]} at {max_col1_row['bid_x'].iloc[0]} ARS")
with cols[1]:
    st.metric(label="ars_entry_point", value="$ {:.1f}".format(round(ars_entry_point, 1)))
    st.write(f"Buy {min_col2_row['symbol_x'].iloc[0]} at {min_col2_row['ask_x'].iloc[0]} ARS")
    st.write(f"Sell {min_col2_row['symbol_y'].iloc[0]} at {min_col2_row['bid_y'].iloc[0]} USD")

st.metric(label="expected_profit", value="{:.1f} %".format(round(expected_profit * 100, 1)))
