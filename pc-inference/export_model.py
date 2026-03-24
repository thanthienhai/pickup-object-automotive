from ultralytics import YOLO
import sys
import os

def export_model_optimized():
    """
    Xuất mô hình YOLO11 sang định dạng NCNN tối ưu cho CPU (Raspberry Pi 5 / PC CPU).
    Mọi cấu hình được fix cứng trong code để đạt hiệu năng inference nhanh nhất.
    """
    
    # --- CẤU HÌNH EXPORT (Chỉnh sửa tại đây) ---
    CONFIG = {
        "model_pt": "models/yolo11s.pt",   # File weight gốc đặt trong thư mục models
        "imgsz": 640,                      # Kích thước ảnh (640 cho độ chi tiết tốt nhất)
        "half_precision": True,     # FP16 giúp tăng tốc độ trên ARM (Pi 5)
        "int8": False               # Tắt int8 vì NCNN ổn định nhất với FP16
    }
    # ------------------------------------------

    try:
        # 1. Kiểm tra sự tồn tại của file weight
        if not os.path.exists(CONFIG["model_pt"]):
            print(f"--- Đang tải mô hình mặc định {CONFIG['model_pt']} ---")

        # 2. Khởi tạo model
        print(f"--- BẮT ĐẦU QUÁ TRÌNH EXPORT ---")
        print(f"Target Model: {CONFIG['model_pt']}")
        model = YOLO(CONFIG["model_pt"])
        
        # 3. Thực hiện Export
        print(f"Cấu hình Export: imgsz={CONFIG['imgsz']}, half={CONFIG['half_precision']}")
        print("Quá trình chuyển đổi sang NCNN có thể mất vài phút...")
        
        # Lệnh export tối ưu
        exported_path = model.export(
            format="ncnn", 
            imgsz=CONFIG["imgsz"], 
            half=CONFIG["half_precision"],
            int8=CONFIG["int8"]
        )
        
        print("\n" + "="*50)
        print("[THÀNH CÔNG] Đã tạo xong mô hình NCNN.")
        print(f"VỊ TRÍ: {exported_path}")
        print("="*50)
        print("\nHƯỚNG DẪN KẾT NỐI:")
        print(f"Chép đường dẫn trên vào biến 'model_path' trong file run_model_base.py")
        print("="*50)
        
        return exported_path
        
    except Exception as e:
        print(f"\n[LỖI] Xuất mô hình thất bại: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    # Chạy trực tiếp, không cần truyền tham số (args)
    export_model_optimized()