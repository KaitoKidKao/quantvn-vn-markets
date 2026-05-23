# BÁO CÁO TỰ ĐÁNH GIÁ HIỆU SUẤT HỆ THỐNG ĐA CHIẾN LƯỢC (MULTI-STRATEGY EVALUATION)

* Học viên: [Họ và Tên của bạn]
* Dự án: QuantVN Entry Test
* Repository: https://github.com/KaitoKidKao/quantvn-vn-markets

---

## 1. Đặt vấn đề và Phương pháp nghiên cứu
Để hoàn thành bài test đầu vào và có được cái nhìn đa chiều nhất về thị trường chứng khoán Việt Nam, tôi đã không chỉ triển khai một chiến lược đơn lẻ mà chủ động thiết kế, lập trình và chạy thử nghiệm **5 chiến lược giao dịch định lượng khác nhau** (gồm cả trường phái Theo xu hướng - Trend Following và Đảo chiều xu hướng - Mean Reversion) nhằm so sánh, đối chiếu hiệu quả thực tế trên nền tảng QuantVN.

Dữ liệu backtest được chạy từ ngày **13-08-2018 đến 30-12-2022** trên sàn QuantVN.

---

## 2. Kết quả đối chiếu số liệu từ Platform

Dưới đây là bảng tổng hợp các chỉ số hiệu suất thực tế thu được từ Dashboard của 5 Bot sau khi chạy kiểm thử trên Platform:

| Hạng | Tên chiến lược | Lợi nhuận trung bình | Điểm Hiệu suất | Điểm Sáng tạo | Điểm Ổn định | Đặc tính chiến lược |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | **EMA_Trend** | **+137.09%** | **5.24** | **9.0** | **6.0** | Xu hướng trung hạn (Đường EMA 50) |
| **2** | **Trend (Following)** | **+116.06%** | **5.33** | **9.0** | **6.0** | Xu hướng dài hạn (SMA 100 + SMA 20) |
| **3** | **MA_Crossover** | **+110.22%** | *Đang xử lý* | *Đang xử lý* | *Đang xử lý* | Xu hướng trung hạn (MA 20 / MA 50) |
| **4** | **BreakOut** | **+98.76%** | **3.77** | **9.0** | **6.0** | Đột phá hộp Donchian 20 phiên |
| **5** | **RSI** | **-109.44%** | **0.00** | **9.0** | **6.0** | Đảo chiều ngắn hạn (RSI 14) |

---

## 3. Phân tích Chi tiết từng Chiến lược

### 3.1. Các chiến lược Theo xu hướng (EMA_Trend, Trend Following, MA_Crossover, BreakOut)
* **EMA_Trend (+137.09%)**: Đạt mức sinh lời cao nhất. Nhờ sử dụng trung bình lũy thừa (EMA 50), chiến lược phản ứng nhanh nhạy hơn với biến động giá, giúp vào lệnh sớm khi xu hướng tăng bắt đầu và thoát vị thế kịp thời khi thị trường đảo chiều đi xuống.
* **Trend Following (+116.06% - Điểm Hiệu suất: 5.33)**: Đạt điểm hiệu suất và độ ổn định tối ưu nhất. Việc kết hợp bộ lọc xu hướng dài hạn (SMA 100) giúp hệ thống chỉ thực hiện lệnh mua khi thị trường chung thực sự an toàn (Uptrend), loại bỏ được rất nhiều tín hiệu nhiễu ngắn hạn.
* **MA_Crossover (+110.22%)**: Hoạt động ổn định, bám trend tốt nhưng biên lợi nhuận thấp hơn EMA do SMA có độ trễ lớn hơn.
* **BreakOut (+98.76% - Điểm Hiệu suất: 3.77)**: Đón đầu được các sóng tăng bứt phá vượt đỉnh nhưng điểm hiệu suất thấp hơn do gặp phải các đợt bứt phá giả (False Breakout) trong các giai đoạn thị trường đi ngang.

### 3.2. Chiến lược Đảo chiều (RSI)
* **RSI (-109.44% - Điểm Hiệu suất: 0.00)**: Đây là chiến lược duy nhất bị thua lỗ nặng. RSI hoạt động theo nguyên lý mua khi quá bán (<30) và bán khi quá mua (>70). Khi gặp một cổ phiếu đang trong xu hướng giảm mạnh dài hạn (Downtrend), chỉ báo liên tục báo quá bán và kích hoạt lệnh mua bắt đáy ("bắt dao rơi"). Do giá không có nhịp hồi đáng kể, bot buộc phải gồng lỗ trong thời gian dài, dẫn đến cháy tài khoản giả lập.

---

## 4. Điểm mạnh và Điểm yếu tổng thể của hệ thống

### Điểm mạnh:
* Các chiến lược bám xu hướng (Trend Following) như EMA Trend hay SMA Crossover chứng tỏ mức độ tương thích rất cao với thị trường chứng khoán Việt Nam, nơi có các sóng tăng/giảm kéo dài rõ rệt (ví dụ sóng uptrend 2020-2021).
* Điểm số ổn định đạt tối đa `6.0` trên cả 4 bot xu hướng cho thấy tính hệ thống cao.

### Điểm yếu và rủi ro:
* Rủi ro lớn nhất của các chiến lược xu hướng là khi thị trường chung bước vào giai đoạn đi ngang tích lũy (Sideways). Lúc này, các tín hiệu mua/bán sẽ liên tục đảo chiều khiến tài khoản bị bào mòn nhanh chóng.
* Chiến lược RSI hoàn toàn bất lực trong downtrend nếu không được tích hợp bộ lọc xu hướng lớn đi kèm.

---

## 5. Hướng cải tiến đề xuất
Nếu có thêm thời gian phát triển chiến lược, tôi đề xuất các hướng tối ưu sau:
1. **Kết hợp Động lượng và Xu hướng:** Chỉ cho phép chiến lược RSI hoạt động mua khi xu hướng dài hạn (EMA 200) xác nhận đang là Uptrend.
2. **Quản trị rủi ro chủ động:** Thay vì đợi các đường MA cắt nhau hoặc RSI chạm 70 mới bán, cần thiết lập điểm Cắt lỗ (Stop Loss) và Chốt lời (Take Profit) động dựa trên độ biến động thực tế ATR (Average True Range).
3. **Quản lý vốn:** Tối ưu hóa khối lượng vào lệnh (Position Sizing) thay vì mua một khối lượng cố định, ví dụ nâng quy mô lệnh khi xu hướng mạnh và giảm quy mô lệnh khi thị trường biến động hẹp.
