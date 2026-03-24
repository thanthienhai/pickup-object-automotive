# Hướng dẫn thiết lập chạy tự động script thu thập dữ liệu trên Raspberry Pi

Tài liệu này hướng dẫn cách cấu hình `systemd` (systemctl) để script `collect_data.py` tự động chạy ngầm mỗi khi khởi động Raspberry Pi (cắm nguồn).

## Bước 1: Tạo file service cho systemd

Mở terminal trên Raspberry Pi và dùng trình soạn thảo `nano` để tạo một file service mới tên là `collect_data.service` nằm trong thư mục `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/collect_data.service
```

## Bước 2: Thêm nội dung cấu hình vào file

Đưa đoạn cấu hình sau vào file vừa mở.

**Lưu ý quan trọng trước khi Copy/Paste:** 
- Thay đổi `[USER]` mặc định của Pi (thường là `pi` hoặc tên bạn đã tạo).
- Thay đường dẫn `/home/[USER]/pickup-object-automotive/` thành đường dẫn thực tế chứa project của bạn.

```ini
[Unit]
Description=Chay script thu thap du lieu collect_data.py
After=network.target

[Service]
# Thư mục gốc chứa mã nguồn (Thay đổi đường dẫn này cho đúng với Pi của bạn)
WorkingDirectory=/home/pi/pickup-object-automotive/data-collection/

# Tên người dùng sẽ thực thi script (thường là pi)
User=pi

# Lệnh để chạy script. 
# CHÚ Ý: Nếu có dùng môi trường ảo venv, hãy thay /usr/bin/python3 bằng đường dẫn thực tế của /venv/bin/python
ExecStart=/usr/bin/python3 /home/pi/pickup-object-automotive/data-collection/collect_data.py

# Tự động khởi động lại nếu script bị dừng đột ngột (lỗi hoặc do tiến trình khác tắt)
Restart=always
RestartSec=5

# Đẩy các dòng lệnh print() và báo lỗi của script ra syslog (xem log bằng lệnh journalctl)
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=collect_data_script

[Install]
WantedBy=multi-user.target
```

Sau khi dán nội dung vào `nano`, lưu lại và thoát bằng cách bấm:
1. `Ctrl + O`
2. `Enter`
3. `Ctrl + X`

## Bước 3: Áp dụng cấu hình và kích hoạt service tự động chạy

Bạn cần thông báo cho systemd biết về file service mới và bật nó lên chạy tự động. Lần lượt thi hành các lệnh sau:

1. **Reload lại cấu hình của systemd để nạp file mới:**
   ```bash
   sudo systemctl daemon-reload
   ```

2. **Kích hoạt (Enable) service để ứng dụng tự chạy mỗi khi Pi khởi động:**
   ```bash
   sudo systemctl enable collect_data.service
   ```

3. **Khởi động (Start) script ngay lập tức vào lúc này (mà không cần khởi động lại máy):**
   ```bash
   sudo systemctl start collect_data.service
   ```

## Bước 4: Kiểm tra và theo dõi log

### Kiểm tra script có đang chạy không:
Bạn có thể xem trạng thái hiện tại của service bằng lệnh:
```bash
sudo systemctl status collect_data.service
```
- Nếu hiển thị `active (running)`, script đã chạy trên luồng ngầm thành công.
- Nếu báo `failed` hoặc không thấy chạy, bạn sẽ cần xem log để biết nguyên nhân lỗi.

### Xem log console và lỗi trong quá trình chạy:
Bất cứ lệnh `print()` nào bên trong file `collect_data.py` hoặc log lỗi văng ra sẽ được ghi vào system log. Dùng dòng lệnh này để theo dõi:
```bash
# -f: Follow log liên tục như tail
sudo journalctl -u collect_data.service -f
```

---

*Lưu ý: Nếu script `collect_data.py` sử dụng `cv2.imshow` thì việc chạy nền từ `systemd` khi chưa nạp được GUI sẽ gây lỗi, bạn chỉ có thể chạy background nếu đã loại bỏ code show cửa sổ (chỉ đọc hình/lưu hình).*
