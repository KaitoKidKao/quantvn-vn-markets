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
    """Tạo tín hiệu giao dịch và xác định vị thế cổ phiếu dựa trên chiến lược giao cắt MA (Moving Average Crossover).

    Tham số:
        df: DataFrame chứa dữ liệu lịch sử cổ phiếu (yêu cầu có cột 'Close' hoặc 'close').

    Các cột output được tạo thêm:
        ma_fast: Đường trung bình động nhanh (mặc định 20 phiên).
        ma_slow: Đường trung bình động chậm (mặc định 50 phiên).
        signal: Tín hiệu giao dịch giao cắt:
            1  = Tín hiệu Mua (Đường MA nhanh cắt lên trên đường MA chậm)
            -1 = Tín hiệu Bán (Đường MA nhanh cắt xuống dưới đường MA chậm)
            0  = Không hành động / Giữ nguyên vị thế hiện tại
        position: Vị thế mục tiêu (Số lượng cổ phiếu nắm giữ: TRADE_SIZE khi đang ở xu hướng tăng, 0 khi xu hướng giảm).
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    # 1. Tính toán hai đường trung bình động MA nhanh và MA chậm
    result["ma_fast"] = close.rolling(FAST_WINDOW, min_periods=FAST_WINDOW).mean()
    result["ma_slow"] = close.rolling(SLOW_WINDOW, min_periods=SLOW_WINDOW).mean()

    # Xác định các điểm dữ liệu hợp lệ (sau khi kết thúc chu kỳ khởi động của đường MA chậm)
    ready = result["ma_fast"].notna() & result["ma_slow"].notna()
    
    # Xu hướng tăng (long regime): MA nhanh lớn hơn MA chậm
    long_regime = (result["ma_fast"] > result["ma_slow"]) & ready

    # Vị thế mục tiêu: 1 (nắm giữ), 0 (đứng ngoài)
    position_unit = long_regime.astype(int)
    
    # Xác định sự thay đổi vị thế để tạo tín hiệu mua/bán tại điểm giao cắt
    position_change = position_unit.diff().fillna(position_unit)

    # 2. Tạo tín hiệu giao dịch (signal) dựa trên sự thay đổi vị thế
    # position_change > 0 -> Bắt đầu giữ cổ phiếu -> Mua (1)
    # position_change < 0 -> Bán hết cổ phiếu -> Bán (-1)
    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)
    
    # Vị thế thực tế (số lượng cổ phiếu nắm giữ)
    result["position"] = (position_unit * TRADE_SIZE).astype(int)

    # 3. Loại bỏ tín hiệu nhiễu trong giai đoạn khởi động (warmup period)
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
