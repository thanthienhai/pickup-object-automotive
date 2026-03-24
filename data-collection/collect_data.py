import cv2
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
CAMERA_ID = 0  # Thay đổi nếu Pi có nhiều camera (0, 1)
FRAME_WIDTH = 320  # GIỮ NGUYÊN - khớp với lúc inference
FRAME_HEIGHT = 240  # GIỮ NGUYÊN - khớp với lúc inference
FPS_LIMIT = 15

SAVE_INTERVAL = 0.5  # Cứ 0.5s chụp 1 tấm (2 FPS thu thập)
MAX_IMAGES = 1000  # Giới hạn an toàn, tránh tràn thẻ nhớ
OUTPUT_DIR = "dataset/raw_images"
# ---------------------


def init_camera():
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        print(f"[LỖI] Không thể kết nối tới camera ID: {CAMERA_ID}")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS_LIMIT)
    return cap


def main():
    print(f"--- BẮT ĐẦU THU THẬP DỮ LIỆU TỰ ĐỘNG ---")
    print(
        f"Cấu hình: {FRAME_WIDTH}x{FRAME_HEIGHT}, interval: {SAVE_INTERVAL}s, Max: {MAX_IMAGES} ảnh."
    )

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    cap = init_camera()
    if cap is None:
        return

    img_count = 0
    last_save_time = time.time()

    try:
        while img_count < MAX_IMAGES:
            # Retry mechanism
            success = False
            for _ in range(5):
                success, frame = cap.read()
                if success:
                    break
                time.sleep(0.01)

            if not success:
                print("[LỖI] Mất kết nối camera giữa chừng.")
                break

            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                # Cấu trúc tên: frame_20260324_153022_123.jpg
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
                filename = os.path.join(OUTPUT_DIR, f"frame_{timestamp}.jpg")

                cv2.imwrite(filename, frame)
                img_count += 1
                last_save_time = current_time

                print(f"[{img_count}/{MAX_IMAGES}] Đã lưu: {filename}")

        if img_count >= MAX_IMAGES:
            print(
                f"\n[INFO] Đã đạt giới hạn chụp {MAX_IMAGES} ảnh. Dừng thu thập để bảo vệ bộ nhớ."
            )

    except KeyboardInterrupt:
        print("\n[INFO] Người dùng bấm Ctrl+C. Dừng chương trình an toàn.")

    finally:
        cap.release()
        print(f"[HOÀN TẤT] Tổng số ảnh thu thập được: {img_count}")


if __name__ == "__main__":
    main()
