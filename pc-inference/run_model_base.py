import cv2
from ultralytics import YOLO
import sys
import serial
import time

# Cấu hình UART (Kết nối PC qua Serial/USB)
UART_CONFIG = {
    "port": "COM7",  # Cần sửa lại cho đúng cổng COM thực tế trên Windows
    "baudrate": 115200,
    "timeout": 1,
}

def send_telemetry(serial_conn, status, class_id=0, x_center=0, y_max=0, area=0):
    """
    Hàm định dạng và gửi gói tin ASCII: $<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\n
    """
    if serial_conn is None or not serial_conn.is_open:
        return False

    packet = f"${int(status)},{int(class_id)},{int(x_center)},{int(y_max)},{int(area)}#\n"
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
        print(f"[UART OK] Mở kết nối thành công tại: {UART_CONFIG['port']} @ {UART_CONFIG['baudrate']}")
        return ser
    except serial.SerialException as e:
        print(f"[UART WARNING] Không thể mở cổng Serial {UART_CONFIG['port']}.")
        print("[UART WARNING] Chương trình sẽ chạy inference mà không gửi dữ liệu.")
        return None

def run_inference():
    # --- CẤU HÌNH CAMERA & MODEL ---
    CAM_CONFIG = {
        "source": 0,           # ID Camera (0 cho webcam mặc định, 1 cho camera USB ngoài)
        "width": 640,          # Độ phân giải chiều ngang (Đã nâng lên 640)
        "height": 480,         # Độ phân giải chiều dọc (Đã nâng lên 480)
        "fps_limit": 15,       # Giới hạn FPS đầu vào của Camera
        "sim_pi_fps": 3        # Tốc độ giả lập Pi 5 khi chạy 640 (Giảm xuống ~3 FPS do nặng hơn)
    }
    
    # Load model. Thay bằng đường dẫn tới model NCNN hoặc .pt của bạn
    model_path = "models/yolo11n_ncnn_model" 
    # -------------------------------

    # Khởi tạo kết nối UART
    ser = init_serial()

    try:
        model = YOLO(model_path, task="detect")
    except Exception as e:
        print(f"Lỗi khi load model: {e}")
        print("Vui lòng đảm bảo bạn đã có file model tại đường dẫn trên.")
        sys.exit(1)

    # Mở camera USB với cấu hình ID từ CAM_CONFIG và dùng backend DSHOW để ổn định trên Windows
    cap = cv2.VideoCapture(CAM_CONFIG["source"], cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"Không thể mở được camera ID {CAM_CONFIG['source']}. Vùi lòng kiểm tra lại quyền truy cập Camera trên Windows.")
        sys.exit(1)
        
    # Áp dụng các thông số kỹ thuật cho Camera từ CAM_CONFIG
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_CONFIG["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_CONFIG["height"])
    cap.set(cv2.CAP_PROP_FPS, CAM_CONFIG["fps_limit"])

    # Trong COCO dataset (được train trên YOLO11n), con người (person) có id là 0.
    # Chúng ta lọc person bằng cách tạo danh sách các class id từ 1 đến 79 (bỏ class 0)
    allowed_classes = list(range(1, 80))

    print(f"Bắt đầu inference với Cam ID: {CAM_CONFIG['source']} ({CAM_CONFIG['width']}x{CAM_CONFIG['height']})")
    print(f"Sử dụng backend: CAP_DSHOW | Giả lập tốc độ tương đối Ras Pi: ~{CAM_CONFIG['sim_pi_fps']} FPS")
    print("Nhấn 'q' để thoát.")

    while True:
        loop_start_time = time.time()
        # Retry logic: Một số camera cần vài lần thử để grab frame thành công khi mới start
        success = False
        frame = None
        for _ in range(5):
            success, frame = cap.read()
            if success:
                break
            cv2.waitKey(10) # Đợi một chút nếu chưa lấy được frame
            
        if not success:
            print("Đã mất kết nối hoặc không thể lấy frame từ camera.")
            break
            
        # Chạy dự đoán (predict) trên frame hiện tại
        results = model.predict(
            source=frame,
            imgsz=640,
            classes=allowed_classes, # --> CHÌA KHÓA: Chỉ xử lý các đồ vật, bỏ qua person (class 0)
            vid_stride=2,            # Bỏ qua luân phiên khung hình
            verbose=False            # Tắt log để giao diện terminal dễ nhìn hơn
        )
        
        # Thêm thông tin tốc độ xử lý (Inference Time)
        infer_time_ms = results[0].speed['inference']
        fps = 1000.0 / infer_time_ms if infer_time_ms > 0 else 0

        # --- XỬ LÝ KẾT QUẢ DETECTION ĐỂ GỬI UART ---
        boxes = results[0].boxes
        best_obj = None
        max_y = -1
        sent_packet = False

        if len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0].item())
                width = x2 - x1
                height = y2 - y1
                x_center = x1 + width / 2
                y_max = y2
                area = width * height

                if y_max > max_y:
                    max_y = y_max
                    best_obj = (class_id, x_center, y_max, area)

            if best_obj:
                c_id, x_c, y_m, ar = best_obj
                sent_packet = send_telemetry(ser, 1, c_id, x_c, y_m, ar)
                print(f"ID:{CAM_CONFIG['source']} | FPS: {fps:.1f} | [UART SENT] {sent_packet.strip() if sent_packet else 'No Serial'}")
        else:
            sent_packet = send_telemetry(ser, 0, 0, 0, 0, 0)
            print(f"ID:{CAM_CONFIG['source']} | FPS: {fps:.1f} | [UART SENT] Heartbeat: $0,0,0,0,0#")

        # Trích xuất và vẽ kết quả lên tấm hình 
        annotated_frame = results[0].plot()
        
        # Ghi chữ lên góc trái phía trên của Video
        cv2.putText(
            annotated_frame, 
            f"ID:{CAM_CONFIG['source']} | Res:{CAM_CONFIG['width']}x{CAM_CONFIG['height']} | Infer:{infer_time_ms:.1f}ms", 
            (10, 20), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (0, 255, 0), 
            1
        )
        
        # Ghi thông tin UART lên hình ảnh
        uart_text = f"UART: {sent_packet.strip() if sent_packet else '$0,0,0,0,0#'}"
        cv2.putText(
            annotated_frame,
            uart_text,
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )
        
        # Hiển thị hình ảnh
        cv2.imshow("YOLO11n - Automotive Object Detection", annotated_frame)
        
        # Nhấn phím 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Thêm độ trễ để mô phỏng phần cứng vi xử lý Pi 5 (Giảm tải độ dội gói tin qua UART)
        loop_time = time.time() - loop_start_time
        target_loop_time = 1.0 / CAM_CONFIG["sim_pi_fps"]
        if loop_time < target_loop_time:
            time.sleep(target_loop_time - loop_time)

    # Dọn dẹp tài nguyên
    cap.release()
    cv2.destroyAllWindows()
    if ser and ser.is_open:
        ser.close()
        print("[UART] Đã đóng cổng Serial.")

if __name__ == '__main__':
    run_inference()
