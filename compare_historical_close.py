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


symbol_data = get_stock_info("SPY")
df1, df2, df3 = query_historical_data(stock_data=symbol_data, period="1y", interval="1d")


# Create the Plotly figure
fig = go.Figure()

for df_i, asset_symbol, c in [(df1, symbol_data.base_symbol, (44, 160, 44)),
                              (df2, symbol_data.symbol_arg_usd, (31, 119, 180)),
                              (df3, symbol_data.symbol_arg, (255, 127, 14))
                              ]:
    # Add the price line
    fig.add_trace(go.Scatter(x=df_i.index, y=df_i['Close'], mode='lines', name=asset_symbol, line_color=f'rgb{c}'))

    # Add the high-low area
    fig.add_trace(go.Scatter(x=df_i.index, y=df_i['Low'], mode='lines', name='low', hoverinfo='skip', showlegend=False,
                             line_color=f'rgba({c[0]},{c[1]},{c[2]},0)'))

    fig.add_trace(go.Scatter(x=df_i.index, y=df_i['High'], mode='none', fill='tonexty',
                             fillcolor=f'rgba({c[0]},{c[1]},{c[2]},0.2)',
                             name='High-Low', hoverinfo='skip', showlegend=False))
# Set the layout
fig.update_layout(title='Asset Price', xaxis=dict(title='Date'), yaxis=dict(title='Price'), showlegend=True)

# Display the plot using Streamlit
st.plotly_chart(fig)

# Create the Plotly figure
fig = go.Figure()
for df_i, asset_symbol, c in [(df1, symbol_data.base_symbol, (44, 160, 44)),
                              (df2, symbol_data.symbol_arg_usd, (31, 119, 180)),
                              (df3, symbol_data.symbol_arg, (255, 127, 14))
                              ]:
    fig.add_trace(
        go.Candlestick(x=df_i.index, open=df_i.Open, high=df_i.High, low=df_i.Low, close=df_i.Close, name=asset_symbol,
                       increasing=dict(line=dict(color=f'rgb({c[0]},{c[1]},{c[2] + 30})')),
                       decreasing=dict(line=dict(color='red')),
                       ))

# Set the layout
fig.update_layout(title='Asset Price', xaxis=dict(title='Date'), yaxis=dict(title='Price'), showlegend=True)

# Display the plot using Streamlit
st.plotly_chart(fig)


# # df4 = (df2["Adj Close"] / df1["Adj Close"] - 1)
# # plt.plot(df3.index, df4, label="Stock 2")
# # plt.show()
