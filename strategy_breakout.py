from __future__ import annotations

import numpy as np
import pandas as pd


BREAKOUT_WINDOW = 20
TRADE_SIZE = 100


def _close_column(df: pd.DataFrame) -> str:
    """Return the price column used by QuantVN stock data."""
    for column in ("Close", "close"):
        if column in df.columns:
            return column
    raise KeyError("Input DataFrame must contain a 'Close' or 'close' column.")


def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo tín hiệu giao dịch và xác định vị thế cổ phiếu dựa trên chiến lược Breakout (Donchian Channel).

    Tham số:
        df: DataFrame chứa dữ liệu lịch sử cổ phiếu (yêu cầu có cột 'Close' hoặc 'close').

    Các cột output được tạo thêm:
        high_max: Mức giá cao nhất trong N phiên gần nhất (Kháng cự).
        low_min: Mức giá thấp nhất trong N phiên gần nhất (Hỗ trợ).
        signal: Tín hiệu giao dịch bứt phá:
            1  = Tín hiệu Mua (Giá đóng cửa bứt phá lên trên kháng cự high_max)
            -1 = Tín hiệu Bán (Giá đóng cửa thủng dưới hỗ trợ low_min)
            0  = Giữ nguyên vị thế hiện tại
        position: Vị thế mục tiêu (Số lượng cổ phiếu nắm giữ: TRADE_SIZE khi đang giữ vị thế mua, 0 khi đứng ngoài).
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    # 1. Tính toán giá cao nhất và thấp nhất của N phiên trước đó (lùi 1 phiên để tránh look-ahead bias)
    result["high_max"] = close.shift(1).rolling(window=BREAKOUT_WINDOW).max()
    result["low_min"] = close.shift(1).rolling(window=BREAKOUT_WINDOW).min()

    # 2. Xác định vị thế mục tiêu (position)
    position_signal = pd.Series(index=result.index, dtype=float)
    position_signal.loc[close > result["high_max"]] = 1.0
    position_signal.loc[close < result["low_min"]] = 0.0

    # Giữ nguyên vị thế trong khoảng tích lũy (không có breakout mới)
    position_signal = position_signal.ffill().fillna(0.0).astype(int)

    # Vị thế thực tế (số lượng cổ phiếu nắm giữ)
    result["position"] = (position_signal * TRADE_SIZE).astype(int)

    # 3. Tạo tín hiệu giao dịch (signal) dựa trên sự thay đổi vị thế
    position_change = position_signal.diff().fillna(position_signal)
    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)

    # 4. Loại bỏ tín hiệu trong giai đoạn khởi động (warmup period)
    warmup_rows = min(BREAKOUT_WINDOW, len(result))
    if warmup_rows > 0:
        warmup_index = result.index[:warmup_rows]
        result.loc[warmup_index, "signal"] = 0
        result.loc[warmup_index, "position"] = 0

    return result


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "Close": list(range(100, 115)) + list(range(115, 95, -1)) + list(range(95, 125)),
        }
    )
    checked = gen_position(sample)
    print(checked[["Close", "high_max", "low_min", "signal", "position"]].tail(15))
