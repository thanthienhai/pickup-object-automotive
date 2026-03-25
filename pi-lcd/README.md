# Hướng dẫn kết nối màn hình LCD I2C với Raspberry Pi

Màn hình LCD kèm module I2C (thường dùng chip PCF8574) sẽ có 4 chân. Dưới đây là sơ đồ kết nối 4 chân này với các chân (pins) trên board mạch Raspberry Pi.

## 1. Sơ đồ cắm dây (Wiring Diagram)

| Chân trên module I2C (LCD) | Chân trên Raspberry Pi (Physical Pin) | Chức năng |
| :--- | :--- | :--- |
| **GND** | **Pin 6** (hoặc 9, 14, 20, 25, 30, 34, 39) | Nối đất (Ground) |
| **VCC** | **Pin 2** (hoặc Pin 4) | Cấp nguồn 5V cho màn hình |
| **SDA** | **Pin 3** (GPIO 2) | Kênh truyền dữ liệu I2C |
| **SCL** | **Pin 5** (GPIO 3) | Kênh xung nhịp I2C (Clock) |

*(Lưu ý: Pin số 1 trên Raspberry Pi là chân vuông nằm ở góc có khe cắm thẻ nhớ hoặc góc ngoài cùng, hàng bên trong).*

## 2. Lưu ý quan trọng
1. **Tắt nguồn Raspberry Pi** trước khi cắm hoặc rút dây để tránh gây chập cháy hỏng mạch.
2. **Chỉnh độ tương phản:** Ở mặt sau của module I2C (gắn sau màn LCD) có một biến trở màu xanh dương (chiếc ốc nhỏ). Nếu bạn chạy code mà màn hình chỉ sáng đèn nền nhưng không hiện chữ, hãy dùng tua-vít vặn nhẹ biến trở này cho đến khi chữ hiện lên rõ nét.
3. **Mức điện áp:** Màn hình LCD thường cần nguồn 5V để hiển thị rõ ràng và sáng đèn nền, do đó ta cắm VCC vào chân 5V của Pi.

## 3. Cách chạy code
```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy file main
python main.py
```