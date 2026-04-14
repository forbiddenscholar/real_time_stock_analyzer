import os
import subprocess
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")
st.title("Stock Analyzer Dashboard")

# ================ PATHS ================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_DIR, "src")
INCLUDE_DIR = os.path.join(PROJECT_DIR, "include")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
NIFTY_DIR = os.path.join(DATA_DIR, "Nifty50_Data")

APP_EXE = os.path.join(BUILD_DIR, "app.exe")
NGE_EXE = os.path.join(BUILD_DIR, "nge.exe")
FINAL_CSV = os.path.join(DATA_DIR, "final.csv")
CUSTOM_CSV = os.path.join(DATA_DIR, "custom.csv")
DATES_CSV = os.path.join(DATA_DIR, "dates_mapping.csv")
SORTED_CSV = os.path.join(DATA_DIR, "sorted_prices.csv")


def init_state():
    defaults = {
        "sim_running": False,
        "sim_started": False,
        "sim_index": 0,
        "sim_start_index": 0,
        "sim_end_index": 0,
        "sim_gap_seconds": 1,
        "sim_dataset_signature": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def needs_recompile():
    if not os.path.exists(APP_EXE) or not os.path.exists(NGE_EXE):
        return True

    exe_mtime = min(os.path.getmtime(APP_EXE), os.path.getmtime(NGE_EXE))
    src_files = [os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR) if f.endswith(".cpp")]
    hdr_files = [os.path.join(INCLUDE_DIR, f) for f in os.listdir(INCLUDE_DIR) if f.endswith(".h")]

    for file_path in src_files + hdr_files:
        if os.path.getmtime(file_path) > exe_mtime:
            return True
    return False


def reset_simulation_state(dataset_signature):
    st.session_state["sim_running"] = False
    st.session_state["sim_started"] = False
    st.session_state["sim_index"] = 0
    st.session_state["sim_start_index"] = 0
    st.session_state["sim_end_index"] = 0
    st.session_state["sim_gap_seconds"] = 1
    st.session_state["sim_dataset_signature"] = dataset_signature


def ensure_simulation_state(df):
    dataset_signature = f"{len(df)}::{df['Date'].iloc[0]}::{df['Date'].iloc[-1]}"
    if st.session_state.get("sim_dataset_signature") != dataset_signature:
        reset_simulation_state(dataset_signature)


def load_analysis_data():
    if not os.path.exists(FINAL_CSV):
        return None

    df = pd.read_csv(FINAL_CSV)
    if df.empty:
        return df

    if os.path.exists(DATES_CSV):
        df_dates = pd.read_csv(DATES_CSV)
        if len(df_dates) == len(df):
            df["Date"] = df_dates["Date"].astype(str)
        else:
            df["Date"] = df["time"].astype(str)
    else:
        df["Date"] = df["time"].astype(str)

    return df


def build_and_run_analyzers(input_path):
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    if needs_recompile():
        with st.spinner("Building C++ analyzers..."):
            app_sources = [
                os.path.join(SRC_DIR, "main.cpp"),
                os.path.join(SRC_DIR, "Analyzer.cpp"),
                os.path.join(SRC_DIR, "Stream.cpp"),
                os.path.join(SRC_DIR, "FileManager.cpp"),
            ]
            app_cmd = ["g++", "-std=c++14", f"-I{INCLUDE_DIR}"] + app_sources + ["-o", APP_EXE]
            run_app_build = subprocess.run(app_cmd, cwd=PROJECT_DIR, capture_output=True, text=True)

            if run_app_build.returncode != 0:
                st.error("Build failed for app.exe")
                st.text(run_app_build.stderr)
                st.stop()

            nge_cmd = ["g++", "-std=c++14", os.path.join(SRC_DIR, "NGEProcessor.cpp"), "-o", NGE_EXE]
            run_nge_build = subprocess.run(nge_cmd, cwd=PROJECT_DIR, capture_output=True, text=True)

            if run_nge_build.returncode != 0:
                st.error("Build failed for nge.exe")
                st.text(run_nge_build.stderr)
                st.stop()

        st.toast("Build complete.", icon="🔧")
    else:
        st.toast("Using cached executables.", icon="⚡")

    with st.spinner("Running C++ analysis pipeline..."):
        run_app = subprocess.run([APP_EXE, input_path], cwd=PROJECT_DIR, capture_output=True, text=True)
        if run_app.returncode != 0:
            st.error("Execution failed for app.exe")
            st.text(run_app.stderr)
            st.stop()

        run_nge = subprocess.run([NGE_EXE], cwd=PROJECT_DIR, capture_output=True, text=True)
        if run_nge.returncode != 0:
            st.error("Execution failed for nge.exe")
            st.text(run_nge.stderr)
            st.stop()

    st.toast("Analysis processed.", icon="📈")


def format_trade_date(df, index_value):
    if pd.isna(index_value):
        return "Not found yet"

    try:
        row_index = int(index_value)
    except (TypeError, ValueError):
        return "Not found yet"

    if row_index < 0 or row_index >= len(df):
        return "Not found yet"

    return str(df.iloc[row_index]["Date"])


def add_trade_markers(fig, df, buy_index, sell_index):
    marker_x = []
    marker_y = []
    marker_text = []
    marker_color = []

    for label, row_index, color in [
        ("Best Buy", buy_index, "green"),
        ("Best Sell", sell_index, "red"),
    ]:
        if row_index is None:
            continue
        if row_index < 0 or row_index >= len(df):
            continue

        row = df.iloc[row_index]
        marker_x.append(row["Date"])
        marker_y.append(row["price"])
        marker_text.append(label)
        marker_color.append(color)

    if marker_x:
        fig.add_trace(
            go.Scatter(
                x=marker_x,
                y=marker_y,
                mode="markers+text",
                text=marker_text,
                textposition="top center",
                marker=dict(size=12, color=marker_color, symbol="diamond"),
                name="Trade Markers",
            )
        )


def render_overview_tab(df):
    st.subheader("Real-Time Analytics")
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Current Price", round(df["price"].iloc[-1], 2))
    col2.metric("Max Profit Found", round(df["profit"].iloc[-1], 2))
    col3.metric("Last Span", int(df["span"].iloc[-1]))
    col4.metric("Heap Tracked Max", round(df["heap_max"].iloc[-1], 2))
    col5.metric("Heap Tracked Min", round(df["heap_min"].iloc[-1], 2))

    best_buy_index = int(df["best_buy_index"].iloc[-1]) if "best_buy_index" in df.columns else -1
    best_sell_index = int(df["best_sell_index"].iloc[-1]) if "best_sell_index" in df.columns else -1

    if os.path.exists(SORTED_CSV):
        df_sorted = pd.read_csv(SORTED_CSV)
        if not df_sorted.empty:
            st.divider()
            st.subheader("Historical Analytics (C++ Merge Sort)")
            n = len(df_sorted)
            median = df_sorted.iloc[n // 2]["sorted_price"]
            percentile25 = df_sorted.iloc[n // 4]["sorted_price"]
            percentile75 = df_sorted.iloc[(n * 3) // 4]["sorted_price"]

            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Median Historic Price", round(median, 2))
            sc2.metric("25th Percentile", round(percentile25, 2))
            sc3.metric("75th Percentile", round(percentile75, 2))

    st.divider()
    st.subheader("Price Trend")
    fig_price = px.line(df, x="Date", y="price", template="plotly_white")
    fig_price.update_yaxes(range=[df["price"].min() * 0.95, df["price"].max() * 1.05])
    add_trade_markers(fig_price, df, best_buy_index, best_sell_index)
    st.plotly_chart(fig_price, use_container_width=True)

    st.subheader("Span & Profit Evolution")
    fig_metrics = go.Figure()
    fig_metrics.add_trace(go.Scatter(x=df["Date"], y=df["profit"], name="Max Profit", line=dict(color="green")))
    fig_metrics.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["span"],
            name="Current Span",
            marker_color="blue",
            opacity=0.3,
            yaxis="y2",
        )
    )
    fig_metrics.update_layout(
        template="plotly_white",
        yaxis=dict(title="Profit"),
        yaxis2=dict(title="Span", overlaying="y", side="right"),
    )
    st.plotly_chart(fig_metrics, use_container_width=True)

    if "nge" in df.columns:
        st.subheader("Next Greater Element Projection")
        nge_plot = df.copy()
        nge_plot["nge_plot"] = nge_plot["nge"].replace(-1, None)
        fig_nge = px.scatter(nge_plot, x="Date", y="nge_plot", template="plotly_white")
        fig_nge.update_traces(marker=dict(size=6, color="red"))
        st.plotly_chart(fig_nge, use_container_width=True)

    st.subheader("Detailed Action Data")
    st.dataframe(df, use_container_width=True)


def render_simulation_tab(df):
    st.subheader("Real-Time Data Input Simulation")

    start_index = 0
    max_days = len(df) - start_index
    control_col1, control_col2 = st.columns([4, 1])
    days_to_simulate = control_col1.slider("Days To Simulate", min_value=1, max_value=max_days, value=min(max_days, 30))
    gap_seconds = control_col2.selectbox(
        "Gap (Sec)",
        options=[1, 2, 3, 4, 5],
        index=max(0, min(4, int(st.session_state["sim_gap_seconds"]) - 1)),
    )

    start_stop_label = "Stop" if st.session_state["sim_started"] else "Start"
    pause_resume_label = "Pause" if st.session_state["sim_running"] else "Resume"
    button_col1, button_col2, _ = st.columns([2, 2, 6])

    if button_col1.button(start_stop_label, key="sim_start_stop_button", use_container_width=True):
        if st.session_state["sim_started"]:
            st.session_state["sim_running"] = False
            st.session_state["sim_started"] = False
            st.session_state["sim_start_index"] = start_index
            st.session_state["sim_end_index"] = start_index + days_to_simulate - 1
            st.session_state["sim_index"] = start_index
            st.session_state["sim_gap_seconds"] = gap_seconds
        else:
            st.session_state["sim_started"] = True
            st.session_state["sim_running"] = True
            st.session_state["sim_start_index"] = start_index
            st.session_state["sim_end_index"] = start_index + days_to_simulate - 1
            st.session_state["sim_index"] = start_index
            st.session_state["sim_gap_seconds"] = gap_seconds
        st.rerun()

    pause_disabled = not st.session_state["sim_started"]
    if button_col2.button(
        pause_resume_label,
        key="sim_pause_resume_button",
        disabled=pause_disabled,
        use_container_width=True,
    ):
        if st.session_state["sim_running"]:
            st.session_state["sim_running"] = False
        else:
            st.session_state["sim_running"] = True
        st.session_state["sim_gap_seconds"] = gap_seconds
        st.rerun()

    if not st.session_state["sim_started"]:
        st.session_state["sim_start_index"] = start_index
        st.session_state["sim_end_index"] = start_index + days_to_simulate - 1
        st.session_state["sim_index"] = start_index
        st.session_state["sim_gap_seconds"] = gap_seconds

    sim_start_index = st.session_state["sim_start_index"]
    sim_end_index = min(st.session_state["sim_end_index"], len(df) - 1)
    sim_index = min(max(st.session_state["sim_index"], sim_start_index), sim_end_index)

    visible_df = df.iloc[sim_start_index : sim_index + 1].copy()
    current_row = visible_df.iloc[-1]
    current_buy_index = int(current_row["best_buy_index"]) if "best_buy_index" in current_row else -1
    current_sell_index = int(current_row["best_sell_index"]) if "best_sell_index" in current_row else -1

    progress_value = (sim_index - sim_start_index + 1) / (sim_end_index - sim_start_index + 1)
    st.progress(progress_value)

    metric1, metric2, metric3, metric4, metric5 = st.columns(5)
    metric1.metric("Current Simulated Date", str(current_row["Date"]))
    metric2.metric("Current Price", round(float(current_row["price"]), 2))
    metric3.metric("Live Max Profit", round(float(current_row["profit"]), 2))
    metric4.metric("Live Best Buy Date", format_trade_date(df, current_buy_index))
    metric5.metric("Live Best Sell Date", format_trade_date(df, current_sell_index))

    if st.session_state["sim_running"]:
        status_text = "Running"
    elif st.session_state["sim_started"]:
        status_text = "Paused"
    else:
        status_text = "Stopped"
    st.caption(
        f"Status: {status_text} | Step {sim_index - sim_start_index + 1} of {sim_end_index - sim_start_index + 1} | Gap: {st.session_state['sim_gap_seconds']} sec"
    )

    sim_fig = px.line(visible_df, x="Date", y="price", template="plotly_white")
    sim_fig.update_yaxes(range=[df["price"].min() * 0.95, df["price"].max() * 1.05])
    add_trade_markers(sim_fig, df, current_buy_index, current_sell_index)
    st.plotly_chart(sim_fig, use_container_width=True)

    sim_metrics = go.Figure()
    sim_metrics.add_trace(
        go.Scatter(
            x=visible_df["Date"],
            y=visible_df["profit"],
            name="Live Max Profit",
            line=dict(color="green"),
        )
    )
    sim_metrics.add_trace(
        go.Bar(
            x=visible_df["Date"],
            y=visible_df["span"],
            name="Live Span",
            marker_color="royalblue",
            opacity=0.35,
            yaxis="y2",
        )
    )
    sim_metrics.update_layout(
        template="plotly_white",
        yaxis=dict(title="Profit"),
        yaxis2=dict(title="Span", overlaying="y", side="right"),
    )
    st.plotly_chart(sim_metrics, use_container_width=True)

    st.subheader("Simulated Stream Output")
    display_df = visible_df.drop(columns=["best_buy_index", "best_sell_index"], errors="ignore")
    st.dataframe(display_df, use_container_width=True)

    if st.session_state["sim_running"]:
        if sim_index < sim_end_index:
            time.sleep(st.session_state["sim_gap_seconds"])
            st.session_state["sim_index"] = sim_index + 1
            st.rerun()
        else:
            st.session_state["sim_running"] = False
            st.session_state["sim_started"] = False
            st.success("Simulation completed.")


init_state()

# ---------------- SIDEBAR: INPUT ----------------
st.sidebar.title("Input Configuration")

option = st.sidebar.radio("Choose Data Source", ["Nifty 50 Data", "Sample Data", "Manual Input"])
input_path = None

if option == "Nifty 50 Data":
    if os.path.exists(NIFTY_DIR):
        files = sorted([file_name for file_name in os.listdir(NIFTY_DIR) if file_name.endswith(".csv")])
        selected_file = st.sidebar.selectbox("Search & Select Nifty50 Stock", files)

        if selected_file:
            df_nifty = pd.read_csv(os.path.join(NIFTY_DIR, selected_file), header=[0, 1], index_col=0)
            df_nifty.index = pd.to_datetime(df_nifty.index)
            prices_series = df_nifty["Close"].iloc[:, 0].dropna()

            min_date = prices_series.index.min().date()
            max_date = prices_series.index.max().date()

            default_start = max_date - pd.Timedelta(days=365)
            if default_start < min_date:
                default_start = min_date

            start_date = st.sidebar.date_input(
                "Purchase Date",
                value=default_start,
                min_value=min_date,
                max_value=max_date,
            )
            period = st.sidebar.slider("Time Period to Analyze (Days)", min_value=10, max_value=365, value=365)

            end_date = start_date + pd.Timedelta(days=period)
            mask = (prices_series.index.date >= start_date) & (prices_series.index.date <= end_date)
            sliced_series = prices_series.loc[mask]

            if sliced_series.empty:
                st.sidebar.error("No trading days found in this range.")
            else:
                pd.DataFrame({"price": sliced_series.values}).to_csv(CUSTOM_CSV, index=False)
                pd.DataFrame({"Date": sliced_series.index.strftime("%Y-%m-%d")}).to_csv(DATES_CSV, index=False)
                input_path = CUSTOM_CSV
    else:
        st.sidebar.warning("Nifty 50 data folder not found.")

elif option == "Sample Data":
    sample_files = sorted(
        [file_name for file_name in os.listdir(DATA_DIR) if file_name.startswith("sample_") and file_name.endswith(".csv")]
    )
    file_choice = st.sidebar.selectbox("Dataset", sample_files)
    input_path = os.path.join(DATA_DIR, file_choice)
    try:
        sample_df = pd.read_csv(input_path)
        pd.DataFrame({"Date": [f"Day {i}" for i in range(len(sample_df))]}).to_csv(DATES_CSV, index=False)
    except Exception:
        pass

else:
    user_input = st.sidebar.text_area("Enter prices (comma-separated)", "100,80,60,70,75,85")
    try:
        prices = [float(value.strip()) for value in user_input.split(",") if value.strip()]
    except ValueError:
        st.sidebar.error("Invalid input. Enter comma-separated numbers.")
        prices = []

    if prices:
        pd.DataFrame({"price": prices}).to_csv(CUSTOM_CSV, index=False)
        pd.DataFrame({"Date": [f"Day {i}" for i in range(len(prices))]}).to_csv(DATES_CSV, index=False)
        input_path = CUSTOM_CSV

# ---------------- RUN ----------------
if st.sidebar.button("Run Analyzer"):
    if not input_path or not os.path.exists(input_path):
        st.error("Invalid input path. Please select correct data.")
        st.stop()

    build_and_run_analyzers(input_path)
    if os.path.exists(FINAL_CSV):
        refreshed_df = load_analysis_data()
        if refreshed_df is not None and not refreshed_df.empty:
            ensure_simulation_state(refreshed_df)

# ---------------- LOAD DATA ----------------
df = load_analysis_data()

if df is None:
    st.info("Select a stock and click 'Run Analyzer' to visualize data.")
elif df.empty:
    st.warning("No data available.")
else:
    ensure_simulation_state(df)
    overview_tab, simulation_tab = st.tabs(["Dashboard Overview", "Simulation Replay"])

    with overview_tab:
        render_overview_tab(df)

    with simulation_tab:
        render_simulation_tab(df)
