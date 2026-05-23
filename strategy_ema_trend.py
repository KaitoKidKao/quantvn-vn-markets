from __future__ import annotations

import numpy as np
import pandas as pd


EMA_WINDOW = 50
TRADE_SIZE = 100


def _close_column(df: pd.DataFrame) -> str:
    """Return the price column used by QuantVN stock data."""
    for column in ("Close", "close"):
        if column in df.columns:
            return column
    raise KeyError("Input DataFrame must contain a 'Close' or 'close' column.")


def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo tín hiệu giao dịch và xác định vị thế cổ phiếu dựa trên chiến lược EMA Trend.

    Tham số:
        df: DataFrame chứa dữ liệu lịch sử cổ phiếu (yêu cầu có cột 'Close' hoặc 'close').

    Các cột output được tạo thêm:
        ema: Đường trung bình động lũy thừa (mặc định 50 phiên).
        signal: Tín hiệu giao dịch theo xu hướng:
            1  = Tín hiệu Mua (Giá đóng cửa cắt lên trên đường EMA)
            -1 = Tín hiệu Bán (Giá đóng cửa cắt xuống dưới đường EMA)
            0  = Giữ nguyên vị thế hiện tại
        position: Vị thế mục tiêu (Số lượng cổ phiếu nắm giữ: TRADE_SIZE khi giá trên EMA, 0 khi giá dưới EMA).
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    # 1. Tính toán đường EMA
    result["ema"] = close.ewm(span=EMA_WINDOW, adjust=False).mean()

    # Xác định các điểm dữ liệu sau giai đoạn warmup
    ready = result.index >= (EMA_WINDOW - 1)
    
    # Xu hướng tăng khi giá lớn hơn EMA
    long_regime = (close > result["ema"]) & ready

    # Vị thế mục tiêu: 1 (nắm giữ), 0 (đứng ngoài)
    position_unit = long_regime.astype(int)
    
    # Xác định sự thay đổi vị thế để tạo tín hiệu mua/bán
    position_change = position_unit.diff().fillna(position_unit)

    # 2. Tạo tín hiệu giao dịch (signal)
    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)
    
    # Vị thế thực tế (số lượng cổ phiếu nắm giữ)
    result["position"] = (position_unit * TRADE_SIZE).astype(int)

    # 3. Loại bỏ tín hiệu trong giai đoạn khởi động (warmup period)
    warmup_rows = min(EMA_WINDOW - 1, len(result))
    if warmup_rows > 0:
        warmup_index = result.index[:warmup_rows]
        result.loc[warmup_index, "signal"] = 0
        result.loc[warmup_index, "position"] = 0

    return result


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "Close": list(range(100, 150)) + list(range(150, 90, -1)),
        }
    )
    checked = gen_position(sample)
    print(checked[["Close", "ema", "signal", "position"]].tail(10))
