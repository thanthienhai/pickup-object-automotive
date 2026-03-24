import cv2
from ultralytics import YOLO
import sys
import os
import time
from datetime import datetime


def run_inference():
    # --- CẤU HÌNH CAMERA & MODEL ---
    CAM_CONFIG = {
        "source": 0,  # ID Camera (0 thường là webcam mặc định hoặc /dev/video0 trên Pi)
        "width": 320,  # Độ phân giải chiều ngang
        "height": 240,  # Độ phân giải chiều dọc
        "fps_limit": 15,  # Giới hạn FPS đầu vào của Camera
    }

    # Cấu hình lưu ảnh
    SAVE_DIR = "output_frames"
    SAVE_INTERVAL = 1.0  # Lưu 1 frame mỗi giây (tính theo thời gian thực)

    # Load model NCNN (lưu ý đường dẫn tới folder ncnn exported)
    # Cần chắc chắn bạn đã export model sang định dạng ncnn trước khi chạy
    model_path = "./models/yolo11s_ncnn_model"
    # -------------------------------

    # Tạo thư mục lưu ảnh nếu chưa có
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        model = YOLO(model_path, task="detect")
    except Exception as e:
        print(f"Lỗi khi load model: {e}")
        print("Vui lòng đảm bảo bạn đã có file model ncnn tại đường dẫn trên.")
        sys.exit(1)

    # Mở camera. Trên Raspberry Pi (Linux), backend mặc định là V4L2 nên không cần CAP_DSHOW
    cap = cv2.VideoCapture(CAM_CONFIG["source"])

    if not cap.isOpened():
        print(
            f"Không thể mở được camera ID {CAM_CONFIG['source']}. Vui lòng kiểm tra lại kết nối Camera."
        )
        sys.exit(1)

    # Áp dụng các thông số kỹ thuật cho Camera từ CAM_CONFIG
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_CONFIG["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_CONFIG["height"])
    cap.set(cv2.CAP_PROP_FPS, CAM_CONFIG["fps_limit"])

    # Lọc person bằng cách tạo danh sách các class id từ 1 đến 79 (bỏ class 0)
    allowed_classes = list(range(1, 80))

    print(
        f"Bắt đầu Pi Headless Inference với Cam ID: {CAM_CONFIG['source']} ({CAM_CONFIG['width']}x{CAM_CONFIG['height']})"
    )
    print(
        f"Cấu hình lưu ảnh: 1 frame mỗi {SAVE_INTERVAL} giây vào thư mục '{SAVE_DIR}'"
    )
    print("Nhấn Ctrl+C để thoát chương trình.")

    last_save_time = time.time()

    try:
        while True:
            # Retry logic: Một số camera cần vài lần thử để grab frame thành công
            success = False
            frame = None
            for _ in range(5):
                success, frame = cap.read()
                if success:
                    break
                time.sleep(0.01)  # Đợi một chút nếu chưa lấy được frame

            if not success:
                print("Đã mất kết nối hoặc không thể lấy frame từ camera.")
                break

            # Chạy dự đoán (predict) trên frame hiện tại
            results = model.predict(
                source=frame,
                imgsz=320,
                classes=allowed_classes,  # Bỏ qua person (class 0)
                vid_stride=2,  # Bỏ qua luân phiên khung hình
                verbose=False,  # Tắt log để terminal dễ nhìn hơn
            )

            # Trích xuất tốc độ xử lý (Inference Time)
            infer_time_ms = results[0].speed["inference"]
            fps = 1000.0 / infer_time_ms if infer_time_ms > 0 else 0

            # In ra Console để dễ theo dõi
            print(
                f"ID:{CAM_CONFIG['source']} | Infer: {infer_time_ms:.1f}ms | FPS: {fps:.1f}"
            )

            # Xử lý lưu ảnh định kỳ
            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                # Vẽ kết quả lên hình để lưu
                annotated_frame = results[0].plot()

                # Ghi thông số lên ảnh
                cv2.putText(
                    annotated_frame,
                    f"ID:{CAM_CONFIG['source']} | Res:{CAM_CONFIG['width']}x{CAM_CONFIG['height']} | Infer:{infer_time_ms:.1f}ms",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

                # Tạo tên file có timestamp
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SAVE_DIR, f"frame_{timestamp_str}.jpg")

                cv2.imwrite(filename, annotated_frame)
                print(f"[INFO] Đã lưu ảnh kiểm tra: {filename}")

                last_save_time = current_time

    except KeyboardInterrupt:
        print("\nNhận tín hiệu dừng chương trình (Ctrl+C). Đang dọn dẹp tài nguyên...")

    finally:
        # Dọn dẹp tài nguyên
        cap.release()
        print("Đã đóng kết nối camera. Thoát chương trình.")


if __name__ == "__main__":
    run_inference()
