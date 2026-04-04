import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(layout="wide")
st.title("📈 Stock Analyzer")

# ---------------- INPUT ----------------
st.sidebar.title("Input")

option = st.sidebar.radio(
    "Choose Input",
    ["Sample Data", "Manual Input"]
)

if option == "Sample Data":
    file_choice = st.sidebar.selectbox(
        "Dataset",
        ["sample_1.csv", "sample_2.csv", "sample_3.csv"]
    )
    input_path = f"../data/{file_choice}"

else:
    user_input = st.sidebar.text_area(
        "Enter prices",
        "100,80,60,70,75,85"
    )

    prices = [int(x.strip()) for x in user_input.split(",")]

    input_path = "../data/custom.csv"
    pd.DataFrame({"price": prices}).to_csv(input_path, index=False)

# ---------------- RUN ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "../src")
BUILD_DIR = os.path.join(BASE_DIR, "../build")
input_path = os.path.abspath(input_path)

if st.sidebar.button("Run Analyzer"):

    st.info("Building...")

    # Create build directory if it doesn't exist
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    # Configure with CMake
    cmake_config = subprocess.run(
        ["cmake", ".."],
        cwd=BUILD_DIR,
        capture_output=True,
        text=True
    )

    if cmake_config.returncode != 0:
        st.error("CMake configuration failed")
        st.text(cmake_config.stderr)
        st.stop()

    # Build with make
    cmake_build = subprocess.run(
        ["make"],
        cwd=BUILD_DIR,
        capture_output=True,
        text=True
    )

    if cmake_build.returncode != 0:
        st.error("Build failed")
        st.text(cmake_build.stderr)
        st.stop()

    st.success("Build complete!")
    st.info("Running analyzer...")

    # Run app
    run_app = subprocess.run(
        [os.path.join(BUILD_DIR, "app"), input_path],
        cwd=SRC_DIR,
        capture_output=True,
        text=True
    )

    st.text(run_app.stdout)

    # Run nge
    run_nge = subprocess.run(
        [os.path.join(BUILD_DIR, "nge")],
        cwd=SRC_DIR,
        capture_output=True,
        text=True
    )

    st.text(run_nge.stdout)

    st.success("Processing complete!")

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("../data/final.csv")

    if df.empty:
        st.warning("No data available.")
    else:
        # -------- METRICS --------
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Price", df["price"].iloc[-1])
        col2.metric("Profit", df["profit"].iloc[-1])
        col3.metric("Span", df["span"].iloc[-1])
        col4.metric("Max Price", df["price"].max())
        col5.metric("Min Price", df["price"].min())

        # -------- GRAPH 1 --------
        st.subheader("Price Trend")
        st.line_chart(df.set_index("time")["price"])

        # -------- GRAPH 2 --------
        st.subheader("Span & Profit")
        st.line_chart(df.set_index("time")[["span", "profit"]])

        # -------- TABLE --------
        st.subheader("Data")
        st.dataframe(df)

except FileNotFoundError:
    st.warning("Click 'Run Analyzer' to generate data.")
