# Quy Trình Trọn Vẹn: Model Training -> Deploy NCNN

Chào mừng bạn đến với Data Pipeline cho xe tự hành nhặt vật! Đây là tài liệu hướng dẫn nhanh các bước để tự huấn luyện mạng Neural Network (YOLO11) nhận diện vật thể của riêng bạn.

## Các Công Đoạn Chính

### Bước 1: Thu thập Dữ Liệu
1. Bạn đưa script `data-collection/collect_data.py` lên Raspberry Pi.
2. Cho xe chạy vài vòng, mở script. Cứ `0.5s` nó sẽ lưu 1 tấm ảnh với độ phân giải `320x240`. Hãy quăng các vật bạn muốn xe nhặt ra khắp nơi (có khi trong góc, có khi ngược sáng, có khi không có vật).
3. Copy toàn bộ ảnh trong thư mục `dataset/raw_images/` về máy tính (PC).

### Bước 2: Gán nhãn (Annotation) - Gợi ý dùng Roboflow
1. Tạo một tài khoản trên [Roboflow.com](https://app.roboflow.com/) hoặc tải phần mềm `CVAT`/`LabelImg`.
2. Tải toàn bộ `raw_images` lên.
3. Kéo hộp (Bounding Box) quanh từng vật thể, gán nhãn (ví dụ: `object_1`, `bong_do`, `lon_nuoc`).
4. Quan trọng: Lúc xuất (Export) dữ liệu, hãy chọn định dạng **YOLOv11** (hoặc v8 đều chung chuẩn `txt`). Không resize thêm vì ảnh ta thu đã là 320x240.

### Bước 3: Huấn Luyện (Training)
1. Tải file ZIP từ Roboflow về, xả nén vào mục `model-training/dataset/`.
2. Vào file `dataset.yaml`, trỏ đường dẫn tuyệt đối hoặc tương đối tới mục `train`, `val` vừa tải về. Đồng thời cập nhật `names: [...]` đúng với những gì bạn đã vẽ hộp.
3. Mở Terminal / CMD tại PC:
   ```bash
   pip install -r requirements.txt
   python train.py
   ```
4. Đợi vài tiếng (hoặc vài phút nếu bạn có Card rời RTX). Model sẽ nằm trong thư mục `runs/detect/pickup_automotive/weights/best.pt`.

### Bước 4: Export (Convert) & Đưa Lên Pi
1. Mở file `export.py`, sửa dòng `MODEL_PATH = "runs/detect/pickup_automotive/weights/best.pt"`.
2. Chạy:
   ```bash
   python export.py
   ```
3. Script sẽ chạy `ncnn` converter (C++ backend) để tối ưu mô hình xuống mức thấp nhất (`FP16`). Nó sẽ sinh ra một thư mục `best_ncnn_model` chứa các file `.bin`, `.param`.
4. Gửi nguyên thư mục đó sang Pi (bỏ vào `models/` trên code cũ). Sửa dòng `model_path` trong code của bạn.

> Xong! Giờ Pi 5 của bạn đã biết tự động nhận ra các vật đặc thù trên đường đua. Chúc may mắn.