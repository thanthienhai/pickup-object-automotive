import cv2
from ultralytics import YOLO
import sys
import os
import time
import serial
from datetime import datetime

# Import thư viện LCD
try:
    from RPLCD.i2c import CharLCD
    lcd_available = True
except ImportError:
    lcd_available = False
    print("[WARNING] Không tìm thấy thư viện RPLCD. Màn hình LCD sẽ bị vô hiệu hóa.")

# --- CẤU HÌNH HỆ THỐNG ---
CAM_CONFIG = {
    "source": 0,  # ID Camera
    "width": 640,
    "height": 480,
    "fps_limit": 15,
}

# Cấu hình UART (Kết nối Pi với Vi điều khiển)
UART_CONFIG = {
    "port": "/dev/ttyUSB0",  # Sửa lại nếu dùng chân GPIO (vd: /dev/serial0)
    "baudrate": 9200,
    "timeout": 1,
}

SAVE_DIR = "output_frames"
SAVE_INTERVAL = 1.0
model_path = "./models/last_ncnn_model"
# -------------------------

# --- KHỞI TẠO LCD ---
lcd = None
if lcd_available:
    try:
        lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
        lcd.clear()
        lcd.write_string('He thong khoi dong...')
        time.sleep(1)
        lcd.clear()
        print("[LCD OK] Khởi tạo màn hình LCD thành công.")
    except Exception as e:
        print(f"[LCD ERROR] Lỗi khi khởi tạo màn hình: {e}")
        lcd = None

def update_lcd(line1, line2=""):
    """Cập nhật nội dung lên màn hình LCD"""
    if lcd is not None:
        try:
            # Rút gọn chuỗi nếu dài hơn 16 ký tự để tránh lỗi tràn màn hình
            line1_safe = line1[:16].ljust(16, ' ')
            line2_safe = line2[:16].ljust(16, ' ')
            
            lcd.cursor_pos = (0, 0)
            lcd.write_string(line1_safe)
            lcd.cursor_pos = (1, 0)
            lcd.write_string(line2_safe)
        except Exception as e:
            print(f"[LCD UPDATE ERROR]: {e}")
# --------------------


def send_telemetry(serial_conn, status, class_id=0, x_center=0, y_max=0, area=0):
    """
    Hàm định dạng và gửi gói tin ASCII: $<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\\n
    """
    if serial_conn is None or not serial_conn.is_open:
        return False

    packet = (
        f"${int(status)},{int(class_id)},{int(x_center)},{int(y_max)},{int(area)}#\n"
    )
    try:
        serial_conn.write(packet.encode("utf-8"))
        return packet
    except Exception as e:
        print(f"[UART ERROR] Lỗi khi gửi dữ liệu: {e}")
        return False


def init_serial():
    """Khởi tạo kết nối Serial an toàn"""
    try:
        ser = serial.Serial(
            UART_CONFIG["port"], UART_CONFIG["baudrate"], timeout=UART_CONFIG["timeout"]
        )
        print(
            f"[UART OK] Mở kết nối thành công tại: {UART_CONFIG['port']} @ {UART_CONFIG['baudrate']}"
        )
        return ser
    except serial.SerialException as e:
        print(f"[UART WARNING] Không thể mở cổng Serial {UART_CONFIG['port']}.")
        print("[UART WARNING] Chương trình sẽ chạy inference mà không gửi dữ liệu.")
        return None


def run_inference_and_telemetry():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # 1. Init UART
    ser = init_serial()

    # 2. Load Model
    try:
        model = YOLO(model_path, task="detect")
    except Exception as e:
        print(f"Lỗi khi load model: {e}")
        sys.exit(1)

    # 3. Mở Camera
    cap = cv2.VideoCapture(CAM_CONFIG["source"])
    if not cap.isOpened():
        print(f"Lỗi: Không mở được camera ID {CAM_CONFIG['source']}.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_CONFIG["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_CONFIG["height"])
    cap.set(cv2.CAP_PROP_FPS, CAM_CONFIG["fps_limit"])

    # Các nhãn cần nhận diện dựa trên mô hình mới
    allowed_classes = [0, 1, 2]

    # Mapping hiển thị tên tiếng Việt không dấu
    VIETNAMESE_NAMES = {
        0: "bong",
        1: "cam",
        2: "nut",
    }

    print(f"Bắt đầu Inference & Telemetry với Cam ID: {CAM_CONFIG['source']}")
    last_save_time = time.time()

    try:
        while True:
            success = False
            frame = None
            for _ in range(5):
                success, frame = cap.read()
                if success:
                    break
                time.sleep(0.01)

            if not success:
                print("Lỗi: Mất kết nối camera.")
                break

            results = model.predict(
                source=frame,
                imgsz=640,
                conf=0.3,
                classes=allowed_classes,
                vid_stride=2,
                verbose=False,
            )

            infer_time_ms = results[0].speed["inference"]
            fps = 1000.0 / infer_time_ms if infer_time_ms > 0 else 0

            # --- XỬ LÝ KẾT QUẢ DETECTION ĐỂ GỬI UART ---
            boxes = results[0].boxes
            best_obj = None
            best_box_coords = None # Biến lưu tọa độ box tốt nhất để vẽ
            max_y = -1
            sent_packet = ""  # Khởi tạo biến lưu bản tin UART gửi đi

            if len(boxes) > 0:
                # Tìm vật thể nằm ở vị trí Y thấp nhất trên màn hình (gần xe nhất)
                for box in boxes:
                    # Bounding box xyxy format: xmin, ymin, xmax, ymax
                    # Tâm x_center = xmin + width/2
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    class_id = int(box.cls[0].item())

                    width = x2 - x1
                    height = y2 - y1
                    x_center = x1 + width / 2
                    y_max = y2  # Cạnh dưới cùng của box = Y MAX
                    area = width * height

                    if y_max > max_y:
                        max_y = y_max
                        best_obj = (class_id, x_center, y_max, area)
                        best_box_coords = (x1, y1, x2, y2) # Lưu lại tọa độ

                # Gửi telemetry với obj tìm được
                if best_obj:
                    c_id, x_c, y_m, ar = best_obj
                    sent_packet = send_telemetry(ser, 1, c_id, x_c, y_m, ar)

                    if sent_packet:
                        print(f"FPS: {fps:.1f} | [UART SENT] {sent_packet.strip()}")
                    else:
                        # Ghi log tọa độ ra file nếu không có kết nối UART
                        log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NO_UART | FPS: {fps:.1f} | OBJ: {VIETNAMESE_NAMES.get(c_id, f'ID:{c_id}')} | Packet: $1,{c_id},{int(x_c)},{int(y_m)},{int(ar)}#"
                        print(log_line)
                        with open("telemetry_log.txt", "a") as f:
                            f.write(log_line + "\n")
                    
                    # Cập nhật thông tin lên LCD
                    # Sử dụng VIETNAMESE_NAMES để hiển thị tên tiếng Việt không dấu
                    class_name = VIETNAMESE_NAMES.get(c_id, f"ID:{c_id}")
                    # In ra Dòng 1: Vật - Dòng 2: Bản tin UART 
                    update_lcd(f"Vat: {class_name}", f"{sent_packet.strip() if sent_packet else 'NO UART'}")

            else:
                # Không thấy vật -> KHÔNG GỬI UART nữa (bỏ comment gửi heartbeat)
                # sent_packet = send_telemetry(ser, 0, 0, 0, 0, 0)
                sent_packet = ""
                print(f"FPS: {fps:.1f} | [UART] Không thấy vật, không gửi dữ liệu.")
                # Hiển thị trên màn hình là không thấy gì
                update_lcd("Trang thai:", "Khong co vat")
            # -------------------------------------------

            # Lưu ảnh kiểm tra
            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                annotated_frame = results[0].plot()

                # Vẽ viền xanh lá dày và chữ nổi bật cho vật thể đang được chọn gửi UART
                if best_box_coords:
                    bx1, by1, bx2, by2 = map(int, best_box_coords)
                    # Vẽ khung hình chữ nhật nổi bật (Màu xanh lá mạ - Xanh lục)
                    cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (0, 255, 0), 4)
                    
                    # Vẽ nhãn CHỌN
                    label_text = f"DANG CHON GUI UART: {class_name}"
                    (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(annotated_frame, (bx1, by1 - th - 10), (bx1 + tw, by1), (0, 255, 0), -1)
                    cv2.putText(annotated_frame, label_text, (bx1, by1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                # Vẽ thông tin UART lên ảnh (Dùng sent_packet đã lưu)
                uart_text = f"UART: {sent_packet.strip() if sent_packet else '$0,0,0,0,0#'}"
                cv2.putText(
                    annotated_frame,
                    uart_text,
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

                filename = os.path.join(
                    SAVE_DIR, f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )
                cv2.imwrite(filename, annotated_frame)
                last_save_time = current_time

    except KeyboardInterrupt:
        print("\n[INFO] Đã nhận tín hiệu dừng (Ctrl+C).")

    finally:
        cap.release()
        if ser and ser.is_open:
            ser.close()
            print("[UART] Đã đóng cổng Serial.")
            
        if lcd:
            lcd.clear()
            lcd.write_string('Tam biet!')
            time.sleep(1)
            lcd.clear()
            
        print("[INFO] Thoát chương trình.")


if __name__ == "__main__":
    run_inference_and_telemetry()
