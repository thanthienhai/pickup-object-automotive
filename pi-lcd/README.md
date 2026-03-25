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

## 3. Cách chạy code thủ công
```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Chạy file main
python main.py
```

## 4. Thiết lập chạy tự động khi khởi động Pi (Tự động chạy liên tục)
Để chương trình hiển thị LCD tự động chạy ngay khi bật Raspberry Pi, bạn có thể thiết lập như một dịch vụ nền (service) thông qua `systemd`.

**Bước 1:** Xác định thư mục lưu mã nguồn. Giả sử bạn lưu thư mục `pi-lcd` tại `/home/pi/pickup-object-automotive/pi-lcd`. Hãy lấy đường dẫn thư mục tuyệt đối bằng lệnh `pwd`.

**Bước 2:** Tạo một file cấu hình service cho hệ thống (yêu cầu quyền `sudo`):
```bash
sudo nano /etc/systemd/system/lcd_display.service
```

**Bước 3:** Dán nội dung dưới đây vào file `lcd_display.service`.
*(Lưu ý: nếu thư mục code của bạn không nằm ở `/home/pi/pickup-object-automotive/pi-lcd`, hãy sửa lại mục `WorkingDirectory` và `ExecStart` cho đúng với đường dẫn của bạn. Chữ `pi` trong dòng `User=pi` là tên người dùng của bạn trên Raspberry Pi).*

```ini
[Unit]
Description=Chay chu tren man hinh LCD I2C
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pickup-object-automotive/pi-lcd
ExecStart=/home/pi/pickup-object-automotive/.venv/bin/python /home/pi/pickup-object-automotive/pi-lcd/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Nhấn `Ctrl + X`, sau đó nhấn `Y` và `Enter` để lưu file.

**Bước 4:** Cập nhật lại hệ thống `systemd` để nhận diện dịch vụ mới:
```bash
sudo systemctl daemon-reload
```

**Bước 5:** Bật chế độ khởi động cùng hệ thống (Tự động chạy khi mở máy):
```bash
sudo systemctl enable lcd_display.service
```

**Bước 6:** Khởi động dịch vụ ngay bây giờ (Không cần khởi động lại máy):
```bash
sudo systemctl start lcd_display.service
```

### 🛠️ Các lệnh quản lý dịch vụ (Service):
- Kiểm tra xem chương trình LCD đang chạy ổn không, có báo lỗi gì không:
  ```bash
  sudo systemctl status lcd_display.service
  ```
- Dừng chương trình LCD:
  ```bash
  sudo systemctl stop lcd_display.service
  ```
- Tắt tính năng tự khởi động khi bật máy:
  ```bash
  sudo systemctl disable lcd_display.service
  ```
