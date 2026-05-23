from __future__ import annotations

import numpy as np
import pandas as pd


RSI_WINDOW = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
TRADE_SIZE = 100


def _close_column(df: pd.DataFrame) -> str:
    """Return the price column used by QuantVN stock data."""
    for column in ("Close", "close"):
        if column in df.columns:
            return column
    raise KeyError("Input DataFrame must contain a 'Close' or 'close' column.")


def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """Tạo tín hiệu giao dịch và xác định vị thế cổ phiếu dựa trên chiến lược RSI (Relative Strength Index).

    Tham số:
        df: DataFrame chứa dữ liệu lịch sử cổ phiếu (yêu cầu có cột 'Close' hoặc 'close').

    Các cột output được tạo thêm:
        rsi: Chỉ số sức mạnh tương đối RSI (14 phiên).
        signal: Tín hiệu giao dịch đảo chiều:
            1  = Tín hiệu Mua (RSI giảm xuống dưới ngưỡng quá bán 30)
            -1 = Tín hiệu Bán (RSI vượt lên trên ngưỡng quá mua 70)
            0  = Không hành động / Giữ nguyên vị thế hiện tại
        position: Vị thế mục tiêu (Số lượng cổ phiếu nắm giữ: TRADE_SIZE khi đang giữ vị thế mua, 0 khi đứng ngoài).
    """
    result = df.copy()
    close_col = _close_column(result)
    close = pd.to_numeric(result[close_col], errors="coerce")

    # 1. Tính toán động lượng tăng/giảm của giá
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Tính toán trung bình tăng và trung bình giảm (Wilder's smoothing hoặc Simple Moving Average)
    avg_gain = gain.rolling(window=RSI_WINDOW, min_periods=RSI_WINDOW).mean()
    avg_loss = loss.rolling(window=RSI_WINDOW, min_periods=RSI_WINDOW).mean()

    # Tính toán chỉ số RSI tránh lỗi chia cho 0
    rs = np.where(avg_loss != 0, avg_gain / avg_loss, np.nan)
    rsi = np.where(avg_loss == 0, np.where(avg_gain == 0, 50.0, 100.0), 100.0 - (100.0 / (1.0 + rs)))
    result["rsi"] = pd.Series(rsi, index=result.index)

    # 2. Xác định vị thế mục tiêu (position)
    # Mua (nắm giữ cổ phiếu) khi RSI đi vào vùng quá bán (< 30)
    # Bán (thoát vị thế, về 0) khi RSI đi vào vùng quá mua (> 70)
    position_signal = pd.Series(index=result.index, dtype=float)
    position_signal.loc[result["rsi"] < RSI_OVERSOLD] = 1.0
    position_signal.loc[result["rsi"] > RSI_OVERBOUGHT] = 0.0

    # Đối với các giai đoạn trung gian (30 đến 70), giữ nguyên vị thế trước đó
    # Giai đoạn đầu chu kỳ (trước khi có tín hiệu đầu tiên) mặc định là 0
    position_signal = position_signal.ffill().fillna(0.0).astype(int)

    # Vị thế thực tế (số lượng cổ phiếu nắm giữ)
    result["position"] = (position_signal * TRADE_SIZE).astype(int)

    # 3. Tạo tín hiệu giao dịch (signal) dựa trên sự thay đổi vị thế
    # signal = 1: Bắt đầu mua (vị thế từ 0 tăng lên 100)
    # signal = -1: Bắt đầu bán (vị thế từ 100 giảm xuống 0)
    # signal = 0: Không đổi
    position_change = position_signal.diff().fillna(position_signal)
    result["signal"] = np.select(
        [position_change > 0, position_change < 0],
        [1, -1],
        default=0,
    ).astype(int)

    # 4. Loại bỏ tín hiệu trong giai đoạn khởi động (warmup period) của RSI
    warmup_rows = min(RSI_WINDOW, len(result))
    if warmup_rows > 0:
        warmup_index = result.index[:warmup_rows]
        result.loc[warmup_index, "signal"] = 0
        result.loc[warmup_index, "position"] = 0

    return result


if __name__ == "__main__":
    # Tạo chuỗi giá mẫu để kiểm thử logic
    extended_close = list(range(100, 80, -2)) + list(range(80, 120, 2))
    sample = pd.DataFrame({"Close": extended_close})
    checked = gen_position(sample)
    print(checked[["Close", "rsi", "signal", "position"]].tail(15))
