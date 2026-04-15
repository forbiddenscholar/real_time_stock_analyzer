import streamlit as st
import pandas as pd
import os
import subprocess
import yfinance as yf
import matplotlib.pyplot as plt

# fetching data from the api
def fetch_api_data(symbol="AAPL"):
    data = yf.download(symbol, period="1d", interval="1m")

    if data.empty:
        raise ValueError("No data fetched from API")

    if isinstance(data.columns, pd.MultiIndex):
        if ("Close", symbol) in data.columns:
            prices = data[("Close", symbol)]
        else:
            prices = data.xs("Close", level=0, axis=1)
    else:
        if "Close" in data.columns:
            prices = data["Close"]
        else:
            prices = data.iloc[:, 0]

    prices = prices.squeeze()
    prices = prices.dropna().reset_index(drop=True)

    df = pd.DataFrame({"price": prices.values})

    path = "../data/api.csv"
    df.to_csv(path, index=False)

    return path


st.set_page_config(layout="wide")
st.title("📈 Stock Analyzer")

stocks = [
    "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN",
    "ADANIENT.NS", "RELIANCE.NS", "TCS.NS"
]

symbol = st.sidebar.selectbox("Select Stock", stocks)

# fetch data
input_path = fetch_api_data(symbol)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "../build")
input_path = os.path.abspath(input_path)


# running the analyzer
if st.sidebar.button("Run Analyzer"):

    st.info("Building...")

    os.makedirs(BUILD_DIR, exist_ok=True)

    subprocess.run(["cmake", ".."], cwd=BUILD_DIR)
    subprocess.run(["make"], cwd=BUILD_DIR)

    st.success("Build complete!")
    st.info("Running analyzer...")

    subprocess.run(
        [os.path.join(BUILD_DIR, "app"), input_path],
        cwd=BUILD_DIR
    )

    st.success("Processing complete!")

    st.rerun()


# loading data
try:
    df = pd.read_csv("../data/output.csv")

    if not df.empty:

        # metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Price", df["price"].iloc[-1])
        col2.metric("Profit", df["profit"].iloc[-1])
        col3.metric("Span", df["span"].iloc[-1])
        col4.metric("Max Price", df["price"].max())
        col5.metric("Min Price", df["price"].min())

        # graphs
        st.subheader("Price + Buy/Sell Signals")

        fig, ax = plt.subplots()

        time_arr = df["time"].to_numpy()
        price_arr = df["price"].to_numpy()

        ax.plot(time_arr, price_arr, label="Price")

        buy_idx = int(df["buy"].iloc[-1])
        sell_idx = int(df["sell"].iloc[-1])

        if 0 <= buy_idx < len(price_arr):
            ax.scatter(
                buy_idx,
                price_arr[buy_idx],
                color="green",
                marker="^",
                s=120,
                label="Buy"
            )

        if 0 <= sell_idx < len(price_arr):
            ax.scatter(
                sell_idx,
                price_arr[sell_idx],
                color="red",
                marker="v",
                s=120,
                label="Sell"
            )

        ax.legend()
        st.pyplot(fig)

        # span and profit
        st.subheader("Span & Profit")
        st.line_chart(df.set_index("time")[["span", "profit"]])

        # data table
        st.subheader("Data")
        st.dataframe(df)

    else:
        st.warning("No data available.")

except FileNotFoundError:
    st.warning("Click 'Run Analyzer' to generate data.")