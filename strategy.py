from __future__ import annotations

import numpy as np
import pandas as pd


FAST_WINDOW = 20
SLOW_WINDOW = 50
TRADE_SIZE = 100


def _close_column(df: pd.DataFrame) -> str:
    """Return the price column used by QuantVN stock data."""
    for column in ("Close", "close"):
        if column in df.columns:
            return column
    raise KeyError("Input DataFrame must contain a 'Close' or 'close' column.")


def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """Generate MA crossover signals and target stock position.

    signal:
        1  = enter long
        -1 = exit long
        0  = no action

    position:
        Desired number of shares for QuantVN Backtest_Stock.
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    result["ma_fast"] = close.rolling(FAST_WINDOW, min_periods=FAST_WINDOW).mean()
    result["ma_slow"] = close.rolling(SLOW_WINDOW, min_periods=SLOW_WINDOW).mean()

    ready = result["ma_fast"].notna() & result["ma_slow"].notna()
    long_regime = (result["ma_fast"] > result["ma_slow"]) & ready

    position_unit = long_regime.astype(int)
    position_change = position_unit.diff().fillna(position_unit)

    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)
    result["position"] = (position_unit * TRADE_SIZE).astype(int)

    warmup_rows = min(SLOW_WINDOW - 1, len(result))
    if warmup_rows > 0:
        warmup_index = result.index[:warmup_rows]
        result.loc[warmup_index, "signal"] = 0
        result.loc[warmup_index, "position"] = 0

    return result


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "Close": list(range(100, 180)) + list(range(180, 120, -1)),
        }
    )
    checked = gen_position(sample)
    print(checked[["Close", "ma_fast", "ma_slow", "signal", "position"]].tail())
