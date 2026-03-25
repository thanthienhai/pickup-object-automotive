import smbus2
from RPLCD.i2c import CharLCD
from time import sleep

# Khởi tạo LCD
# Địa chỉ I2C thường là 0x27 hoặc 0x3f
# Cổng I2C thường là 1 trên Raspberry Pi
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)

    # Xóa màn hình
    lcd.clear()

    # Dòng chữ muốn chạy ngang
    # Lưu ý: LCD thông thường (như 1602/2004) dùng chip điều khiển HD44780
    # không có sẵn bộ font Tiếng Việt có dấu. Nếu in "Tôi là" sẽ ra ký tự lạ. 
    # Để hiển thị chuẩn xác nhất, ta dùng chữ không dấu:
    text = "Toi la ras pi 5"
    
    # Tạo sẵn các "khung hình" (frames) để làm hiệu ứng cuộn mượt mà
    frames = []
    
    # Giai đoạn 1: Chữ từ từ xuất hiện ở cạnh trái (kéo dài chữ ra)
    for i in range(1, len(text)):
        frame = text[:i].ljust(16, ' ')
        frames.append(frame)
        
    # Giai đoạn 2: Chữ trôi dần sang bên phải màn hình rồi biến mất ở cạnh phải
    for i in range(0, 16 + 1):
        frame = (" " * i + text)[:16].ljust(16, ' ')
        frames.append(frame)

    print("Đang chạy chữ ngang trên màn hình LCD...")
    print("Bấm tổ hợp phím Ctrl + C để dừng chương trình.")
    
    # Vòng lặp cuộn chữ liên tục không ngừng
    while True:
        for frame in frames:
            lcd.cursor_pos = (0, 0) # Đặt con trỏ ở Dòng 1, Cột 1
            lcd.write_string(frame)
            sleep(0.3) # Chỉnh số này để làm chữ chạy nhanh hay chậm (Ví dụ: 0.1 là rất nhanh)

except KeyboardInterrupt:
    # Xử lý khi người dùng ấn Ctrl + C để thoát
    print("\nĐã dừng chương trình an toàn!")
    lcd.clear()
    lcd.close(clear=True)
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")
    print("Vui lòng kiểm tra lại địa chỉ I2C (thường là 0x27 hoặc 0x3f) và kết nối dây.")
