from __future__ import annotations

import pandas as pd

# ==============================================================================
# HƯỚNG DẪN: Để chọn chiến lược cần chạy, hãy bỏ comment dòng import tương ứng.
# (Chỉ được phép bỏ comment một dòng import duy nhất).
# ==============================================================================

# Chiến lược 1: MA Crossover (Đường MA nhanh 20 giao cắt đường MA chậm 50) - KHUYẾN NGHỊ NỘP BÀI
from strategy_ma import gen_position

# Chiến lược 2: RSI (Relative Strength Index chu kỳ 14 phiên)
# from strategy_rsi import gen_position

# Chiến lược 3: EMA Trend (Đường EMA 50 phiên đóng vai trò đường xu hướng động)
# from strategy_ema_trend import gen_position

# Chiến lược 4: Breakout (Donchian Channel breakout 20 phiên)
# from strategy_breakout import gen_position

# Chiến lược 5: Trend Following (SMA 100 làm bộ lọc xu hướng dài hạn + SMA 20 làm điểm mua ngắn hạn)
# from strategy_trend_following import gen_position

# ==============================================================================
# Kiểm thử nhanh khi chạy trực tiếp tệp này
# ==============================================================================
if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "Close": list(range(100, 180)) + list(range(180, 120, -1)),
        }
    )
    checked = gen_position(sample)
    # Lấy các cột hiển thị tùy thuộc vào chiến lược đang hoạt động
    cols_to_print = [c for c in ["Close", "ma_fast", "ma_slow", "rsi", "ema", "high_max", "low_min", "sma_long", "sma_short", "signal", "position"] if c in checked.columns]
    print(f"Chiến lược đang hoạt động: {gen_position.__module__}")
    print(checked[cols_to_print].tail())
