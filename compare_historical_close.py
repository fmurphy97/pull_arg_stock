import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import seaborn as sns
import plotly.express as px

stock = "SPY"
period = "1y"
interval = "1d"
metric = "Adj Close"
stock_data = pd.read_csv("data/inputs/cedear_ratios.csv", index_col="symbol").loc[stock, :]

stock2 = stock_data.symbol_arg_usd
stock3 = stock_data.symbol_arg

df1 = yf.download(stock, period=period, interval=interval) / stock_data.ratio
df2 = yf.download(stock2, period=period, interval=interval)
df3 = yf.download(stock3, period=period, interval=interval)

fig, ax1 = plt.subplots(figsize=(20, 8))

# Plot the first stock from df1
sns.lineplot(data=df1, x=df1.index, y=df1[metric], label=stock, color="green", ax=ax1, alpha=0.5)
ax1.fill_between(df1.index, df1['Low'], df1['High'], color='green', alpha=0.1)

# Plot the second stock from df2
sns.lineplot(data=df2, x=df2.index, y=df2[metric], label=stock2, color="orange", ax=ax1, alpha=0.5)
ax1.fill_between(df2.index, df2['Low'], df2['High'], color='orange', alpha=0.1)

historic_ccl = pd.read_csv("data/inputs/dolar_ccl_historic.csv", index_col="Fecha")
historic_ccl.index = pd.to_datetime(historic_ccl.index)

# Merge the two DataFrames based on the 'id' column
df3 = df3.merge(historic_ccl, left_index=True, right_index=True)

# Divide each row in merged_df
for col_name in [metric, "Low", "High"]:
    df3[col_name] = df3[col_name]/df3["Referencia"]

# Plot the second stock from df3
sns.lineplot(data=df3, x=df3.index, y=df3[metric], label=stock3, color="blue", ax=ax1, alpha=0.5)
ax1.fill_between(df3.index, df3['Low'], df3['High'], color='blue', alpha=0.1)

# Add labels and legend
plt.xlabel("Date")
plt.ylabel("Adj Close Price")
plt.title("Stock Price Comparison")
plt.legend()
plt.gcf().set_dpi(300)
# Show the plot
plt.show()

# df3 = (df2["Adj Close"] / df1["Adj Close"] - 1)
# plt.plot(df3.index, df3, label="Stock 2")
# plt.show()

