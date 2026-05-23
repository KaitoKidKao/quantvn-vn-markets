from __future__ import annotations

import os

import pandas as pd

from strategy import gen_position


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def run_synthetic_check() -> pd.DataFrame:
    sample = pd.DataFrame(
        {
            "Date": ["2026-01-01"] * 80 + ["2026-01-02"] * 80,
            "time": [f"09:{i % 60:02d}:00" for i in range(160)],
            "Open": list(range(100, 180)) + list(range(180, 100, -1)),
            "High": list(range(101, 181)) + list(range(181, 101, -1)),
            "Low": list(range(99, 179)) + list(range(179, 99, -1)),
            "Close": list(range(100, 180)) + list(range(180, 100, -1)),
            "volume": [1000] * 160,
        }
    )
    result = gen_position(sample)

    required_columns = {"signal", "position"}
    missing = required_columns.difference(result.columns)
    if missing:
        raise AssertionError(f"Missing columns: {sorted(missing)}")

    invalid_signals = set(result["signal"].dropna().unique()).difference({-1, 0, 1})
    if invalid_signals:
        raise AssertionError(f"Invalid signal values: {sorted(invalid_signals)}")

    print("Synthetic check passed.")
    cols_to_print = [c for c in ["Close", "ma_fast", "ma_slow", "rsi", "ema", "high_max", "low_min", "sma_long", "sma_short", "signal", "position"] if c in result.columns]
    print(result[cols_to_print].tail())
    return result


def run_quantvn_check() -> None:
    _load_dotenv_if_available()
    api_key = os.getenv("QUANTVN_API_KEY")
    if not api_key:
        print("QUANTVN_API_KEY is not set; skipping live QuantVN data check.")
        return

    from quantvn.vn.data import get_stock_hist
    from quantvn.vn.data.utils import client
    from quantvn.vn.metrics import Backtest_Stock, Metrics
    import time

    client(apikey=api_key)
    
    df = None
    max_retries = 5
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching live data from QuantVN for symbol 'VIC' (attempt {attempt + 1}/{max_retries})...")
            df = get_stock_hist("VIC", resolution="1H")
            if df is not None and not df.empty:
                break
        except Exception as e:
            print(f"Warning: Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("\nError: All attempts to fetch live data failed due to connection issues.")
                print("Skipping live QuantVN backtest check.")
                return

    if df is None or df.empty:
        print("Warning: Retrieved DataFrame is empty. Skipping live check.")
        return

    result = gen_position(df)

    backtest = Backtest_Stock(result, pnl_type="after_fees")
    pnl = backtest.PNL()
    
    # Calculate performance metrics
    try:
        metrics = Metrics(backtest)
        sharpe = metrics.sharpe()
        max_dd = metrics.max_drawdown()
        win_rate = metrics.win_rate()
        profit_factor = metrics.profit_factor()
    except Exception as e:
        metrics = None
        print(f"Warning: Could not calculate performance metrics: {e}")

    print("\nLive QuantVN check passed.")
    cols_to_print = [c for c in ["Close", "ma_fast", "ma_slow", "rsi", "ema", "high_max", "low_min", "sma_long", "sma_short", "signal", "position"] if c in result.columns]
    print(result[cols_to_print].tail())
    print("-" * 50)
    print("BACKTEST PERFORMANCE REPORT (VIC 1H):")
    print(f"  Final PnL:                  {pnl.iloc[-1]:,.2f} VND")
    print(f"  Estimated Minimum Capital:   {backtest.estimate_minimum_capital():,.0f} VND")
    if metrics:
        print(f"  Sharpe Ratio:                {sharpe:.3f}")
        print(f"  Max Drawdown:                {max_dd*100:.2f}%")
        print(f"  Win Rate:                    {win_rate*100:.2f}%")
        if pd.notna(profit_factor):
            print(f"  Profit Factor:               {profit_factor:.3f}")
    print("-" * 50)


if __name__ == "__main__":
    run_synthetic_check()
    run_quantvn_check()
