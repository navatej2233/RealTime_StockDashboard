import pandas as pd
import numpy as np
import yfinance as yf

def fetch_data_yfinance(ticker: str, period: str = "7d", interval: str = "1m") -> pd.DataFrame:
    try:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval=interval,
            progress=False,
            threads=False
        )
    except Exception:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, actions=False)

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume"
    })

    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            df[col] = np.nan

    df.index = pd.to_datetime(df.index)

    return df[["open", "high", "low", "close", "volume"]]


def SMA(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

def EMA(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()

def RSI(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=window, min_periods=window).mean()
    ma_down = down.rolling(window=window, min_periods=window).mean()
    rs = ma_up / ma_down.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)

def MACD(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = EMA(series, fast)
    ema_slow = EMA(series, slow)
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line, macd - signal_line

def compute_indicators(df: pd.DataFrame, sma_windows=None, ema_windows=None):
    if df is None or df.empty:
        return pd.DataFrame()

    if sma_windows is None: sma_windows = [20,50]
    if ema_windows is None: ema_windows = [12,26]

    df = df.copy()

    for w in sma_windows:
        df[f"sma_{w}"] = SMA(df["close"], w)

    for w in ema_windows:
        df[f"ema_{w}"] = EMA(df["close"], w)

    df["rsi_14"] = RSI(df["close"], 14)

    macd, sig, hist = MACD(df["close"])
    df["macd"] = macd
    df["macd_signal"] = sig

    return df









