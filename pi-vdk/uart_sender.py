import cv2
from ultralytics import YOLO
import sys
import os
import time
import serial
from datetime import datetime

# --- CẤU HÌNH HỆ THỐNG ---
CAM_CONFIG = {
    "source": 0,  # ID Camera
    "width": 320,
    "height": 240,
    "fps_limit": 15,
}

# Cấu hình UART (Kết nối Pi với Vi điều khiển)
UART_CONFIG = {
    "port": "/dev/ttyUSB0",  # Sửa lại nếu dùng chân GPIO (vd: /dev/serial0)
    "baudrate": 115200,
    "timeout": 1,
}

SAVE_DIR = "output_frames"
SAVE_INTERVAL = 1.0
model_path = "./models/yolo11n_ncnn_model"
# -------------------------


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

    allowed_classes = list(range(1, 80))  # Bỏ qua person (id=0)

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
                imgsz=320,
                classes=allowed_classes,
                vid_stride=2,
                verbose=False,
            )

            infer_time_ms = results[0].speed["inference"]
            fps = 1000.0 / infer_time_ms if infer_time_ms > 0 else 0

            # --- XỬ LÝ KẾT QUẢ DETECTION ĐỂ GỬI UART ---
            boxes = results[0].boxes
            best_obj = None
            max_y = -1

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

                # Gửi telemetry với obj tìm được
                if best_obj:
                    c_id, x_c, y_m, ar = best_obj
                    sent_packet = send_telemetry(ser, 1, c_id, x_c, y_m, ar)

                    print(
                        f"FPS: {fps:.1f} | [UART SENT] {sent_packet.strip() if sent_packet else 'No Serial'}"
                    )
            else:
                # Không thấy vật -> Gửi Heartbeat
                send_telemetry(ser, 0, 0, 0, 0, 0)
                print(f"FPS: {fps:.1f} | [UART SENT] Heartbeat: $0,0,0,0,0#")
            # -------------------------------------------

            # Lưu ảnh kiểm tra
            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                annotated_frame = results[0].plot()

                # Vẽ thông tin UART lên ảnh
                uart_text = f"UART: {sent_packet.strip() if best_obj and 'sent_packet' in locals() and sent_packet else '$0,0,0,0,0#'}"
                cv2.putText(
                    annotated_frame,
                    uart_text,
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
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
        print("[INFO] Thoát chương trình.")


if __name__ == "__main__":
    run_inference_and_telemetry()
