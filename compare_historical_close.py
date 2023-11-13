import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def get_stock_info(symbol: str):
    stock_data = pd.read_csv("data/cedear_ratios.csv", index_col="symbol").loc[symbol, :]
    stock_data["base_symbol"] = symbol
    return stock_data


def query_historical_data(stock_data: pd.DataFrame, period: str, interval: str,
                          use_local_usd=True, use_local_ars=True, use_ext_usd=True):
    dfs = {}

    if use_ext_usd:
        foreign_usd_df = yf.download(stock_data.base_symbol, period=period, interval=interval)
        foreign_usd_adj_df = adjust_by_ratio(foreign_usd_df, stock_data.ratio)
        dfs[symbol_data.base_symbol] = foreign_usd_adj_df

    if use_local_usd:
        local_usd_df = yf.download(stock_data.symbol_arg_usd, period=period, interval=interval)
        dfs[symbol_data.symbol_arg_usd] = local_usd_df

    if use_local_ars:
        local_ars_df = yf.download(stock_data.symbol_arg, period=period, interval=interval)
        local_ars_adj_df = adjust_local_price(local_ars_df)
        dfs[symbol_data.symbol_arg] = local_ars_adj_df

    return dfs


def adjust_by_ratio(df: pd.DataFrame, ratio: float):
    return df / ratio


def adjust_local_price(df: pd.DataFrame):
    historic_ccl = pd.read_csv("data/dolar_ccl_historic.csv", index_col="Fecha")
    historic_ccl.index = pd.to_datetime(historic_ccl.index)

    # Merge the two DataFrames based on the 'id' column
    df = df.merge(historic_ccl, left_index=True, right_index=True)

    # Divide each row in merged_df
    for col_name in df.columns:
        df[col_name] = df[col_name] / df["Referencia"]

    return df


def area_plot(dfs_by_symbol):
    colors = [(44, 160, 44), (31, 119, 180), (255, 127, 14)]
    fig = go.Figure()
    for i, (asset_symbol, df) in enumerate(dfs_by_symbol.items()):
        c = colors[i]
        # Add the price line
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name=asset_symbol, line_color=f'rgb{c}',
                                 hovertemplate='%{y:.2f}'))

        # Add the high-low area
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Low'], mode='lines', name='low', hoverinfo='skip', showlegend=False,
                       line_color=f'rgba({c[0]},{c[1]},{c[2]},0)'))

        fig.add_trace(go.Scatter(x=df.index, y=df['High'], mode='none', fill='tonexty',
                                 fillcolor=f'rgba({c[0]},{c[1]},{c[2]},0.2)',
                                 name='High-Low', hoverinfo='skip', showlegend=False))
        # Set the layout
    fig.update_layout(title='', xaxis=dict(title='Date'), yaxis=dict(title='Price'), showlegend=True,
                      hovermode="x unified", width=900, height=600)

    return fig


def candle_plot(dfs_by_symbol):
    colors = [(44, 160, 44), (31, 119, 180), (255, 127, 14)]
    fig = go.Figure()
    for i, (asset_symbol, df) in enumerate(dfs_by_symbol.items()):
        c = colors[i]
        new_c = tuple(int(v * 0.6) for v in c)
        fig.add_trace(
            go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df["Adj Close"], name=asset_symbol,
                           increasing=dict(line=dict(color=f'rgb{c}')),
                           decreasing=dict(line=dict(color=f'rgb{new_c}')),
                           ))
        # Set the layout
    fig.update_layout(title='', xaxis=dict(title='Date'), yaxis=dict(title='Price'), showlegend=True,
                      hovermode="x unified", width=900, height=600)

    return fig


symbol_usa = st.text_input("Select a symbol", value="SPY").upper()

possible_periods = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
                    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

selected_period = st.radio("Select an Period", possible_periods[possible_periods.index("1d"):], horizontal=True)
selected_interval = st.radio("Select an Interval", possible_periods[:possible_periods.index(selected_period)],
                             horizontal=True)

use_local_ars_data = st.checkbox("Use local ARS", value=False)
use_ext_usd_data = st.checkbox("Use Foreign USD", value=True)
use_local_usd_data = st.checkbox("Use local USD", value=True)

if st.button("RUN"):
    symbol_data = get_stock_info(symbol_usa)

    asset_data_by_symbol = query_historical_data(
        stock_data=symbol_data, period=selected_period, interval=selected_interval,
        use_local_usd=use_local_usd_data, use_local_ars=use_local_ars_data, use_ext_usd=use_ext_usd_data)

    for symbol, df in asset_data_by_symbol.items():
        asset_data_by_symbol[symbol] = df.round(2)

    fig_area_plot = area_plot(asset_data_by_symbol)
    st.plotly_chart(fig_area_plot)

    fig_candle_plot = candle_plot(asset_data_by_symbol)
    st.plotly_chart(fig_candle_plot)
