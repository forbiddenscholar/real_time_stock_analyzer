import streamlit as st
import pandas as pd
import os
import subprocess
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Stock Analyzer")

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
OUTPUT_CSV = os.path.join(DATA_DIR, "output.csv")
FINAL_CSV = os.path.join(DATA_DIR, "final.csv")
CUSTOM_CSV = os.path.join(DATA_DIR, "custom.csv")
DATES_CSV = os.path.join(DATA_DIR, "dates_mapping.csv")

def needs_recompile():
    if not os.path.exists(APP_EXE) or not os.path.exists(NGE_EXE):
        return True
    
    exe_mtime = min(os.path.getmtime(APP_EXE), os.path.getmtime(NGE_EXE))
    src_files = [os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR) if f.endswith(".cpp")]
    hdr_files = [os.path.join(INCLUDE_DIR, f) for f in os.listdir(INCLUDE_DIR) if f.endswith(".h")]
    
    for f in src_files + hdr_files:
        if os.path.getmtime(f) > exe_mtime:
            return True
    return False

# ---------------- SIDEBAR: INPUT ----------------
st.sidebar.title("Input configuration")

option = st.sidebar.radio(
    "Choose Data Source",
    ["Nifty 50 Data", "Sample Data", "Manual Input"]
)

input_path = None

if option == "Nifty 50 Data":
    if os.path.exists(NIFTY_DIR):
        files = [f for f in os.listdir(NIFTY_DIR) if f.endswith(".csv")]
        selected_file = st.sidebar.selectbox("Search & Select Nifty50 Stock", files)
        
        if selected_file:
            df_nifty = pd.read_csv(os.path.join(NIFTY_DIR, selected_file), header=[0, 1], index_col=0)
            df_nifty.index = pd.to_datetime(df_nifty.index)
            prices_series = df_nifty["Close"].iloc[:, 0].dropna()
            
            min_date = prices_series.index.min().date()
            max_date = prices_series.index.max().date()
            
            # Default to 1 Year Backwards
            default_start = max_date - pd.Timedelta(days=365)
            if default_start < min_date:
                default_start = min_date
            
            start_date = st.sidebar.date_input("Purchase Date", value=default_start, min_value=min_date, max_value=max_date)
            period = st.sidebar.slider("Time Period to Analyze (Days)", min_value=10, max_value=365, value=365)
            
            end_date = start_date + pd.Timedelta(days=period)
            
            mask = (prices_series.index.date >= start_date) & (prices_series.index.date <= end_date)
            sliced_series = prices_series.loc[mask]
            
            if sliced_series.empty:
                st.sidebar.error("No trading days found in this range.")
            else:
                pd.DataFrame({"price": sliced_series.values}).to_csv(CUSTOM_CSV, index=False)
                # Map real dates
                pd.DataFrame({"Date": sliced_series.index.strftime('%Y-%m-%d')}).to_csv(DATES_CSV, index=False)
                input_path = CUSTOM_CSV
    else:
        st.sidebar.warning("Nifty 50 data folder not found.")

elif option == "Sample Data":
    file_choice = st.sidebar.selectbox("Dataset", ["sample_1.csv", "sample_2.csv", "sample_3.csv"])
    input_path = os.path.join(DATA_DIR, file_choice)
    # Generate backup sequence dates
    try:
        sample_df = pd.read_csv(input_path)
        pd.DataFrame({"Date": [f"Day {i}" for i in range(len(sample_df))]}).to_csv(DATES_CSV, index=False)
    except Exception:
        pass

else:
    user_input = st.sidebar.text_area("Enter prices (comma-separated)", "100,80,60,70,75,85")
    try:
        prices = [float(x.strip()) for x in user_input.split(",") if x.strip()]
    except ValueError:
        st.sidebar.error("Invalid input! Enter comma-separated numbers.")
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

    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    if needs_recompile():
        with st.spinner("🔨 Building C++ Analyzers..."):

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
                
        st.toast("✅ Build complete!", icon='🔨')
    else:
        st.toast("✅ Using cached executables (instant run).", icon='⚡')
        
    with st.spinner("⚙️ Running analyzer..."):
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

    st.toast("✅ Analysis processed instantly!", icon='📈')

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv(FINAL_CSV)

    if df.empty:
        st.warning("No data available.")
    else:
        # Re-attach the actual dates onto the DF mapping
        if os.path.exists(DATES_CSV):
            df_dates = pd.read_csv(DATES_CSV)
            if len(df_dates) == len(df):
                df["Date"] = df_dates["Date"]
            else:
                df["Date"] = df["time"]
        else:
            df["Date"] = df["time"]

        # -------- METRICS --------
        st.subheader("Real-Time Analytics")
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Current Price", round(df["price"].iloc[-1], 2))
        col2.metric("Max Profit Found", round(df["profit"].iloc[-1], 2))
        col3.metric("Last Span", df["span"].iloc[-1])
        
        # Use Heap Outputs from C++ Backend to fulfill project requirements
        heap_max = df["heap_max"].iloc[-1] if "heap_max" in df.columns else df["price"].max()
        heap_min = df["heap_min"].iloc[-1] if "heap_min" in df.columns else df["price"].min()
        
        col4.metric("Heap Tracked Max", round(heap_max, 2))
        col5.metric("Heap Tracked Min", round(heap_min, 2))

        # -------- HISTORICAL SORTING ANALYTICS --------
        SORTED_CSV = os.path.join(DATA_DIR, "sorted_prices.csv")
        if os.path.exists(SORTED_CSV):
            st.divider()
            st.subheader("Historical Analytics (C++ Merge Sort)")
            df_sorted = pd.read_csv(SORTED_CSV)
            if not df_sorted.empty:
                n = len(df_sorted)
                median = df_sorted.iloc[n//2]["sorted_price"]
                percentile25 = df_sorted.iloc[n//4]["sorted_price"]
                percentile75 = df_sorted.iloc[(n*3)//4]["sorted_price"]
                
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("Median Historic Price", round(median, 2))
                sc2.metric("25th Percentile", round(percentile25, 2))
                sc3.metric("75th Percentile", round(percentile75, 2))
            st.divider()

        # -------- GRAPH 1 (Dynamic with Plotly) --------
        st.subheader("Price Trend")
        fig_price = px.line(df, x="Date", y="price", template="plotly_white")
        # Focus strictly on min and max points so graph avoids flat zero bounding
        fig_price.update_yaxes(range=[df["price"].min() * 0.95, df["price"].max() * 1.05])
        st.plotly_chart(fig_price, use_container_width=True)

        # -------- GRAPH 2 (Span & Profit) --------
        st.subheader("Span & Profit Evolution")
        fig_metrics = go.Figure()
        fig_metrics.add_trace(go.Scatter(x=df["Date"], y=df["profit"], name="Max Profit", line=dict(color='green')))
        fig_metrics.add_trace(go.Bar(x=df["Date"], y=df["span"], name="Current Span", marker_color='blue', opacity=0.3, yaxis='y2'))
        fig_metrics.update_layout(
            template="plotly_white",
            yaxis=dict(title="Profit"),
            yaxis2=dict(title="Span", overlaying="y", side="right")
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
        
        # -------- GRAPH 3 (NEW: NGE) --------
        if "nge" in df.columns:
            st.subheader("Next Greater Element Projection")
            # Replace -1 with None for clean plotting optionally
            nge_plot = df.replace(-1, None)
            fig_nge = px.scatter(nge_plot, x="Date", y="nge", template="plotly_white")
            fig_nge.update_traces(marker=dict(size=6, color='red'))
            st.plotly_chart(fig_nge, use_container_width=True)

        # -------- TABLE --------
        st.subheader("Detailed Action Data")
        st.dataframe(df)

except FileNotFoundError:
    st.info("Select a stock and click 'Run Analyzer' to visualize data.")
