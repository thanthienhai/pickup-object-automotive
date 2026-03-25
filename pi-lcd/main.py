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

    # In ra màn hình
    lcd.write_string('Hello, Pi!\r\nI2C LCD Demo')

    print("Đang hiển thị trên màn hình LCD...")
    
    # Đợi 5 giây
    sleep(5)

    # Xóa màn hình trước khi thoát
    lcd.clear()
    lcd.close(clear=True)
    print("Đã hoàn thành!")

except Exception as e:
    print(f"Có lỗi xảy ra: {e}")
    print("Vui lòng kiểm tra lại địa chỉ I2C (thường là 0x27 hoặc 0x3f) và kết nối dây.")
