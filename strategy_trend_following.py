from __future__ import annotations

import numpy as np
import pandas as pd


FILTER_WINDOW = 100
TRIGGER_WINDOW = 20
TRADE_SIZE = 100


def _close_column(df: pd.DataFrame) -> str:
    """Return the price column used by QuantVN stock data."""
    for column in ("Close", "close"):
        if column in df.columns:
            return column
    raise KeyError("Input DataFrame must contain a 'Close' or 'close' column.")


def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo tín hiệu giao dịch và xác định vị thế cổ phiếu dựa trên chiến lược Trend Following (Bộ lọc dài hạn + Kích hoạt ngắn hạn).

    Tham số:
        df: DataFrame chứa dữ liệu lịch sử cổ phiếu (yêu cầu có cột 'Close' hoặc 'close').

    Các cột output được tạo thêm:
        sma_long: Đường trung bình động dài hạn (mặc định 100 phiên) đóng vai trò làm Bộ lọc xu hướng (Trend Filter).
        sma_short: Đường trung bình động ngắn hạn (mặc định 20 phiên) đóng vai trò làm Điểm kích hoạt (Trigger).
        signal: Tín hiệu giao dịch theo xu hướng:
            1  = Tín hiệu Mua (Giá vượt trên SMA 20 khi đang ở xu hướng tăng dài hạn SMA 100)
            -1 = Tín hiệu Bán (Giá cắt xuống dưới SMA 20)
            0  = Giữ nguyên vị thế hiện tại
        position: Vị thế mục tiêu (Số lượng cổ phiếu nắm giữ: TRADE_SIZE khi đang giữ vị thế mua, 0 khi đứng ngoài).
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    # 1. Tính toán 2 đường SMA ngắn hạn và dài hạn
    result["sma_long"] = close.rolling(window=FILTER_WINDOW, min_periods=FILTER_WINDOW).mean()
    result["sma_short"] = close.rolling(window=TRIGGER_WINDOW, min_periods=TRIGGER_WINDOW).mean()

    # 2. Xác định vị thế mục tiêu (position)
    position_signal = pd.Series(index=result.index, dtype=float)
    # Mua: khi giá lớn hơn SMA ngắn hạn VÀ xu hướng dài hạn tăng (giá lớn hơn SMA dài hạn)
    position_signal.loc[(close > result["sma_short"]) & (close > result["sma_long"])] = 1.0
    # Bán: khi giá cắt xuống dưới SMA ngắn hạn
    position_signal.loc[close < result["sma_short"]] = 0.0

    # Giữ nguyên vị thế
    position_signal = position_signal.ffill().fillna(0.0).astype(int)

    # Vị thế thực tế
    result["position"] = (position_signal * TRADE_SIZE).astype(int)

    # 3. Tạo tín hiệu giao dịch (signal) dựa trên sự thay đổi vị thế
    position_change = position_signal.diff().fillna(position_signal)
    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)

    # 4. Loại bỏ tín hiệu trong giai đoạn khởi động (warmup period)
    warmup_rows = min(FILTER_WINDOW - 1, len(result))
    if warmup_rows > 0:
        warmup_index = result.index[:warmup_rows]
        result.loc[warmup_index, "signal"] = 0
        result.loc[warmup_index, "position"] = 0

    return result


if __name__ == "__main__":
    extended_close = list(range(100, 150)) + list(range(150, 90, -1)) + list(range(90, 160))
    sample = pd.DataFrame({"Close": extended_close})
    checked = gen_position(sample)
    print(checked[["Close", "sma_long", "sma_short", "signal", "position"]].tail(15))
