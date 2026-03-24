import cv2
import numpy as np
import os
from ultralytics import YOLO


def extract_objects_from_folder(
    input_dir="input", output_dir="output", model_path="yolo11x.pt", conf_thresh=0.25
):
    # Tạo output dir nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading Detection model: {model_path} ...")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Failed to load YOLO model: {e}")
        return

    # Lấy danh sách ảnh
    image_files = [
        f
        for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    if not image_files:
        print(f"No images found in '{input_dir}' directory.")
        return

    print(f"Found {len(image_files)} images. Starting extraction...")

    total_images_processed = 0
    total_objects_extracted = 0

    for filename in image_files:
        filepath = os.path.join(input_dir, filename)

        # Đọc ảnh BGR bằng OpenCV
        img = cv2.imread(filepath)
        if img is None:
            print(f"Warning: Could not read image {filename}. Skipping.")
            continue

        orig_h, orig_w = img.shape[:2]

        # Chạy inference
        results = model.predict(source=img, conf=conf_thresh, verbose=False)
        result = results[0]

        # Kiểm tra xem có object nào không
        if result.boxes is None or len(result.boxes) == 0:
            print(f"[{filename}] No objects found.")
            total_images_processed += 1
            continue

        # Lấy boxes
        boxes = (
            result.boxes.xyxy.cpu().numpy()
        )  # shape: (N, 4) [xmin, ymin, xmax, ymax]

        # Tách tên file gốc để làm prefix cho output
        base_name = os.path.splitext(filename)[0]

        for i, box in enumerate(boxes):
            # Cắt gọn (crop) ảnh theo bounding box
            x1, y1, x2, y2 = map(int, box)

            # Đảm bảo box nằm trong viền ảnh
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(orig_w, x2)
            y2 = min(orig_h, y2)

            cropped_obj = img[y1:y2, x1:x2]

            # Bỏ qua nếu crop bị rỗng (box lỗi)
            if cropped_obj.size == 0:
                continue

            # Lưu ảnh thành PNG (chỉ crop vuông vắn, không tách nền trong suốt)
            output_filename = f"{base_name}_obj_{i}.png"
            output_path = os.path.join(output_dir, output_filename)

            cv2.imwrite(output_path, cropped_obj)
            total_objects_extracted += 1

        print(f"[{filename}] Extracted {len(boxes)} objects.")
        total_images_processed += 1

    # In báo cáo tổng kết
    print("\n--- EXTRACTION COMPLETE ---")
    print(f"Total Images Processed: {total_images_processed}")
    print(f"Total Objects Extracted: {total_objects_extracted}")
    print(f"Output Directory: {output_dir}")


if __name__ == "__main__":
    # Đảm bảo thư mục tồn tại khi chạy độc lập
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    print("Please place images in 'input/' folder and run this script.")
    extract_objects_from_folder()
