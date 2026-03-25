## Context

Chúng ta có các thư mục chứa ảnh vật thể trong `create-data-v1/output/` (ví dụ: `bangdinh/`, `bong/`, `tenis/`). Mỗi thư mục đại diện cho một loại vật thể cần nhận diện. Chúng ta cần tạo một dataset YOLO tổng hợp (synthetic dataset) bằng cách dán các vật thể này lên nhiều loại background khác nhau với các kích cỡ đa dạng.

## Goals / Non-Goals

**Goals:**
- Đọc ảnh vật thể từ các thư mục con trong `output/` (ví dụ: `output/bong/`, `output/bangdinh/`, `output/tenis/`).
- Sử dụng **tên thư mục** làm nhãn (label) thay vì tên file.
- Duy trì dictionary mapping từ tên folder sang ID số nguyên (ví dụ: `{"bong": 0, "bangdinh": 1, "tenis": 2}`).
- Đọc ảnh nền (background) từ thư mục `backgrounds/`.
- Thay đổi kích cỡ vật thể ngẫu nhiên (scale) để tạo sự đa dạng.
- Dán một hoặc nhiều vật thể lên background tại vị trí (x, y) ngẫu nhiên.
- Tính toán tọa độ bounding box theo định dạng YOLO (normalized `x_center`, `y_center`, `width`, `height`).
- Xuất ảnh ra `dataset/images/train/` và labels ra `dataset/labels/train/`.

**Non-Goals:**
- Tạo scene 3D phức tạp. Đây là phương pháp đơn giản 2D overlay (dán hình chữ nhật lên hình chữ nhật).
- Augmentation phức tạp như lighting, blur (có thể handle bằng augmentation native của YOLO khi train).

## Decisions

- **Phương pháp ghép ảnh**: Sử dụng OpenCV và Numpy slicing để dán patch vật thể lên background. Vì ảnh vật thể là ảnh crop có bounding box nên sẽ giữ nguyên hình chữ nhật.
  - *Lý do*: Phương pháp "Cut-and-Paste" đơn giản, tính toán nhanh và hiệu quả cho việc train object detection. Model sẽ học features của vật thể bên trong hình chữ nhật.
- **Label Generation**: YOLO yêu cầu format `[class_id x_center y_center width height]`, normalized về `0.0 - 1.0`. Tính toán chính xác dựa trên tọa độ (x, y) và kích thước vật thể.
- **Scale ngẫu nhiên**: Mỗi vật thể sẽ được resize ngẫu nhiên với scale từ 0.2 đến 1.0 để tạo sự đa dạng kích cỡ.
- **Output Structure**: Script sẽ tạo thư mục `yolo_dataset` chứa `images` và `labels`, cùng với file `dataset.yaml` sẵn sàng cho training.

## Risks / Trade-offs

- **[Trade-off] Artifact từ bounding box**: Vì ảnh nguồn là hình chữ nhật (không phải shape transparent), ảnh generate sẽ trông như bị dán chồng lên nhau.
  - *Giải pháp*: CNN vẫn xử lý tốt vì model tập trung vào features bên trong rectangle. Training sẽ dùng heavy augmentation (Mosaic, MixUp, HSV shifting).
- **[Risk] Vật thể bị dán ra ngoài biên**: Nếu (x, y) quá gần mép, vật thể có thể bị cắt hoặc lỗi numpy slicing.
  - *Giải pháp*: Logic random (x, y) sẽ giới hạn `max_x = background_width - object_width`, tương tự cho y, đảm bảo vật thể nằm hoàn toàn trong khung hình.