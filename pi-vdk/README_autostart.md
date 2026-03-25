# Hướng dẫn thiết lập chạy tự động (Autostart) chương trình nhận diện và UART

Tài liệu này hướng dẫn cách cấu hình systemd (`systemctl`) trên Raspberry Pi để chương trình `uart_sender.py` có thể tự động chạy ngầm ngay khi máy tính Raspberry Pi được cấp điện khởi động.

---

## 1. Xác định đường dẫn môi trường và code

*Lưu ý: Bạn phải sửa đường dẫn dưới đây cho phù hợp nếu vị trí thư mục trên Raspberry Pi của bạn khác so với hướng dẫn.*

- **Thư mục chứa code (Working Directory):** `/home/pi/pickup-object-automotive/pi-vdk`
- **Đường dẫn tới môi trường Python ảo (venv):** `/home/pi/pickup-object-automotive/.venv/bin/python`
- **Đường dẫn file chạy chính:** `/home/pi/pickup-object-automotive/pi-vdk/uart_sender.py`

## 2. Tạo file cấu hình dịch vụ (Service file)

1. Mở terminal trên Raspberry Pi và chạy lệnh sau để tạo/sửa file service hệ thống bằng nano:
   ```bash
   sudo nano /etc/systemd/system/vdk_inference.service
   ```

2. Copy toàn bộ nội dung dưới đây và paste vào trong cửa sổ nano:

   ```ini
   [Unit]
   Description=YOLO Inference va Gui UART
   After=multi-user.target
   
   [Service]
   Type=simple
   User=pi
   # Thu muc lam viec cua chuong trinh
   WorkingDirectory=/home/pi/pickup-object-automotive/pi-vdk
   
   # Duong dan den Python nam trong moi truong ao (venv) va file script
   ExecStart=/home/pi/pickup-object-automotive/.venv/bin/python /home/pi/pickup-object-automotive/pi-vdk/uart_sender.py
   
   # Tu dong khoi dong lai neu chuong trinh bi vo tinh tat hoac gap loi
   Restart=always
   RestartSec=5
   
   # (Tuy chon) Cai dat cac bien moi truong he thong neu can
   # Environment=DISPLAY=:0
   
   [Install]
   WantedBy=multi-user.target
   ```

3. Bấm tổ hợp phím `Ctrl + X` (để thoát), sau đó bấm `Y` (đồng ý lưu file), rồi ấn phím `Enter`.

## 3. Kích hoạt và quản lý Service

Sau khi tạo xong file cấu hình, hãy chạy lần lượt các lệnh dưới đây trong Terminal:

**1. Tải lại cấu hình hệ thống:**
```bash
sudo systemctl daemon-reload
```

**2. Bật tính năng tự khởi động cùng hệ thống:**
```bash
sudo systemctl enable vdk_inference.service
```

**3. Khởi động chương trình ngay lập tức (không cần reset máy):**
```bash
sudo systemctl start vdk_inference.service
```

---

## 4. Các lệnh kiểm tra và sửa lỗi thường dùng

Vì chương trình chạy ngầm (không hiện Terminal trên màn hình), bạn sử dụng các lệnh sau để theo dõi tình trạng của nó.

- **Kiểm tra xem nó có đang chạy ổn định không:**
  ```bash
  sudo systemctl status vdk_inference.service
  ```
- **Đọc log/print của chương trình (Để xem có báo lỗi thiếu thư viện hay lỗi UART không):**
  ```bash
  journalctl -u vdk_inference.service -f
  ```
  *(Bấm `Ctrl + C` để thoát khỏi màn hình xem log).*
- **Dừng chương trình:**
  ```bash
  sudo systemctl stop vdk_inference.service
  ```
- **Tắt hẳn chức năng tự động khởi động:**
  ```bash
  sudo systemctl disable vdk_inference.service
  ```