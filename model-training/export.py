from ultralytics import YOLO


def main():
    # Đường dẫn đến model tốt nhất của bạn sau khi chạy train.py
    # Bạn sẽ thay thế bằng "runs/detect/pickup_automotive/weights/best.pt"
    # Dùng yolo11n.pt mặc định để test nếu bạn chưa train xong
    MODEL_PATH = "yolo11n.pt"

    print(f"Đang tải model từ: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)

    print("Tiến hành Export model sang NCNN...")

    # Export cực kỳ quan trọng cho Raspberry Pi
    # Khuyến khích: imgsz 320 và sử dụng half=True để chuyển weights sang FP16
    # (giảm 1/2 kích thước model, tăng tốc trên CPU ARM)
    success = model.export(format="ncnn", imgsz=320, half=True, optimize=False)

    if success:
        print("\n--- XUẤT NCNN THÀNH CÔNG ---")
        print("Một folder đuôi '_ncnn_model' đã được tạo ra cạnh file gốc của bạn.")
        print(
            "Bạn chỉ cần copy nguyên folder đó sang Raspberry Pi (bỏ vào /models/) là xong!"
        )
    else:
        print("\n--- LỖI XUẤT FILE ---")


if __name__ == "__main__":
    main()
