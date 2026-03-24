from ultralytics import YOLO


def main():
    # 1. Khởi tạo model từ trọng số Nano nhẹ nhất
    print("Khởi tạo YOLO11n model...")
    model = YOLO("yolo11n.pt")

    # 2. Bắt đầu training với file cấu hình yaml
    print("Bắt đầu huấn luyện...")
    results = model.train(
        data="dataset.yaml",  # Đường dẫn tới file dataset của bạn
        epochs=100,  # Số chu kỳ huấn luyện (thử 100 epoch trước)
        imgsz=320,  # KIẾN QUYẾT phải là 320 để tương thích Pi lúc infer
        batch=16,  # Giảm nếu bị lỗi hết vRAM (Cuda Out of Memory)
        device="0",  # '0' nếu có GPU, hoặc 'cpu' nếu bạn train máy thường
        name="pickup_automotive",  # Tên folder chứa kết quả train (trong thư mục runs/)
    )

    print(
        "Huấn luyện thành công! Model tốt nhất được lưu tại: runs/detect/pickup_automotive/weights/best.pt"
    )


if __name__ == "__main__":
    main()
