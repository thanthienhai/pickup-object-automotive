import serial

# Cấu hình cổng COM bạn tìm thấy (vd: COM7)
port = "COM7" 
baudrate = 115200

try:
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"--- Đang lắng nghe trên {port} @ {baudrate} ---")
    
    while True:
        if ser.in_waiting > 0:
            # Đọc một dòng dữ liệu kết thúc bằng \n
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[NHẬN ĐƯỢC]: {line}")
                
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
