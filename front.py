import streamlit as st
import pandas as pd
from use_iol_query import update_iol_data, update_iol_data_cedear, update_iol_data_on
from user_yahoo_finance_query import update_yahoo_data
import datetime as dt

st.set_page_config(layout="wide")

data_source = st.radio(label="Select Data Source", options=["IOL", "Yahoo Finance"], horizontal=True)
if data_source == "IOL":
    instrument_type = st.radio(label="Select Instrument Type", options=["ALL", "ON", "CEDEAR"], horizontal=True)
if st.button("Refresh/Pull Data"):
    if data_source == "IOL":
        if instrument_type == "ON":
            update_iol_data_on()
        elif instrument_type == "CEDEAR":
            update_iol_data_cedear()
        else:
            update_iol_data()
    else:
        update_yahoo_data()

min_vol_usd = st.number_input("Min Volume USD", step=1250, value=5 * 10 ** 3)
# max_spread = cols[1].number_input("Max Spread", step=0.1, value=0.5)
max_spread = 0.5


df_mep = pd.read_csv("data/df_mep.csv")

df_mep["vol_ARS"] = df_mep["volume_BA"] * df_mep["open_BA"]
df_mep["vol_USD"] = df_mep["volume_D_BA"] * df_mep["open_D_BA"]
df_mep["spread_ARS"] = ((df_mep["ask_BA"] - df_mep["bid_BA"]).abs() * 2 /
                        (df_mep["ask_BA"] + df_mep["bid_BA"]))
df_mep["spread_USD"] = ((df_mep["ask_D_BA"] - df_mep["bid_D_BA"]).abs() * 2 /
                        (df_mep["ask_D_BA"] + df_mep["bid_D_BA"]))
df_mep["max_spread"] = df_mep[['spread_ARS', 'spread_USD']].max(axis=1)

df_mep = df_mep[
    (df_mep["vol_USD"] >= min_vol_usd)
    & (df_mep["max_spread"] < max_spread)
    ]

# Remove outliers in terms of USD/ARS relationship
for col_name in ["USD/ARS bid", "USD/ARS ask"]:
    reference_value = df_mep[col_name].median()
    df_mep = df_mep[
        (df_mep["USD/ARS ask"] - reference_value).abs() / reference_value < 0.5]


column_config = {"bid_D_BA": st.column_config.NumberColumn("bid_D_BA", format="%.2f"),
                 "ask_D_BA": st.column_config.NumberColumn("ask_D_BA", format="%.2f"),
                 "USD/ARS ask": st.column_config.NumberColumn("USD/ARS ask", format="$ %.0f"),
                 "USD/ARS bid": st.column_config.NumberColumn("USD/ARS bid", format="$ %.0f"),
                 "vol_ARS": st.column_config.NumberColumn("vol_ARS", format="%.0e"),
                 "vol_USD": st.column_config.NumberColumn("vol_USD", format="%.0e")

                 }

# CALCULATE CCL
ccl_estimate = (df_mep["USD/ARS ask"].mean()+df_mep["USD/ARS bid"].mean()) / 2
df_mep["volume_total"] = (df_mep["vol_ARS"] + df_mep["vol_USD"] * ccl_estimate)

ccl_puntas = []
for col_name in ["USD/ARS bid", "USD/ARS ask"]:
    df_mep["aux"] = df_mep[col_name] * df_mep['volume_total']
    ccl = df_mep["aux"].sum() / df_mep['volume_total'].sum()
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

st.dataframe(df_mep[["base_symbol", "shortName", "bid_BA", "ask_BA", "bid_D_BA", "ask_D_BA",
"vol_ARS", "vol_USD", "USD/ARS bid", "USD/ARS ask"]]
             , hide_index=True, column_config=column_config, width=5000)

st.markdown("## WINNERS")
max_col1_row = df_mep[df_mep['USD/ARS bid'] == df_mep['USD/ARS bid'].max()]
min_col2_row = df_mep[df_mep['USD/ARS ask'] == df_mep['USD/ARS ask'].min()]
max_col1_row['Obj'] = 'Buy USD'
min_col2_row['Obj'] = 'Buy ARS'

best_assets = pd.concat([max_col1_row, min_col2_row])
st.dataframe(best_assets[["base_symbol", "shortName", "bid_BA", "ask_BA", "bid_D_BA", "ask_D_BA",
"USD/ARS bid", "USD/ARS ask", 'Obj']]
             , hide_index=True, column_config=column_config, width=5000)

usd_entry_point = max_col1_row['USD/ARS bid'].iloc[0]
ars_entry_point = min_col2_row['USD/ARS ask'].iloc[0]

expected_profit = usd_entry_point / ars_entry_point - 1

cols = st.columns(2)
with cols[0]:
    st.metric(label="usd_entry_point", value="$ {:.1f}".format(round(usd_entry_point, 1)))
    st.write(f"Buy {max_col1_row['base_symbol'].iloc[0]}D at {max_col1_row['ask_D_BA'].iloc[0]} USD")
    st.write(f"Sell {max_col1_row['base_symbol'].iloc[0]} at {max_col1_row['bid_BA'].iloc[0]} ARS")
with cols[1]:
    st.metric(label="ars_entry_point", value="$ {:.1f}".format(round(ars_entry_point, 1)))
    st.write(f"Buy {min_col2_row['base_symbol'].iloc[0]} at {min_col2_row['ask_BA'].iloc[0]} ARS")
    st.write(f"Sell {min_col2_row['base_symbol'].iloc[0]}D at {min_col2_row['bid_D_BA'].iloc[0]} USD")

st.metric(label="expected_profit", value="{:.1f} %".format(round(expected_profit * 100, 1)))


