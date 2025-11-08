import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import fetch_data_yfinance, compute_indicators

st.set_page_config(layout="wide", page_title="Real-Time Stock Dashboard")
st.title("📈 Real-Time Stock Market Dashboard")

with st.sidebar:
    st.header("Settings")
    tickers_input = st.text_input("Tickers (comma separated)", value="AAPL,MSFT,GOOGL")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    interval = st.selectbox("Interval", ["1m","2m","5m","15m","30m","60m","1d"], index=6)
    period = st.selectbox("Period", ["1d","5d","7d","1mo","3mo","6mo","1y"], index=2)

    show_candles = st.checkbox("Candlestick chart", True)
    sma_windows = st.multiselect("SMA windows", [5,10,20,50,100,200], default=[20,50])
    ema_windows = st.multiselect("EMA windows", [5,10,12,20,26,50,100,200], default=[12,26])

    show_rsi = st.checkbox("Show RSI", True)
    show_macd = st.checkbox("Show MACD", True)

cols = st.columns(min(len(tickers), 3))

for i, ticker in enumerate(tickers):
    with cols[i % len(cols)]:
        st.subheader(ticker)

        df = fetch_data_yfinance(ticker, period=period, interval=interval)

        if df.empty:
            st.warning(f"No Data for {ticker}")
            continue

        # normalize column names (fix tuple case)
        df.columns = [c[0].lower() if isinstance(c, tuple) else c.lower() for c in df.columns]

        if "close" not in df.columns and "adj_close" in df.columns:
            df["close"] = df["adj_close"]

        df_ind = compute_indicators(df.copy(), sma_windows=sma_windows, ema_windows=ema_windows)

        # KPIs
        latest = df_ind.iloc[-1]
        prev = df_ind.iloc[-2] if len(df_ind) > 1 else latest
        k1, k2, k3 = st.columns(3)
        k1.metric("Price", f"{latest['close']:.2f}", f"{(latest['close'] - prev['close']):+.2f}")
        k2.metric("High", f"{df_ind['high'].max():.2f}")
        k3.metric("Low", f"{df_ind['low'].min():.2f}")

        # CANDLE
        fig = go.Figure()
        if show_candles:
            fig.add_trace(go.Candlestick(
                x=df_ind.index,
                open=df_ind['open'],
                high=df_ind['high'],
                low=df_ind['low'],
                close=df_ind['close']
            ))
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True, key=f"candle_{ticker}")

       # VOLUME
vol = px.bar(df_ind, x=df_ind.index, y="volume")
vol.update_layout(height=200)
st.plotly_chart(vol, use_container_width=True, key=f"volume_{ticker}")

# RSI
if show_rsi and "rsi_14" in df_ind.columns:
    rsi_fig = px.line(df_ind, x=df_ind.index, y="rsi_14")
    rsi_fig.update_layout(height=200)
    st.plotly_chart(rsi_fig, use_container_width=True, key=f"rsi_{ticker}")

# MACD
if show_macd:
    macd_fig = px.line(df_ind, x=df_ind.index, y=["macd","macd_signal"])
    macd_fig.update_layout(height=200)
    st.plotly_chart(macd_fig, use_container_width=True, key=f"macd_{ticker}")


st.write("---")
st.write("Developed with ❤️")











