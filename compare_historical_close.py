import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def get_stock_info(symbol: str):
    stock_data = pd.read_csv("data/inputs/cedear_ratios.csv", index_col="symbol").loc[symbol, :]
    stock_data["base_symbol"] = symbol
    return stock_data


def query_historical_data(stock_data: pd.DataFrame, period: str, interval: str):
    foreign_usd_df = yf.download(stock_data.base_symbol, period=period, interval=interval)
    foreign_usd_adj_df = adjust_by_ratio(foreign_usd_df, stock_data.ratio)

    local_usd_df = yf.download(stock_data.symbol_arg_usd, period=period, interval=interval)

    local_ars_df = yf.download(stock_data.symbol_arg, period=period, interval=interval)
    local_ars_adj_df = adjust_local_price(local_ars_df)

    return foreign_usd_adj_df, local_usd_df, local_ars_adj_df


def adjust_by_ratio(df: pd.DataFrame, ratio: float):
    return df / ratio


def adjust_local_price(df: pd.DataFrame):
    historic_ccl = pd.read_csv("data/inputs/dolar_ccl_historic.csv", index_col="Fecha")
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
symbol_data = get_stock_info(symbol_usa)
df1, df2, df3 = query_historical_data(stock_data=symbol_data, period="1y", interval="1d")

df1 = df1.round(2)
df2 = df2.round(2)
df3 = df3.round(2)

asset_data_by_symbol = {
    symbol_data.base_symbol: df1,
    symbol_data.symbol_arg_usd: df2,
    symbol_data.symbol_arg: df3
}

fig_area_plot = area_plot(asset_data_by_symbol)
st.plotly_chart(fig_area_plot)

fig_candle_plot = candle_plot(asset_data_by_symbol)
st.plotly_chart(fig_candle_plot)

# # df4 = (df2["Adj Close"] / df1["Adj Close"] - 1)
# # plt.plot(df3.index, df4, label="Stock 2")
# # plt.show()
