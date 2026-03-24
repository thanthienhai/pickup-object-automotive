# Giao thức Giao tiếp UART: Raspberry Pi 5 & Vi điều khiển (Xe Dò Line Nhặt Vật)

Tài liệu này mô tả chi tiết phương pháp và cấu trúc gói tin (packet) để truyền dữ liệu nhận diện vật thể từ Raspberry Pi 5 sang Vi điều khiển (VĐK - ví dụ: Arduino, STM32, ESP32) thông qua giao tiếp UART.

---

## 1. Tổng quan Kiến trúc Hệ thống

Với yêu cầu xe dò line nhặt vật nhưng **Pi chỉ lo việc nhận diện vật**, chúng ta có sự phân công nhiệm vụ rõ ràng:

*   **Vi điều khiển (VĐK):** Đảm nhiệm việc đọc cảm biến dò line (mắt hồng ngoại/quang trở), điều khiển module động cơ để xe bám line và điều khiển cơ cấu gắp vật (servo/tay gắp).
*   **Raspberry Pi 5:** Chạy model AI liên tục qua Camera góc nhìn thẳng về phía trước. Khi phát hiện vật thể nằm trên đường đi, Pi sẽ gửi tọa độ và thông tin vật thể xuống VĐK.
*   **Giao tiếp:** Cáp USB Serial hoặc chân TX/RX (UART) với Baudrate chuẩn (ví dụ: `115200`).

---

## 2. Vi điều khiển cần những dữ liệu gì từ Pi?

Vì Pi dùng camera đặt phía trước xe, VĐK không nhìn thấy vật mà hoàn toàn "mù" cho đến khi Pi báo. VĐK cần biết:

1.  **Có vật hay không?** (Trạng thái: 0 hoặc 1).
2.  **Vật gì?** (Class ID: Phân loại để biết nên gắp, nên đẩy đi hay nên né).
3.  **Vật có nằm chính giữa xe (trên line) không?** (Tọa độ X trung tâm của vật). Nếu xe lệch line, vật sẽ nằm lệch sang hai bên màn hình.
4.  **Khi nào thì đóng tay gắp (khoảng cách)?** Vì dùng camera 2D, chúng ta không có cảm biến khoảng cách (như siêu âm). Thay vào đó, **Tọa độ Y của cạnh dưới bounding box (Y_MAX)** hoặc **Diện tích khung hình (Area)** là thước đo khoảng cách tốt nhất. 
    *   *Nguyên lý:* Khi xe chạy lại gần vật, vật sẽ trôi dần xuống dưới đáy khung hình camera (Y tăng dần) và to ra. Khi `Y_MAX` chạm một ngưỡng nhất định (ví dụ cạnh đáy màn hình), tức là vật đã vào đúng tầm gắp.

---

## 3. Cấu trúc Gói tin (Protocol Data Packet)

Để VĐK (đặc biệt là các dòng 8-bit như Arduino) dễ dàng phân tích cú pháp (parsing) mà không bị tốn tài nguyên hoặc treo bộ nhớ, ta sử dụng định dạng **ASCII chuỗi String có ký tự bắt đầu và kết thúc**.

**Định dạng đề xuất:**
```text
$<STATUS>,<CLASS_ID>,<X_CENTER>,<Y_MAX>,<AREA>#\n
```

### Chi tiết các trường dữ liệu:

| Ký tự / Trường | Kiểu dữ liệu | Mô tả chi tiết |
| :--- | :--- | :--- |
| `$` | Char | **Start Marker**: Ký tự báo hiệu bắt đầu gói tin. Giúp VĐK không đọc nhầm dữ liệu rác. |
| `STATUS` | Int (0/1) | **0**: Không thấy vật nào (Khung hình trống).<br>**1**: Đang thấy vật. |
| `CLASS_ID` | Int | ID của vật thể (theo file `.pt` / `ncnn` của YOLO). Ví dụ: 1 là bóng đỏ, 2 là lon nước. Nếu `STATUS = 0`, trường này mặc định là `0`. |
| `X_CENTER` | Int | Tọa độ X tâm của bounding box (pixel). Ví dụ khung hình 320x240, thì `160` là chính giữa. Giúp VĐK xác nhận vật đang nằm ngay trước mũi xe hay lệch sang bên. |
| `Y_MAX` | Int | Tọa độ Y của **cạnh dưới** bounding box (pixel). Đây là tham số **QUAN TRỌNG NHẤT** để VĐK ước lượng khoảng cách và quyết định thời điểm gắp. |
| `AREA` | Int | Diện tích bounding box (`Width * Height`). Dùng làm tham số phụ trợ xác nhận vật đã đủ to (đủ gần) chưa. |
| `#` | Char | **End Marker**: Ký tự kết thúc gói tin. |
| `\n` | Char | Ký tự xuống dòng (Newline), giúp lệnh đọc `Serial.readStringUntil('\n')` trên VĐK hoạt động mượt mà. |

### Ví dụ gói tin truyền qua UART:
*   **Không có vật:** `$0,0,0,0,0#\n` (Gửi liên tục để VĐK biết Pi vẫn đang sống).
*   **Có vật ở xa:** `$1,2,158,120,4500#\n` (Thấy vật class 2, nằm gần chính giữa X=158, Y=120 nằm ở nửa trên màn hình, diện tích nhỏ).
*   **Có vật ngay sát tay gắp:** `$1,2,162,235,18500#\n` (Vật vẫn là class 2, X=162 vẫn giữa, nhưng **Y_MAX = 235** gần chạm đáy khung hình 240, diện tích cực to -> **VĐK RA LỆNH GẮP NGAY**).

*(Lưu ý: Nếu có nhiều vật trong khung hình, Pi chỉ nên gửi thông tin của vật thể CÓ Y_MAX LỚN NHẤT, tức là vật đang nằm gần xe nhất).*

---

## 4. Logic Xử lý Gợi ý (State Machine)

### A. Phía Raspberry Pi (Python)
Trong vòng lặp inference của `run_model_pi.py`:
1. Quét danh sách các object detect được.
2. Tìm object có tọa độ `Y_MAX` (y_center + height/2) lớn nhất (vật gần nhất).
3. Định dạng chuỗi string: `packet = f"${status},{class_id},{int(x_center)},{int(y_max)},{int(area)}#\n"`
4. Gửi qua Serial: `ser.write(packet.encode('utf-8'))`

### B. Phía Vi điều khiển (C/C++ Arduino)
VĐK duy trì 2 luồng công việc chính trong vòng lặp `loop()`:

**Luồng 1: Chạy dò line bám vạch (Mặc định)**
* Đọc cảm biến hồng ngoại.
* Chạy PID điều khiển 2 bánh xe.

**Luồng 2: Đọc UART và Can thiệp điều khiển**
* Nếu nhận được `$1,...` (Có vật):
  * Kiểm tra `Y_MAX`.
  * Nếu `Y_MAX > THRESHOLD_SLOW_DOWN` (Ví dụ > 180): Xe giảm tốc độ chạy line lại để tránh tông văng vật.
  * Nếu `Y_MAX > THRESHOLD_PICK_UP` (Ví dụ > 220):
    * Ghi đè luồng 1: **Dừng động cơ**.
    * Chạy hàm `Gắp_Vật()`.
    * Đưa vật vào khay.
    * Nhả luồng 1 để xe tiếp tục dò line đi tiếp.

---

## 5. Ưu điểm của phương pháp này
*   **Độc lập & Ổn định:** Pi giật lag hoặc rớt FPS cũng không làm xe chạy chệch line (vì VĐK tự lo dò line cứng).
*   **Không cần cảm biến siêu âm:** Tận dụng triệt để dữ liệu hình học (Bounding Box) của YOLO để tính toán thời điểm gắp chính xác đến từng milimet nếu được tuning (tinh chỉnh) góc nghiêng camera cẩn thận.
*   **Dễ debug:** Có thể cắm dây UART vào máy tính mở Serial Monitor là đọc ngay được data dưới dạng text con người hiểu được.