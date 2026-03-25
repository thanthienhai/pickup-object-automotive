from ultralytics import YOLO


def main():
    # 1. Khởi tạo model từ trọng số Nano nhẹ nhất
    print("Khởi tạo yolo11s.pt model...")
    model = YOLO("yolo11s.pt")

    # 2. Bắt đầu training với file cấu hình yaml
    print("Bắt đầu huấn luyện...")
    results = model.train(
        data="output_dataset/dataset.yaml",  # Sửa đường dẫn vào đúng file dataset.yaml vừa tạo
        epochs=10,  # Số chu kỳ huấn luyện (thử 100 epoch trước)
        imgsz=640,  # Dataset mới sinh ra được fix cứng ở 640x480, nên imgsz=640 là lý tưởng nhất.
        batch=4,  # Giảm xuống 4 hoặc 2 nếu máy vẫn bị lỗi Out of Memory
        device="cpu",  # Thử '0' nếu có GPU, hoặc 'cpu' nếu máy không có card NVIDIA
        workers=2,  # Giảm số lượng luồng xử lý để tiết kiệm RAM
        name="pickup_automotive",  # Tên folder chứa kết quả train (trong thư mục runs/)
    )

    print(
        "Huấn luyện thành công! Model tốt nhất được lưu tại: runs/detect/pickup_automotive/weights/best.pt"
    )


if __name__ == "__main__":
    main()
