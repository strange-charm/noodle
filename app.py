import streamlit as st
import requests
import pandas as pd
import time

# Use Streamlit Secrets for API key
API_KEY = st.secrets["FMP_API_KEY"]

st.set_page_config(page_title="Momentum Scanner", layout="wide")
st.title("📈 Momentum Stock Scanner")

# --- Sidebar Filters ---
st.sidebar.header("Filter Criteria")
exchange = st.sidebar.selectbox(
    "Exchange",
    ["NASDAQ", "NYSE", "AMEX", "LSE", "TSX", "EURONEXT", "HKG", "CRYPTO"],
    index=0
)
min_change = st.sidebar.slider("Min % Change", 1.0, 10.0, 3.0)
volume_multiplier = st.sidebar.slider("Min Volume Spike (x Avg Vol)", 1.0, 10.0, 2.0)
rsi_range = st.sidebar.slider("RSI Range", 0, 100, (30, 70))

# --- Functions ---
def get_tickers(exchange):
    url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange={exchange}&limit=50&apikey={API_KEY}"
    r = requests.get(url)
    return [item['symbol'] for item in r.json()] if r.ok else []

def get_quote(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={API_KEY}"
    r = requests.get(url)
    if r.ok and r.json():
        return r.json()[0]
    return None

def get_rsi(ticker):
    url = f"https://financialmodelingprep.com/api/v4/technical_indicator/daily/{ticker}?period=10&type=rsi&apikey={API_KEY}"
    r = requests.get(url)
    if r.ok and r.json():
        return r.json()[-1]['rsi']
    return None

def scan_momentum_stocks(tickers):
    results = []
    for ticker in tickers:
        quote = get_quote(ticker)
        rsi = get_rsi(ticker)
        if quote and rsi:
            if (
                quote['volume'] > volume_multiplier * quote['avgVolume'] and
                quote['changesPercentage'] > min_change and
                rsi_range[0] <= rsi <= rsi_range[1]
            ):
                results.append({
                    'Ticker': ticker,
                    'Price': quote['price'],
                    'Change %': quote['changesPercentage'],
                    'Volume': quote['volume'],
                    'Avg Vol': quote['avgVolume'],
                    'RSI': round(rsi, 2)
                })
        time.sleep(0.5)  # API rate limit delay
    return pd.DataFrame(results)

# --- Main ---
if st.button("🔄 Scan Now"):
    with st.spinner("Scanning for momentum stocks..."):
        tickers = get_tickers(exchange)
        df = scan_momentum_stocks(tickers)
        if not df.empty:
            st.success(f"Found {len(df)} matching stocks!")
            st.dataframe(df.sort_values("Change %", ascending=False), use_container_width=True)
        else:
            st.warning("No stocks matched your criteria.")