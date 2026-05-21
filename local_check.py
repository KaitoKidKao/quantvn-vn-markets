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

    required_columns = {"ma_fast", "ma_slow", "signal", "position"}
    missing = required_columns.difference(result.columns)
    if missing:
        raise AssertionError(f"Missing columns: {sorted(missing)}")

    invalid_signals = set(result["signal"].dropna().unique()).difference({-1, 0, 1})
    if invalid_signals:
        raise AssertionError(f"Invalid signal values: {sorted(invalid_signals)}")

    print("Synthetic check passed.")
    print(result[["Close", "ma_fast", "ma_slow", "signal", "position"]].tail())
    return result


def run_quantvn_check() -> None:
    _load_dotenv_if_available()
    api_key = os.getenv("QUANTVN_API_KEY")
    if not api_key:
        print("QUANTVN_API_KEY is not set; skipping live QuantVN data check.")
        return

    from quantvn.vn.data import get_stock_hist
    from quantvn.vn.data.utils import client
    from quantvn.vn.metrics import Backtest_Stock

    client(apikey=api_key)
    df = get_stock_hist("VIC", resolution="1H")
    result = gen_position(df)

    backtest = Backtest_Stock(result, pnl_type="after_fees")
    pnl = backtest.PNL()
    print("Live QuantVN check passed.")
    print(result[["Close", "ma_fast", "ma_slow", "signal", "position"]].tail())
    print(f"Final PnL: {pnl.iloc[-1]:,.2f}")
    print(f"Estimated minimum capital: {backtest.estimate_minimum_capital():,.0f}")


if __name__ == "__main__":
    run_synthetic_check()
    run_quantvn_check()
