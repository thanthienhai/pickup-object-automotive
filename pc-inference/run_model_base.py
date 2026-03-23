import cv2
from ultralytics import YOLO
import sys

def run_inference():
    # --- CẤU HÌNH CAMERA & MODEL ---
    CAM_CONFIG = {
        "source": 1,           # ID Camera (0 cho webcam mặc định, 1 cho camera USB ngoài)
        "width": 320,          # Độ phân giải chiều ngang
        "height": 240,         # Độ phân giải chiều dọc
        "fps_limit": 15        # Giới hạn FPS đầu vào của Camera
    }
    
    # Load model. Thay bằng đường dẫn tới model NCNN hoặc .pt của bạn
    model_path = "models/yolo11n_ncnn_model" 
    # -------------------------------

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
    print("Sử dụng backend: CAP_DSHOW")
    print("Nhấn 'q' để thoát.")

    while True:
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
            imgsz=320,
            classes=allowed_classes, # --> CHÌA KHÓA: Chỉ xử lý các đồ vật, bỏ qua person (class 0)
            vid_stride=2,            # Bỏ qua luân phiên khung hình
            verbose=False            # Tắt log để giao diện terminal dễ nhìn hơn
        )
        
        # Trích xuất và vẽ kết quả lên tấm hình 
        annotated_frame = results[0].plot()
        
        # Thêm thông tin tốc độ xử lý (Inference Time)
        infer_time_ms = results[0].speed['inference']
        fps = 1000.0 / infer_time_ms if infer_time_ms > 0 else 0
        
        # In ra Console để dễ theo dõi
        print(f"ID:{CAM_CONFIG['source']} | Infer: {infer_time_ms:.1f}ms | FPS: {fps:.1f}")
        
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
        
        # Hiển thị hình ảnh
        cv2.imshow("YOLO11n - Automotive Object Detection", annotated_frame)
        
        # Nhấn phím 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Dọn dẹp tài nguyên
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_inference()
