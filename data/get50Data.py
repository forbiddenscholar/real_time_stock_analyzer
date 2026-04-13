import yfinance as yf
import pandas as pd
import time
import os
from datetime import timedelta

# The complete list of NIFTY 50 stock tickers (Using the updated tickers)
nifty50_tickers = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TMPV.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "ETERNAL.NS", "^NSEI"
]

# Create the folder to hold the CSVs locally
folder_name = "Nifty50_Data"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

print(f"Checking and updating {len(nifty50_tickers)} stocks...")

for ticker in nifty50_tickers:
    clean_name = "NIFTY50" if ticker == "^NSEI" else ticker.replace('.NS', '')
    filepath = os.path.join(folder_name, f"{clean_name}_data.csv")

    try:
        # SCENARIO A: The file already exists
        if os.path.exists(filepath):
            # 1. Read the existing CSV to find the last date we downloaded
            df_existing = pd.read_csv(filepath)
            
            # Make sure the file isn't empty before proceeding
            if not df_existing.empty:
                # yfinance recent updates changed column headers to a MultiIndex (Price, Ticker, Date)
                # so 'Date' is no longer the column header name for row 0.
                # Safe fallback: The date strings are always in the first column (index 0).
                last_date_str = str(df_existing.iloc[-1, 0])
                
                # Convert that string to a real date object and add 1 day
                last_date = pd.to_datetime(last_date_str)
                next_date = last_date + timedelta(days=1)
                
                # 2. Download ONLY the new data from 'next_date' to today
                new_data = yf.download(ticker, start=next_date.strftime('%Y-%m-%d'), progress=False)
                
                # 3. If there is new data, append it to the bottom of the CSV
                if not new_data.empty:
                    # mode='a' means "append". header=False ensures we don't print "Date,Open..." again
                    new_data.to_csv(filepath, mode='a', header=False)
                    print(f"[{clean_name}] Updated with {len(new_data)} new days of data.")
                else:
                    print(f"[{clean_name}] Already up to date.")
            else:
                print(f"[{clean_name}] File is empty. Please delete it so it can redownload.")

        # SCENARIO B: The file does not exist yet (First time running for this stock)
        else:
            print(f"[{clean_name}] No existing file found. Downloading full history...")
            stock_data = yf.download(ticker, period='max', progress=False)
            stock_data.to_csv(filepath)

        # Pause for 1 second so Yahoo Finance doesn't block your IP
        time.sleep(1)

    except Exception as e:
        print(f"Failed to process {ticker}: {e}")

print("\nAll files are synced and ready for your C++ program!")